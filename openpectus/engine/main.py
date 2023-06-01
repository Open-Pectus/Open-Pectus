
import sys
import os
import time

# TODO replace hack with pip install -e, eg https://stackoverflow.com/questions/30306099/pip-install-editable-vs-python-setup-py-develop
op_path = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(op_path)

from threading import Thread
from typing import Any, List
from typing_extensions import override
from engine.eng import Engine, EngineCommand

from lang.exec import tags
from lang.exec.uod import UnitOperationDefinitionBase, UodCommand
from engine.hardware import HardwareLayerBase, Register, RegisterDirection


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


uod = DemoUod()
e = Engine(uod, tick_interval=1)


class EngineTagListener():
    def __init__(self, e: Engine) -> None:
        self.e = e
        self.running = False

    def run(self):
        self.running = True
        try:
            while self.running:
                tag = e.tag_updates.get()
                if tag is not None:
                    print(f"Tag updated: {tag.name}:\t{tag.get_value()}")
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False


eng_listener = EngineTagListener(e)
eng_listener_thread = Thread(target=eng_listener.run, daemon=True, name="EngineTagListener")


if __name__ == "__main__":
    print("Starting engine")
    eng_listener_thread.start()
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
        eng_listener.stop()
        print("Engine stopped")
