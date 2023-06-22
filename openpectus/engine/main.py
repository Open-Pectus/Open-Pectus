import asyncio
from queue import Empty
import time
from argparse import ArgumentParser
from threading import Thread
from typing import Any, List
from typing_extensions import override

from openpectus.protocol.engine import Client, create_client
from openpectus.engine.eng import Engine, EngineCommand
from openpectus.engine.hardware import HardwareLayerBase, Register, RegisterDirection
from openpectus.lang.exec import tags
from openpectus.lang.exec.uod import UnitOperationDefinitionBase, UodCommand
from openpectus.protocol.messages import (
    RegisterEngineMsg,
    MessageBase,
    SuccessMessage,
    TagsUpdatedMsg,
    TagValue,
    InvokeCommandMsg
)


def get_args():
    parser = ArgumentParser("Start Pectus Engine")
    parser.add_argument("-ws", "--aggregator_ws_url", required=False, default="ws://127.0.0.1:9800/pubsub",
                        # default="ws://localhost:9800/pubsub",
                        help="Address to aggregator web socket service. Default is ws://127.0.0.1:9800/pubsub")
    parser.add_argument("-uod", "--uod", required=False, default="DemoUod", help="The UOD to use")
    parser.add_argument("-r", "--runner", required=False, default="WebSocketRPCEngineRunner",
                        choices=['WebSocketRPCEngineRunner', 'DemoEngineRunner'],
                        help="The event listener to use")
    return parser.parse_args()


class DemoHW(HardwareLayerBase):
    def __init__(self) -> None:
        super().__init__()
        self.register_values = {}

    @override
    def read(self, r: Register) -> Any:
        if r.name in self.registers.keys() and r.name in self.register_values.keys():
            return self.register_values[r.name]
        return None

    @override
    def write(self, value: Any, r: Register):
        if r.name in self.registers.keys():
            self.register_values[r.name] = value


class DemoUod(UnitOperationDefinitionBase):
    def define(self):
        self.define_instrument("TestUod")
        self.define_hardware_layer(DemoHW())

        self.define_register("FT01", RegisterDirection.Both, path='Objects;2:System;2:FT01')
        self.define_register("Reset", RegisterDirection.Both, path='Objects;2:System;2:RESET',
                             from_tag=lambda x: 1 if x == 'Reset' else 0,
                             to_tag=lambda x: "Reset" if x == 1 else "N/A")

        self.define_tag(tags.Reading("FT01", "L/h"))
        self.define_tag(tags.Select("Reset", value="N/A", unit=None, choices=['Reset', "N/A"]))

        # start = time.time()

        # def x():
        #     elapsed = time.time() - start
        #     return elapsed

        # self.tags["FT01"].get_value = x

        self.define_command(DemoResetCommand())


class DemoResetCommand(UodCommand):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Reset"
        self.is_complete = False

    def execute(self, args: List[Any], uod: UnitOperationDefinitionBase) -> None:
        if self.iterations == 0:
            uod.tags.get("Reset").set_value("Reset")
        elif self.iterations == 5:
            uod.tags.get("Reset").set_value("N/A")
            self.is_complete = True
            self.iterations = 0


class EngineRunner:
    def __init__(self, engine: Engine) -> None:
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

    async def send_tag_updates_async(self):
        raise NotImplementedError()

    async def run_loop(self):
        try:
            await self.connect_async()
            await self.register_async()
            await self.notify_initial_tags_async()

            while True:
                await asyncio.sleep(0.1)
                await self.send_tag_updates_async()
        except KeyboardInterrupt:
            await self.disconnect_async()
        except asyncio.CancelledError:
            return


class DemoEngineRunner():
    def __init__(self, e: Engine) -> None:
        self.e = e
        self.running = False

    async def connect_async(self):
        pass

    async def disconnect_async(self):
        self.running = False

    async def register_async(self):
        pass

    async def run_loop(self):
        self.running = True
        try:
            while self.running:
                time.sleep(0.1)

                tag = None
                try:
                    tag = self.e.tag_updates.get_nowait()
                    # tag = self.e.tag_updates.get()
                except Empty:
                    pass
                if tag is not None:
                    print(f"Tag updated: {tag.name}:\t{tag.get_value()}")

        except KeyboardInterrupt:
            await self.disconnect_async()


class WebSocketRPCEngineRunner(EngineRunner):
    def __init__(self, engine: Engine, ws_url: str) -> None:
        self.engine = engine
        self.client: Client | None = None
        self.ws_url = ws_url

    async def connect_async(self):
        client = create_client()
        self.client = client
        await self.client.start_connect_wait_async(ws_url=self.ws_url)

    async def register_async(self):
        if self.client is None:
            raise ValueError("Client is not connected")

        msg = RegisterEngineMsg(engine_name="test-eng", uod_name=self.engine.uod.instrument)
        response = await self.client.send_to_server(msg)  # , on_success=on_register, on_error=on_error)
        if not isinstance(response, SuccessMessage):
            print("Failed to Register")

        self.client.set_message_handler("InvokeCommandMsg", self._schedule_command)

    async def send_tag_updates_async(self):
        if self.client is None:
            raise ValueError("Client is not connected")

        tags = []
        try:
            for _ in range(100):
                tag = self.engine.tag_updates.get_nowait()
                tags.append(TagValue(name=tag.name, value=tag.get_value(), value_unit=tag.unit))
        except Empty:
            pass
        if len(tags) > 0:
            msg = TagsUpdatedMsg(tags=tags)
            await self.client.send_to_server(msg)

    async def _schedule_command(self, msg: MessageBase) -> MessageBase:
        assert isinstance(msg, InvokeCommandMsg)

        # as side effect, start engine on first START command
        # TODO verify this is intended behavior
        if not self.engine.is_running() and msg.name.upper() == "START":
            self.engine.run()

        cmd = EngineCommand(name=msg.name, args=msg.arguments)
        self.engine.cmd_queue.put_nowait(cmd)
        return SuccessMessage()

    async def disconnect_async(self):
        if self.client is not None:
            await self.client.disconnect_wait_async()


async def main(args):
    uod = None
    if args.uod == 'DemoUod':
        uod = DemoUod()
    if uod is None:
        raise ValueError("Uod not configured")

    e = Engine(uod, tick_interval=1)

    if args.runner == "DemoTagListener":
        runner = DemoEngineRunner(e)
        await runner.run_loop()

        listener_thread = Thread(target=runner.run, daemon=True, name=runner.__class__.__name__)

        print("Starting engine")
        listener_thread.start()
        e.run()

        secs_start = time.time() + 5
        secs_stop = secs_start + 10
        secs_reset = secs_start + 5
        never = time.time() * 2
        try:
            while True:
                time.sleep(.1)

                if e._tick_time > secs_start:
                    e.cmd_queue.put(EngineCommand("START"))
                    secs_start = never

                if e._tick_time > secs_reset:
                    e.cmd_queue.put(EngineCommand("RESET"))
                    secs_reset = never

                if e._tick_time > secs_stop:
                    e.cmd_queue.put(EngineCommand("STOP"))
                    secs_stop = never

        except KeyboardInterrupt:
            # TODO
            # e.shutdown()
            runner.stop()
            print("Engine stopped")

    else:

        runner = WebSocketRPCEngineRunner(e, args.aggregator_ws_url)
        await runner.run_loop()


if __name__ == "__main__":
    args = get_args()
    asyncio.run(main(args))
