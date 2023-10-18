import asyncio
import logging
import socket
from queue import Empty
from argparse import ArgumentParser
from typing import Any, List

import httpx

from openpectus import log_setup_colorlog
from openpectus.lang.exec.runlog import RunLogItem
from openpectus.protocol.engine import Client, create_client
from openpectus.engine.eng import EngineProxy, EngineProxyAdapter, ExecutionEngine
from openpectus.engine.hardware import RegisterDirection
from openpectus.lang.exec import tags
from openpectus.lang.exec.uod import UnitOperationDefinitionBase, UodBuilder, UodCommand
from openpectus.lang.exec import readings as R
import openpectus.protocol.messages as M


log_setup_colorlog()

logger = logging.getLogger("openpectus.protocol.engine")
logger.setLevel(logging.INFO)
logging.getLogger("openpectus.lang.exec.pinterpreter").setLevel(logging.INFO)
logging.getLogger("Engine").setLevel(logging.INFO)


def get_args():
    parser = ArgumentParser("Start Pectus Engine")
    parser.add_argument("-ah", "--aggregator_host", required=False, default="127.0.0.1",
                        help="Aggregator websocket host name. Default is 127.0.0.1")
    parser.add_argument("-ap", "--aggregator_port", required=False, default="9800",
                        help="Aggregator websocket port number. Default is 9800")
    parser.add_argument("-uod", "--uod", required=False, default="DemoUod", help="The UOD to use")
    parser.add_argument("-r", "--runner", required=False, default="WebSocketRPCEngineRunner",
                        choices=['WebSocketRPCEngineRunner', 'DemoEngineRunner'],
                        help="The event listener to use")
    return parser.parse_args()


def create_demo_uod() -> UnitOperationDefinitionBase:

    def reset(cmd: UodCommand, args: List[Any]) -> None:
        count = cmd.get_iteration_count()
        if count == 0:
            cmd.context.tags.get("Reset").set_value("Reset")
        elif count == 4:
            cmd.context.tags.get("Reset").set_value("N/A")
            cmd.set_complete()

    return (
        UodBuilder()
        .with_instrument("DemoUod")
        .with_no_hardware()
        .with_hardware_register("FT01", RegisterDirection.Both, path='Objects;2:System;2:FT01')
        .with_hardware_register("Reset", RegisterDirection.Both, path='Objects;2:System;2:RESET',
                                from_tag=lambda x: 1 if x == 'Reset' else 0,
                                to_tag=lambda x: "Reset" if x == 1 else "N/A")
        .with_new_system_tags()
        .with_tag(tags.Reading("FT01", "L/h"))
        .with_tag(tags.Select("Reset", value="N/A", unit=None, choices=['Reset', "N/A"]))
        .with_command(UodCommand.builder().with_name("Reset").with_exec_fn(reset))
        .with_process_value(R.Reading(label="Run Time"))
        .with_process_value(R.Reading(label="FT01"))
        .with_process_value(R.Reading(label="Reset"))
        .with_process_value(R.Reading(label="System State"))
        .build()
    )


class EngineRunner:
    def __init__(self, engine: ExecutionEngine) -> None:
        self.engine = engine

    async def connect_async(self):
        raise NotImplementedError()

    async def disconnect_async(self):
        raise NotImplementedError()

    async def register_async(self):
        raise NotImplementedError()

    async def notify_initial_tags_async(self):
        self.engine.notify_initial_tags()
        await self.send_tag_updates_async()

    async def send_uod_info_async(self):
        raise NotImplementedError()

    async def send_tag_updates_async(self):
        raise NotImplementedError()

    async def send_runlog_async(self):
        raise NotImplementedError()

    async def send_control_state_async(self):
        raise NotImplementedError()

    async def run_loop_async(self):
        try:
            await self.connect_async()
            await self.register_async()
            await self.send_uod_info_async()
            await self.notify_initial_tags_async()

            while True:
                await asyncio.sleep(1)
                await self.send_tag_updates_async()
                await self.send_runlog_async()
                await self.send_control_state_async()
        except KeyboardInterrupt:
            await self.disconnect_async()
        except asyncio.CancelledError:
            return
        except Exception:
            logger.error("Unhandled exception in run_loop_async", exc_info=True)


class WebSocketRPCEngineRunner(EngineRunner):
    def __init__(self, engine: ExecutionEngine, ws_url: str) -> None:
        self.engine = engine
        self.client: Client | None = None
        self.ws_url = ws_url

        self.engine.run()
        self.proxy: EngineProxy = EngineProxyAdapter(engine)

    async def connect_async(self):
        client = create_client()
        self.client = client
        await self.client.start_connect_wait_async(ws_url=self.ws_url)

    async def register_async(self):
        if self.client is None:
            raise ValueError("Client is not connected")

        register_engine_msg = M.RegisterEngineMsg(computer_name=socket.gethostname(), uod_name=self.engine.uod.instrument)
        register_response = await self.client.send_to_server(register_engine_msg)  # , on_success=on_register, on_error=on_error)
        if not isinstance(register_response, M.SuccessMessage):
            print("Failed to Register")
            return

        self.client.set_message_handler(M.InvokeCommandMsg, self._schedule_command)
        self.client.set_message_handler(M.InjectCodeMsg, self._inject_code)
        self.client.set_message_handler(M.MethodMsg, self.set_method)

    async def send_uod_info_async(self):
        if self.client is None:
            raise ValueError("Client is not connected")

        readings: List[M.ReadingInfo] = []
        for r in self.engine.uod.readings:
            ri = M.ReadingInfo(
                label=r.label,
                tag_name=r.tag_name,
                valid_value_units=r.valid_value_units,
                commands=[M.ReadingCommand(name=c.name, command=c.command) for c in r.commands])
            readings.append(ri)

        msg = M.UodInfoMsg(readings=readings)
        await self.client.send_to_server(msg)

    async def send_tag_updates_async(self):
        if self.client is None:
            raise ValueError("Client is not connected")

        tags = []
        try:
            for _ in range(100):
                tag = self.engine.tag_updates.get_nowait()
                tags.append(M.TagValueMsg(name=tag.name, value=tag.get_value(), value_unit=tag.unit))
        except Empty:
            pass
        if len(tags) > 0:
            msg = M.TagsUpdatedMsg(tags=tags)
            await self.client.send_to_server(msg)

    async def send_runlog_async(self):
        if self.client is None:
            raise ValueError("Client is not connected")

        def to_msg(item: RunLogItem) -> M.RunLogLineMsg:
            msg = M.RunLogLineMsg(
                id="",
                command_name=item.command_req.name,
                start=item.start,
                end=item.end,
                progress=None,
                start_values=[],
                end_values=[]
                )
            return msg

        items = self.engine.runlog.get_items()
        msg = M.RunLogMsg(
            id="",
            lines=list(map(to_msg, items))
        )
        await self.client.send_to_server(msg)

    async def send_control_state_async(self):
        if self.client is None:
            raise ValueError("Client is not connected")

        msg = M.ControlStateMsg(
            is_running=self.engine._runstate_started,
            is_holding=self.engine._runstate_holding,
            is_paused=self.engine._runstate_paused
        )
        await self.client.send_to_server(msg)

    async def _schedule_command(self, msg: M.MessageBase) -> M.MessageBase:
        assert isinstance(msg, M.InvokeCommandMsg)

        # as side effect, start engine on first START command
        # TODO verify this is intended behavior
        # TODO - move this into ExecutionEngine
        if not self.engine.is_running() and msg.name.upper() == "START":
            logger.info("Starting engine on first start command")
            self.engine.run()

        self.engine.schedule_execution(name=msg.name, args=msg.arguments)
        return M.SuccessMessage()

    async def _inject_code(self, msg: M.MessageBase) -> M.MessageBase:
        assert isinstance(msg, M.InjectCodeMsg)
        self.engine.inject_code(msg.pcode)
        return M.SuccessMessage()

    async def get_method(self) -> M.MethodMsg | M.RpcErrorMessage:
        try:
            response = await self.proxy.get_method()
            return response
        except Exception as ex:
            return M.ProtocolErrorMessage(message="Failed to get message", exception_message=str(ex),
                                          protocol_mgs="Exception(?)")

    async def set_method(self, msg: M.MessageBase) -> M.MessageBase:
        assert isinstance(msg, M.MethodMsg)
        return await self.proxy.set_method(msg)

    async def disconnect_async(self):
        if self.client is not None:
            await self.client.disconnect_wait_async()


async def async_main(args):
    uod = None
    if args.uod == 'DemoUod':
        uod = create_demo_uod()
    if uod is None:
        raise ValueError("Uod not configured")

    e = ExecutionEngine(uod, tick_interval=1)

    if args.runner == "DemoTagListener":
        raise NotImplementedError()

    else:
        aggregator_health_url = f"http://{args.aggregator_host}:{args.aggregator_port}/health"
        try:
            resp = httpx.get(aggregator_health_url)
        except httpx.ConnectError as ex:
            print("Connection to Aggregator health end point failed.")
            print(f"Status url: {aggregator_health_url}")
            print(f"Error: {ex}")
            print("OpenPectus Engine cannot start.")
            exit(1)
        if resp.is_error:
            print("Aggregator health end point returned an unsuccessful result.")
            print(f"Status url: {aggregator_health_url}")
            print(f"HTTP status code returned: {resp.status_code}")
            print("OpenPectus Engine cannot start.")
            exit(1)
        aggregator_ws_url = f"ws://{args.aggregator_host}:{args.aggregator_port}/engine-pubsub"
        runner = WebSocketRPCEngineRunner(e, aggregator_ws_url)
        await runner.run_loop_async()


def main():
    args = get_args()
    logger.info("Engine starting")
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
