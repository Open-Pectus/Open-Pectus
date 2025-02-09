import ctypes
from datetime import UTC, datetime
import os
import logging
import platform
import time
import csv
from typing import Callable

from openpectus.lang.exec.runlog import RunLog
from openpectus.lang.exec.tags import Tag, TagCollection

logger = logging.getLogger(__name__)

LOW_DISKSPACE_MB = 50
VERY_LOW_DISKSPACE_MB = 5

# file open defaults
encoding = 'utf-8'

# csv option defaults
delimiter = ','     # used in old system
# delimiter = ';'    # makes Excel 365 understand it out of the box
quoting = csv.QUOTE_NONE
escapechar = None
# Note:  The MarkTag value may include a separator char/string. Make sure that does not conflict with the options here.


def get_free_space_mb(dirname):
    """Return folder/drive free space (in megabytes)."""
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(  # type: ignore
            ctypes.c_wchar_p(dirname),
            None,
            None,
            ctypes.pointer(free_bytes))
        return free_bytes.value / 1024 / 1024
    else:
        st = os.statvfs(dirname)
        return st.f_bavail * st.f_frsize / 1024 / 1024


RunlogAccessor = Callable[[], RunLog]
TagsAccessor = Callable[[], TagCollection]


class ArchiverTag(Tag):
    def __init__(self,
                 runlog_accessor: RunlogAccessor,
                 tags_accessor: TagsAccessor,
                 data_log_interval_seconds: float) -> None:
        super().__init__("Archive filename")
        self.runlog_accessor = runlog_accessor
        self.tags_accessor = tags_accessor
        self.tags: TagCollection | None = None
        path = os.path.dirname(os.path.realpath(__file__))
        self.data_path = os.path.join(path, "data")
        self.last_save_tick: float = 0.0
        self.data_log_interval_seconds = data_log_interval_seconds
        self.file_path: str | None = None
        self.file_ready = False

        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
            logger.info("Created archive directory: " + self.data_path)

        self.check_diskspace()

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(data_path="{self.data_path}", ' +
                f'data_log_interval_seconds={self.data_log_interval_seconds}, last_save_tick={self.last_save_tick})')

    def archive(self) -> str | None:
        return None

    def check_diskspace(self) -> bool:
        diskspace_free = get_free_space_mb(self.data_path)
        if diskspace_free < VERY_LOW_DISKSPACE_MB:
            logger.error("Drive is VERY low on diskspace.")
            return False
        elif diskspace_free < LOW_DISKSPACE_MB:
            logger.warning("Drive is low on diskspace. Archiver may soon fill up the drive.")
        return True

    def prepare_tags_file(self):
        """ Create file and write header row"""
        assert self.file_path is not None
        assert self.tags is not None
        with open(self.file_path, 'xt', newline='', encoding=encoding) as f:
            writer = csv.writer(f, delimiter=delimiter, quoting=quoting, escapechar=escapechar)
            tag_values = [tag.archive() for tag in self.tags]
            writer.writerow(
                ['Datetime (UTC)',] +
                [f'{tag.name} [{tag.unit}]' if tag.unit is not None else tag.name
                 for tag, val in zip(self.tags, tag_values)
                 if val is not None]
            )
        self.file_ready = True

    def write_tags_row(self):
        assert self.tags is not None
        if self.file_ready:
            assert self.file_path is not None
            with open(self.file_path, 'at', newline='', encoding=encoding) as f:
                writer = csv.writer(f, delimiter=delimiter, quoting=quoting, escapechar=escapechar)
                tag_values = [tag.archive() for tag in self.tags]
                utc_now = datetime.now(UTC)
                row = [str(utc_now)] + [val for val in tag_values if val is not None]
                try:
                    writer.writerow(row)
                except Exception:
                    logger.error(f"Error writing row: {row}", exc_info=True)

    def write_runlog(self):
        date_part = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        runlog_file_path = os.path.join(self.data_path, "archiver-runlog-" + date_part + ".txt")

        logger.info(f"Writing runlog to {runlog_file_path}")
        with open(runlog_file_path, 'xt', newline='', encoding=encoding) as f:
            writer = csv.writer(f, delimiter=delimiter, quoting=quoting)
            writer.writerow(['Command', 'Start time (UTC)', 'Completed time (UTC)'])
            try:
                runlog = self.runlog_accessor()
            except Exception:
                logger.error("Failed to access the runlog", exc_info=True)
                return

            for x in runlog.items:
                start = datetime.fromtimestamp(x.start, UTC)
                end = datetime.fromtimestamp(x.end, UTC) if x.end is not None else ""
                writer.writerow([x.name, start, end])

    def on_start(self, run_id: str):
        self.tags = self.tags_accessor()
        tick_time = time.time()
        date_part = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = "archiver-" + date_part + ".txt"
        self.set_value(filename, tick_time)
        self.file_path = os.path.join(self.data_path, filename)
        if self.check_diskspace():
            logger.info("Archiver started using logfile " + self.file_path)
            self.prepare_tags_file()
        else:
            logger.error("Archiver will not run due to low diskspace")

    def on_tick(self, tick_time: float, increment_time: float):
        now = time.time()
        is_row_due = self.last_save_tick == 0 or self.last_save_tick + self.data_log_interval_seconds < now
        if is_row_due:
            self.write_tags_row()
            self.last_save_tick = now

    def on_stop(self):
        tick_time = time.time()
        logger.info("Stopped")
        self.set_value(None, tick_time)
        self.file_path = None
        self.file_ready = False
        self.write_runlog()
