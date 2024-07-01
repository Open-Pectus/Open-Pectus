import asyncio
import logging
from logging.handlers import QueueHandler
from queue import Empty, SimpleQueue
import time

from openpectus.protocol.engine_dispatcher import EngineDispatcherBase
import openpectus.protocol.engine_messages as EM
import openpectus.protocol.messages as M
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


class EngineReporter():
    def __init__(self, engine: Engine, dispatcher: EngineDispatcherBase) -> None:
        self.dispatcher = dispatcher
        self.engine = engine
        self._config_data_sent = False
        self.reconnect_message: EM.ReconnectedMsg | None = None

    def build_reconnected_message(self):
        """ Build the reconnect message to be sent just after reconnect. This should be called
        just when the connection is lost. """
        logger.info("Build message ReconnectedMsg")
        self.engine.notify_all_tags()
        tags = self.collect_tag_updates()
        run_id_tag = next((tag for tag in tags if tag.name == SystemTagName.RUN_ID), None)
        run_id = str(run_id_tag.value) if run_id_tag is not None else None
        # TODO collect run_started from somewhere
        # either add an event in engine containing this value - then take it from there
        # or - remove it from the message and have aggregator read it from recent engine 
        self.reconnect_message = EM.ReconnectedMsg(run_id=run_id, run_started_tick=time.time(), tags=tags)
        logger.debug(f"Collected {len(tags)} reconnect tags")

    def restart(self):
        logger.info("restart")
        self._config_data_sent = False

    async def send_reconnected_message(self):
        logger.info("reconnect")
        if self.reconnect_message is None:
            logger.error("No reconnect message built")
        else:
            await self.dispatcher.post_async(self.reconnect_message)
        self.restart()

    async def send_config_messages(self):
        """ Send configuration messages to aggregator. These are required when the connection is created or re-established.
        """
        logger.info("Sending initialization messages")
        valid_uod_info_sent = await self.send_uod_info()
        if valid_uod_info_sent:
            await self.notify_initial_tags()
            self._config_data_sent = True
            logger.info("Config messages sent")
        else:
            logger.error("Failed to send valid uod info. Connection to aggregator is not fully initialized.")

    async def send_data_messages(self):
        """ Send a batch of data messages to aggregator. """
        if not self._config_data_sent:
            await self.send_config_messages()
            return
        try:
            await self.send_tag_updates()
            await self.send_runlog()
            await self.send_control_state()
            await self.send_method_state()
            await self.send_error_log()
        except asyncio.CancelledError:
            logger.info("send_data_messages() was cancelled")  # , exc_info=True)
            return
        except Exception:
            logger.error("Unhandled exception in send_data_messages()", exc_info=True)
            raise

    async def notify_initial_tags(self):
        self.engine.notify_all_tags()
        await self.send_tag_updates()

    async def send_uod_info(self):
        readings: list[Mdl.ReadingInfo] = [
            reading.as_reading_info() for reading in self.engine.uod.readings
        ]
        msg = EM.UodInfoMsg(
            readings=readings,
            plot_configuration=self.engine.uod.plot_configuration,
            hardware_str=str(self.engine.uod.hwl))

        try:
            response = await self.dispatcher.post_async(msg)
            return not isinstance(response, M.ErrorMessage)
        except Exception:
            logger.error("Failed to send uod_info", exc_info=True)
            return False

    def collect_tag_updates(self) -> list[Mdl.TagValue]:
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

    async def send_tag_updates(self):
        tags = self.collect_tag_updates()
        if len(tags) > 0:
            msg = EM.TagsUpdatedMsg(tags=tags)
            await self.dispatcher.post_async(msg)

    async def send_runlog(self):
        tag_names: list[str] = []
        for reading in self.engine.uod.readings:
            tag_names.append(reading.tag_name)

        def filter_value(tag_value: TagValue) -> bool:
            return tag_value.name in tag_names

        def to_value(t: TagValue) -> Mdl.TagValue:
            assert t.tick_time is not None
            return Mdl.TagValue(name=t.name, value=t.value, value_unit=t.unit, tick_time=t.tick_time, direction=t.direction)

        def to_line(item: RunLogItem) -> Mdl.RunLogLine:
            # TODO what about state - try the client in test mode
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
        msg = EM.RunLogMsg(
            id=runlog.id,
            runlog=Mdl.RunLog(lines=list(map(to_line, runlog.items)))
        )
        await self.dispatcher.post_async(msg)

    async def send_error_log(self):
        log: Mdl.ErrorLog = Mdl.ErrorLog(entries=[])
        while not logging_queue.empty():
            log_entry = logging_queue.get_nowait()
            log.entries.append(Mdl.ErrorLogEntry(
                message=log_entry.getMessage(),
                created_time=log_entry.created,
                severity=log_entry.levelno))
        if len(log.entries) != 0:
            await self.dispatcher.post_async(EM.ErrorLogMsg(log=log))

    async def send_control_state(self):
        msg = EM.ControlStateMsg(control_state=Mdl.ControlState(
            is_running=self.engine._runstate_started,
            is_holding=self.engine._runstate_holding,
            is_paused=self.engine._runstate_paused
        ))
        await self.dispatcher.post_async(msg)

    async def send_method_state(self):
        state = self.engine.calculate_method_state()
        msg = EM.MethodStateMsg(method_state=state)
        await self.dispatcher.post_async(msg)
