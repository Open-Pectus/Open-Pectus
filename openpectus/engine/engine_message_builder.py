import logging
from logging.handlers import QueueHandler
from queue import Empty, SimpleQueue
import time

import openpectus.protocol.engine_messages as EM
import openpectus.protocol.models as Mdl
from openpectus.engine.engine import Engine
from openpectus.lang.exec.runlog import RunLogItem
from openpectus.lang.exec.tags import TagValue
from openpectus.lang.exec.uod import logger as uod_logger
from openpectus.engine.engine import frontend_logger as engine_logger
from openpectus.engine.archiver import logger as archiver_logger
from openpectus.engine.internal_commands_impl import logger as internal_cmds_logger

logger = logging.getLogger(__name__)

frontend_logging_queue: SimpleQueue[logging.LogRecord] = SimpleQueue()
frontend_logging_handler = QueueHandler(frontend_logging_queue)
frontend_logging_handler.setLevel(logging.WARN)

# add frontend error logging for selected loggers (this gives import cycle warning - could we reverse this instead?)
uod_logger.addHandler(frontend_logging_handler)
engine_logger.addHandler(frontend_logging_handler)
archiver_logger.addHandler(frontend_logging_handler)
internal_cmds_logger.addHandler(frontend_logging_handler)

MAX_SIZE_TagsUpdatedMsg = 100
""" The maximum number of tags to include in a single TagsUpdatedMsg message """

def to_model_tag(tag: TagValue) -> Mdl.TagValue:
    if tag.tick_time == 0.0:
        logger.warning(f"Tick time was 0 for tag {tag.name}")
        tag.tick_time = time.time()
    return Mdl.TagValue(
        name=tag.name,
        tick_time=tag.tick_time,
        value=tag.value,
        value_formatted=tag.value_formatted,
        value_unit=tag.unit,
        direction=tag.direction,
        simulated=tag.simulated
    )

class EngineMessageBuilder():
    """ Collects data from engine and constructs engine messages """
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(engine={self.engine})'

    def create_uod_info(self) -> EM.UodInfoMsg:

        uod_definition = self.engine.uod.create_lsp_definition()
        uod_definition.system_commands = self.engine.get_command_definitions()

        return EM.UodInfoMsg(
            readings=[reading.as_reading_info() for reading in self.engine.uod.readings],
            commands=[command.as_command_info() for command in self.engine.uod.command_descriptions.values()],
            uod_definition=uod_definition,
            plot_configuration=self.engine.uod.plot_configuration,
            hardware_str=str(self.engine.uod.hwl),
            required_roles=self.engine.uod.required_roles,
            data_log_interval_seconds=self.engine.uod.data_log_interval_seconds)

    def collect_tag_updates(self, snapshot=False) -> list[Mdl.TagValue]:
        if snapshot:
            self.engine.notify_all_tags()
        tags: dict[str, Mdl.TagValue] = {}  # using dict to de-duplicate
        try:
            for _ in range(MAX_SIZE_TagsUpdatedMsg):
                tag_org = self.engine.tag_updates.get_nowait()
                tag = tag_org.as_readonly()
                tags[tag.name] = to_model_tag(tag)
                self.engine.tag_updates.task_done()
        except Empty:
            pass
        return [tag for tag in tags.values()]

    def create_tag_updates_snapshot_msg(self) -> EM.TagsUpdatedMsg:
        tags = self.collect_tag_updates(snapshot=True)
        return EM.TagsUpdatedMsg(tags=tags)

    def create_tag_updates_msg(self) -> EM.TagsUpdatedMsg | None:
        tags = self.collect_tag_updates()
        # print("tags with updates", str([t.name for t in tags]))
        if len(tags) > 0:
            return EM.TagsUpdatedMsg(tags=tags)

    def create_run_started_msg(self, run_id: str, tick_time: float) -> EM.RunStartedMsg:
        return EM.RunStartedMsg(run_id=run_id, started_tick=tick_time)

    def create_run_stopped_msg(self, run_id: str) -> EM.RunStoppedMsg:
        runlog_msg = self.create_runlog_msg(run_id)
        state = self.engine.method_manager.get_method_state()
        return EM.RunStoppedMsg(run_id=run_id, runlog=runlog_msg.runlog, method_state=state)

    def create_runlog_msg(self, run_id: str) -> EM.RunLogMsg:
        tag_names: list[str] = []
        for reading in self.engine.uod.readings:
            tag_names.append(reading.tag_name)

        def filter_value(tag_value: TagValue) -> bool:
            return tag_value.name in tag_names

        def to_line(item: RunLogItem) -> Mdl.RunLogLine:
            msg = Mdl.RunLogLine(
                id=item.id,
                command_name=item.name,
                start=item.start,
                end=item.end,
                progress=item.progress,
                start_values=[to_model_tag(t) for t in filter(filter_value, item.start_values)],
                end_values=[to_model_tag(t) for t in filter(filter_value, item.end_values)],
                forcible=item.forcible,
                cancellable=item.cancellable,
                forced=item.forced,
                cancelled=item.cancelled
            )
            return msg

        runlog = self.engine.runtimeinfo.get_runlog()
        return EM.RunLogMsg(
            id=runlog.id,
            run_id=run_id,
            runlog=Mdl.RunLog(lines=list(map(to_line, runlog.items)))
        )

    def create_error_log_msg(self) -> EM.ErrorLogMsg | None:
        log: Mdl.ErrorLog = Mdl.ErrorLog(entries=[])
        while not frontend_logging_queue.empty():
            log_entry = frontend_logging_queue.get_nowait()
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
        state = self.engine.method_manager.get_method_state()
        return EM.MethodStateMsg(method_state=state)
