import math
from time import time
from typing import List, Any

from openpectus.engine.hardware import HardwareLayerBase, Register, RegisterDirection
from openpectus.lang.exec import tags, readings as R
from openpectus.lang.exec.uod import UnitOperationDefinitionBase, UodCommand, UodBuilder


def create_demo_uod() -> UnitOperationDefinitionBase:
    def reset(cmd: UodCommand, args: List[Any]) -> None:
        count = cmd.get_iteration_count()
        if count == 0:
            cmd.context.tags.get("Reset").set_value("Reset", time())
            cmd.context.hwl.reset_FT01()  # type: ignore
        elif count == 4:
            cmd.context.tags.get("Reset").set_value("N/A", time())
            cmd.set_complete()

    return (
        UodBuilder()
        .with_instrument("DemoUod")
        .with_hardware(DemoHardware())
        .with_location("Demo location")
        .with_hardware_register("FT01", RegisterDirection.Read, path='Objects;2:System;2:FT01')
        .with_hardware_register("FT02", RegisterDirection.Read, path='Objects;2:System;2:FT02')
        .with_hardware_register("Time", RegisterDirection.Read)
        .with_hardware_register("Reset", RegisterDirection.Both, path='Objects;2:System;2:RESET',
                                from_tag=lambda x: 1 if x == 'Reset' else 0,
                                to_tag=lambda x: "Reset" if x == 1 else "N/A")
        .with_new_system_tags()
        .with_tag(tags.ReadingTag("FT01", "L/h"))
        .with_tag(tags.ReadingTag("FT02", "L/h"))
        .with_tag(tags.ReadingTag("Time"))
        .with_tag(tags.SelectTag("Reset", value="N/A", unit=None, choices=['Reset', "N/A"]))
        .with_command(UodCommand.builder().with_name("Reset").with_exec_fn(reset))
        .with_process_value(R.Reading(label="Run Time"))
        .with_process_value(R.Reading(label="FT01"))
        .with_process_value(R.Reading(label="FT02"))
        .with_process_value(R.Reading(label="Time"))
        .with_process_value(R.Reading(label="Reset"))
        .with_process_value(R.Reading(label="System State"))
        .build()
    )


class DemoHardware(HardwareLayerBase):
    """ Simulation hardware. """
    def __init__(self) -> None:
        super().__init__()
        self.start_time: float = time()

    def reset_FT01(self):
        self.start_time = time()

    def read(self, r: Register) -> Any:
        if r.name == "FT01":
            elapsed_seconds = time() - self.start_time
            minutes = elapsed_seconds / 60
            return int(10 * (math.sin(minutes) + 1))
        if r.name == "FT02":
            elapsed_seconds = time() - self.start_time
            minutes = elapsed_seconds / 60
            return 10 * (math.sin(minutes) + 1)
        elif r.name == "Time":
            return time() - self.start_time

    def write(self, value: Any, r: Register):
        pass
