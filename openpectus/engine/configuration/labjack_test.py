from time import time
from openpectus.engine.uod_builder_api import (
    UnitOperationDefinitionBase, UodCommand, UodBuilder,
    tags, RegisterDirection,
)


def create() -> UnitOperationDefinitionBase:
    builder = UodBuilder()

    def reset(cmd: UodCommand, value):
        cmd.context.tags.get("RESET").set_value(time(), time())
        cmd.set_complete()

    return (
        builder
        .with_instrument("LabJack-Test")
        .with_author("Demo Author", "demo@openpectus.org")
        .with_filename(__file__)
        .with_hardware_labjack()
        .with_location("Test location")
        .with_hardware_register("RESET", RegisterDirection.Both, port='USER_RAM0_F32')
        .with_hardware_register("SERIAL_NUMBER", RegisterDirection.Read, port='SERIAL_NUMBER')

        .with_tag(tags.ReadingTag(name="RESET"))
        .with_tag(tags.ReadingTag(name="SERIAL_NUMBER"))

        .with_command("RESET", exec_fn=reset)

        .with_process_value_choice(tag_name="RESET", command_options={"Reset": "RESET"})
        .with_process_value("SERIAL_NUMBER")

        .build()
    )
