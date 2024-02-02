import asyncio
import logging
from queue import Empty
from typing import List

import openpectus.protocol.engine_messages as EM
import openpectus.protocol.messages as M
import openpectus.protocol.models as Mdl
from openpectus.engine.engine import Engine
from openpectus.lang.exec.runlog import RunLogItem
from openpectus.lang.exec.tags import SystemTagName, TagValue
from openpectus.protocol.engine_dispatcher import EngineDispatcher

logger = logging.getLogger(__name__)


class EngineReporter():
    def __init__(self, engine: Engine, dispatcher: EngineDispatcher) -> None:
        self.dispatcher = dispatcher
        self.engine = engine
        self.engine.run()

    async def stop_async(self):
        await self.dispatcher.disconnect_async()
        self.engine.stop()

    async def run_loop_async(self):
        try:
            init_succeeded = False
            while not init_succeeded:
                init_succeeded = self.send_uod_info()
                if init_succeeded:
                    self.notify_initial_tags()
                if not init_succeeded:
                    await asyncio.sleep(10)

            while True:
                await asyncio.sleep(1)
                self.send_tag_updates()
                self.send_runlog()
                self.send_control_state()
                self.send_method_state()
        except asyncio.CancelledError:
            return
        except Exception:
            logger.error("Unhandled exception in run_loop_async", exc_info=True)

    def notify_initial_tags(self):
        self.engine.notify_initial_tags()
        self.send_tag_updates()

    def send_uod_info(self):
        readings: List[Mdl.ReadingInfo] = []
        for reading in self.engine.uod.readings:
            tag_name = self.map_and_filter_tag_name(reading.tag_name)
            if tag_name is not None:
                reading_info = Mdl.ReadingInfo(
                    tag_name=str(tag_name),
                    valid_value_units=reading.valid_value_units,
                    commands=[Mdl.ReadingCommand(name=c.name, command=c.command) for c in reading.commands])
                readings.append(reading_info)

        msg = EM.UodInfoMsg(readings=readings, plot_configuration=self.engine.uod.plot_configuration, hardware_str=str(self.engine.uod.hwl))

        response = self.dispatcher.post(msg)
        return not isinstance(response, M.ErrorMessage)

    def map_and_filter_tag_name(self, tag_name: str):
        match tag_name:
            case SystemTagName.RUN_TIME:
                return Mdl.SystemTagName.run_time
            case SystemTagName.SYSTEM_STATE:
                return Mdl.SystemTagName.system_state
            case SystemTagName.RUN_ID:
                return Mdl.SystemTagName.run_id
            case name if name in [tag.value for tag in SystemTagName]:
                return None
            case _:
                return tag_name

    def send_tag_updates(self):
        tags = []
        try:
            for _ in range(100):
                tag = self.engine.tag_updates.get_nowait()
                tag_name = self.map_and_filter_tag_name(tag.name)
                if tag_name is not None:
                    assert tag.tick_time is not None, f'tick_time is None for tag {tag.name}'
                    tags.append(Mdl.TagValue(name=tag_name, tick_time=tag.tick_time, value=tag.get_value(), value_unit=tag.unit))
                self.engine.tag_updates.task_done()
        except Empty:
            pass
        if len(tags) > 0:
            msg = EM.TagsUpdatedMsg(tags=tags)
            self.dispatcher.post(msg)

    def send_runlog(self):
        tag_names: list[str] = []
        for reading in self.engine.uod.readings:
            tag_name = self.map_and_filter_tag_name(reading.tag_name)
            if tag_name is not None:
                tag_names.append(tag_name)

        def filter_value(tag_value: TagValue) -> bool:
            return tag_value.name in tag_names

        def to_value(t: TagValue) -> Mdl.TagValue:
            assert t.tick_time is not None
            return Mdl.TagValue(name=t.name, value=t.value, value_unit=t.unit, tick_time=t.tick_time)

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
        self.dispatcher.post(msg)

    def send_control_state(self):
        msg = EM.ControlStateMsg(control_state=Mdl.ControlState(
            is_running=self.engine._runstate_started,
            is_holding=self.engine._runstate_holding,
            is_paused=self.engine._runstate_paused
        ))
        self.dispatcher.post(msg)

    def send_method_state(self):
        state = self.engine.calculate_method_state()
        msg = EM.MethodStateMsg(method_state=state)
        self.dispatcher.post(msg)
