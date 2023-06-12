
import asyncio
import os
from queue import Empty
import sys
import time
from argparse import ArgumentParser
from threading import Thread
from typing import Any, List
from typing_extensions import override
from fastapi_websocket_pubsub import PubSubClient

# TODO replace hack with pip install -e, eg https://stackoverflow.com/questions/30306099/pip-install-editable-vs-python-setup-py-develop
op_path = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(op_path)

from protocol.engine import Client
from engine.eng import Engine, EngineCommand
from engine.hardware import HardwareLayerBase, Register, RegisterDirection
from lang.exec import tags
from lang.exec.uod import UnitOperationDefinitionBase, UodCommand
from protocol.engine import create_client
from protocol.messages import (
    RegisterEngineMsg, SuccessMessage, ErrorMessage, TagsUpdatedMsg, TagValue
    )


def get_args():
    parser = ArgumentParser("Start Pectus Engine")
    parser.add_argument("-ws", "--aggregator_ws_url", required=False, default="ws://localhost:7980/pubsub",
                        help="Address to aggregator service")
    parser.add_argument("-uod", "--uod", required=False, default="DemoUod", help="The UOD to use")
    parser.add_argument("-l", "--listener", required=False, default="DemoTagListener",
                        choices=['EngineWebSocketListener', 'DemoTagListener'],
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


class DemoTagListener():
    def __init__(self, e: Engine) -> None:
        self.e = e
        self.running = False

    def run(self):
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
            self.stop()

    def stop(self):
        self.running = False


class EngineWebSocketListener():
    def __init__(self, engine: Engine, ws_url: str) -> None:
        self.engine = engine
        self.client: Client | None = None
        self.ps_client: PubSubClient | None = None
        self.ws_url = ws_url

    async def connect(self):
        client, ps_client = create_client()
        self.client = client
        self.ps_client = ps_client

        await client.wait_start_connect(ws_url=self.ws_url, ps_client=self.ps_client)

        #TODO register callback to handle incoming messages
        #is self.client.set_rpc_handler called or do we need this
        handler = Rpc 
        

    async def register(self):
        if self.client is None:
            raise ValueError("Client is not connected")

        msg = RegisterEngineMsg(engine_name="test-eng", uod_name=self.engine.uod.instrument)
        response = await self.client.send_to_server(msg)  # , on_success=on_register, on_error=on_error)
        if not isinstance(response, SuccessMessage):
            print("Failed to Register")

    async def send_tag_updates(self):
        if self.client is None:
            raise ValueError("Client is not connected")

        tags = []
        try:
            for _ in range(100):
                tag = self.engine.tag_updates.get_nowait()
                tags.append(TagValue(name=tag.name, value=tag.get_value()))
        except Empty:
            pass
        if len(tags) > 0:
            msg = TagsUpdatedMsg(tags=tags)
            await self.client.send_to_server(msg)

    async def dispatch_commands(self):
        raise NotImplementedError()


async def main(args):
    uod = None
    if args.uod == 'DemoUod':
        uod = DemoUod()
    if uod is None:
        raise ValueError("Uod not configured")

    e = Engine(uod, tick_interval=1)

    if args.listener == "DemoTagListener":
        listener = DemoTagListener(e)
        listener_thread = Thread(target=listener.run, daemon=True, name=listener.__class__.__name__)

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
            listener.stop()
            print("Engine stopped")

    else:

        listener = EngineWebSocketListener(e, args.ws)
        await listener.connect()
        await listener.register()

        while True:
            await asyncio.sleep(0.1)
            await listener.send_tag_updates()
            await listener.dispatch_commands()


if __name__ == "__main__":
    args = get_args()
    asyncio.run(main(args))
