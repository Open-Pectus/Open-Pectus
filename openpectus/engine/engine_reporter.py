import asyncio
import logging
import time
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

    async def stop(self):
        await self.dispatcher.disconnect()
        self.engine.stop()

    async def run_loop_async(self):
        try:
            init_succeeded = False
            while (not init_succeeded):
                init_succeeded = await self.send_uod_info_async()
                if init_succeeded: await self.notify_initial_tags_async()
                if not init_succeeded: time.sleep(10)

            while True:
                await asyncio.sleep(1)
                await self.send_tag_updates_async()
                await self.send_runlog_async()
                await self.send_control_state_async()
        except KeyboardInterrupt:
            await self.stop()
        except asyncio.CancelledError:
            return
        except Exception:
            logger.error("Unhandled exception in run_loop_async", exc_info=True)

    async def notify_initial_tags_async(self):
        self.engine.notify_initial_tags()
        await self.send_tag_updates_async()

    async def send_uod_info_async(self):
        readings: List[Mdl.ReadingInfo] = []
        for r in self.engine.uod.readings:
            tag_name = self.map_and_filter_tag_name(r.tag_name)
            if tag_name is not None:
                ri = Mdl.ReadingInfo(
                    label=r.label,
                    tag_name=tag_name,
                    valid_value_units=r.valid_value_units,
                    commands=[Mdl.ReadingCommand(name=c.name, command=c.command) for c in r.commands])
                readings.append(ri)

        msg = EM.UodInfoMsg(readings=readings)
        response = self.dispatcher.post(msg)
        return not isinstance(response, M.ErrorMessage)

    def map_and_filter_tag_name(self, tag_name: str):
        match tag_name:
            case SystemTagName.RUN_TIME:
                return Mdl.SystemTagName.run_time
            case SystemTagName.SYSTEM_STATE:
                return Mdl.SystemTagName.system_state
            case name if name in [tag.name for tag in SystemTagName]:
                return None
            case _:
                return tag_name

    async def send_tag_updates_async(self):
        tags = []
        try:
            for _ in range(100):
                tag = self.engine.tag_updates.get_nowait()
                tag_name = self.map_and_filter_tag_name(tag.name)
                if tag_name is not None:
                    tags.append(Mdl.TagValue(name=tag_name, value=tag.get_value(), value_unit=tag.unit))
        except Empty:
            pass
        if len(tags) > 0:
            msg = EM.TagsUpdatedMsg(tags=tags)
            self.dispatcher.post(msg)

    async def send_runlog_async(self):
        def to_value(t: TagValue) -> Mdl.TagValue:
            return Mdl.TagValue(name=t.name, value=t.value, value_unit=t.unit)

        def to_line(item: RunLogItem) -> Mdl.RunLogLine:
            # TODO what about state - try the client in test mode
            msg = Mdl.RunLogLine(
                id=item.id,
                command_name=item.name,
                start=item.start,
                end=item.end,
                progress=item.progress,
                start_values=[to_value(t) for t in item.start_values],
                end_values=[to_value(t) for t in item.end_values]
            )
            return msg

        runlog = self.engine.runtimeinfo.get_runlog()
        msg = EM.RunLogMsg(
            id=runlog.id,
            runlog=Mdl.RunLog(lines=list(map(to_line, runlog.items)))
        )
        self.dispatcher.post(msg)

    async def send_control_state_async(self):
        msg = EM.ControlStateMsg(control_state=Mdl.ControlState(
            is_running=self.engine._runstate_started,
            is_holding=self.engine._runstate_holding,
            is_paused=self.engine._runstate_paused
        ))
        self.dispatcher.post(msg)

    # async def get_method(self) -> M.MethodMsg | M.RpcErrorMessage:
    #     code = self.engine._pcode
    #     lines = code.splitlines(keepends=True)
    #
    #     proxy_logger.info(f"Returning method with {len(lines)} lines")
    #
    #     # TODO get line ids and status from interpreter
    #     return M.MethodMsg(
    #         lines=[M.MethodLineMsg(id="", content=line) for line in lines],
    #         started_line_ids=[],
    #         executed_line_ids=[],
    #         injected_line_ids=[])
