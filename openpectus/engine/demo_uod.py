from typing import List, Any

from openpectus.engine.hardware import RegisterDirection
from openpectus.lang.exec import tags, readings as R
from openpectus.lang.exec.uod import UnitOperationDefinitionBase, UodCommand, UodBuilder


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
        .with_tag(tags.ReadingTag("FT01", "L/h"))
        .with_tag(tags.SelectTag("Reset", value="N/A", unit=None, choices=['Reset', "N/A"]))
        .with_command(UodCommand.builder().with_name("Reset").with_exec_fn(reset))
        .with_process_value(R.Reading(label="Run Time"))
        .with_process_value(R.Reading(label="FT01"))
        .with_process_value(R.Reading(label="Reset"))
        .with_process_value(R.Reading(label="System State"))
        .build()
    )
