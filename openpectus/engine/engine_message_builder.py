import logging
from logging.handlers import QueueHandler
from queue import Empty, SimpleQueue
import time

import openpectus.protocol.engine_messages as EM
import openpectus.protocol.models as Mdl
from openpectus.engine.engine import Engine
from openpectus.lang.exec.runlog import RunLogItem
from openpectus.lang.exec.tags import SystemTagName, TagValue
from openpectus.lang.exec.uod import logger as uod_logger
from openpectus.engine.engine import logger as engine_logger
from openpectus.engine.archiver import logger as archiver_logger

logger = logging.getLogger(__name__)

logging_queue: SimpleQueue[logging.LogRecord] = SimpleQueue()
logging_handler = QueueHandler(logging_queue)
logging_handler.setLevel(logging.WARN)

# add handler for selected loggers
uod_logger.addHandler(logging_handler)
engine_logger.addHandler(logging_handler)
archiver_logger.addHandler(logging_handler)

MAX_SIZE_TagsUpdatedMsg = 100
""" The maximum number of tags to include in a single TagsUpdatedMsg message """


class EngineMessageBuilder():
    """ Collects data from engine and constructs engine messages """
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def build_reconnected_message(self) -> EM.ReconnectedMsg:
        """ Build the reconnect message to be sent just after reconnect """
        logger.info("Build message ReconnectedMsg")
        tags = self.collect_tag_updates(snapshot=True)
        run_id_tag = next((tag for tag in tags if tag.name == SystemTagName.RUN_ID), None)
        run_id = str(run_id_tag.value) if run_id_tag is not None and run_id_tag.value is not None else None
        # TODO collect run_started from somewhere
        # either add an event in engine containing this value - then take it from there
        # or - remove it from the message and have aggregator read it from recent engine
        logger.debug(f"Collected {len(tags)} reconnect tags")

        return EM.ReconnectedMsg(
            run_id=run_id,
            run_started_tick=time.time(),
            tags=tags,
            method=Mdl.Method(lines=self.engine.method.get_code_lines())
        )

    def create_uod_info(self) -> EM.UodInfoMsg:
        readings: list[Mdl.ReadingInfo] = [
            reading.as_reading_info() for reading in self.engine.uod.readings
        ]
        return EM.UodInfoMsg(
            readings=readings,
            plot_configuration=self.engine.uod.plot_configuration,
            hardware_str=str(self.engine.uod.hwl))

    def collect_tag_updates(self, snapshot=False) -> list[Mdl.TagValue]:
        if snapshot:
            self.engine.notify_all_tags()
        tags = {}  # using dict to de-duplicate
        try:
            for _ in range(MAX_SIZE_TagsUpdatedMsg):
                tag = self.engine.tag_updates.get_nowait()
                assert tag.tick_time is not None, f'tick_time is None for tag {tag.name}'
                tags[tag.name] = Mdl.TagValue(
                    name=tag.name,
                    tick_time=tag.tick_time,
                    value=tag.get_value(),
                    value_unit=tag.unit,
                    direction=tag.direction)
                self.engine.tag_updates.task_done()
        except Empty:
            pass
        return [tag for tag in tags.values()]

    def create_tag_updates_snapshot_msg(self) -> EM.TagsUpdatedMsg:
        tags = self.collect_tag_updates(snapshot=True)
        return EM.TagsUpdatedMsg(tags=tags)

    def create_tag_updates_msg(self) -> EM.TagsUpdatedMsg | None:
        tags = self.collect_tag_updates()
        if len(tags) > 0:
            return EM.TagsUpdatedMsg(tags=tags)

    def create_runlog_msg(self) -> EM.RunLogMsg:
        tag_names: list[str] = []
        for reading in self.engine.uod.readings:
            tag_names.append(reading.tag_name)

        def filter_value(tag_value: TagValue) -> bool:
            return tag_value.name in tag_names

        def to_value(t: TagValue) -> Mdl.TagValue:
            assert t.tick_time is not None
            return Mdl.TagValue(name=t.name, value=t.value, value_unit=t.unit, tick_time=t.tick_time, direction=t.direction)

        def to_line(item: RunLogItem) -> Mdl.RunLogLine:
            msg = Mdl.RunLogLine(
                id=item.id,
                command_name=item.name,
                start=item.start,
                end=item.end,
                progress=item.progress,
                start_values=[to_value(t) for t in filter(filter_value, item.start_values)],
                end_values=[to_value(t) for t in filter(filter_value, item.end_values)]
            )
            return msg

        runlog = self.engine.runtimeinfo.get_runlog()
        return EM.RunLogMsg(
            id=runlog.id,
            runlog=Mdl.RunLog(lines=list(map(to_line, runlog.items)))
        )

    def create_error_log_msg(self) -> EM.ErrorLogMsg | None:
        log: Mdl.ErrorLog = Mdl.ErrorLog(entries=[])
        while not logging_queue.empty():
            log_entry = logging_queue.get_nowait()
            log.entries.append(Mdl.ErrorLogEntry(
                message=log_entry.getMessage(),
                created_time=log_entry.created,
                severity=log_entry.levelno))
        if len(log.entries) != 0:
            return EM.ErrorLogMsg(log=log)

    def create_control_state_msg(self) -> EM.ControlStateMsg:
        return EM.ControlStateMsg(control_state=Mdl.ControlState(
            is_running=self.engine._runstate_started,
            is_holding=self.engine._runstate_holding,
            is_paused=self.engine._runstate_paused
        ))

    def create_method_state_msg(self) -> EM.MethodStateMsg:
        state = self.engine.calculate_method_state()
        return EM.MethodStateMsg(method_state=state)
