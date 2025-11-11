import time
import unittest
from typing import Any
from openpectus.engine.internal_commands import InternalCommandsRegistry
from openpectus.engine.internal_commands_impl import StopEngineCommand
from openpectus.lang.exec.regex import RegexNumber
from openpectus.lang.exec.tags_impl import ReadingTag, SelectTag
from openpectus.engine.hardware import RegisterDirection

from openpectus.lang.exec.tags import Tag, TagDirection
from openpectus.lang.exec.uod import UnitOperationDefinitionBase, UodCommand, UodBuilder
from openpectus.test.engine.utility_methods import (
    EngineTestRunner,
    configure_test_logger, set_engine_debug_logging, set_interpreter_debug_logging
)



configure_test_logger()
set_engine_debug_logging()
set_interpreter_debug_logging()


def create_test_uod() -> UnitOperationDefinitionBase:  # noqa
    def reset(cmd: UodCommand, **kvargs) -> None:
        count = cmd.get_iteration_count()
        if count == 0:
            cmd.context.tags.get("Reset").set_value("Reset", time.time())
        elif count == 4:
            cmd.context.tags.get("Reset").set_value("N/A", time.time())
            cmd.set_complete()

    def cmd_with_args(cmd: UodCommand, **kvargs) -> None:
        print("arguments: " + str(kvargs))
        cmd.set_complete()

    def cmd_arg_parse(args: str) -> dict[str, Any] | None:
        if args is None or args == "" or args == "FAIL":
            return None
        result = {}
        for i, item in enumerate(args.split(",")):
            result[f"item{i}"] = item.strip()
        return result

    def cmd_regex(cmd: UodCommand, number, number_unit) -> None:
        cmd.context.tags["CmdWithRegex_Area"].set_value(number + number_unit, time.time())
        cmd.set_complete()

    def overlap_exec(cmd: UodCommand, **kvargs) -> None:
        count = cmd.get_iteration_count()
        if count >= 9:
            cmd.set_complete()

    builder = (
        UodBuilder()
        .with_instrument("TestUod")
        .with_author("Test Author", "test@openpectus.org")
        .with_filename(__file__)
        .with_hardware_none()
        .with_location("Test location")
        .with_hardware_register("FT01", RegisterDirection.Both, path="Objects;2:System;2:FT01")
        .with_hardware_register(
            "Reset",
            RegisterDirection.Both,
            path="Objects;2:System;2:RESET",
            from_tag=lambda x: 1 if x == "Reset" else 0,
            to_tag=lambda x: "Reset" if x == 1 else "N/A",
        )
        # Readings
        .with_tag(ReadingTag("FT01", "L/h"))
        .with_tag(SelectTag("Reset", value="N/A", unit=None, choices=["Reset", "N/A"]))
        .with_tag(Tag("Danger", value=True, unit=None, direction=TagDirection.Output))
        .with_command(name="Reset", exec_fn=reset)
        .with_command(name="CmdWithArgs", exec_fn=cmd_with_args, arg_parse_fn=cmd_arg_parse)
        .with_command(name="overlap1", exec_fn=overlap_exec)
        .with_command(name="overlap2", exec_fn=overlap_exec)
        .with_command_overlap(['overlap1', 'overlap2'])
        .with_tag(Tag("CmdWithRegex_Area", value=""))
        .with_command_regex_arguments(
            name="CmdWithRegexArgs",
            arg_parse_regex=RegexNumber(units=['m2']),
            exec_fn=cmd_regex)
    )
    uod = builder.build()
    uod.hwl.connect()
    return uod


class TestInternalCommandsRegistry(unittest.TestCase):

    def test_can_create_stop_command(self):
        engine = None
        with InternalCommandsRegistry(engine) as registry:
            # commands in internal_commands_impl.py are auto-registered on context creation
            cmd = registry.create_internal_command("Stop", "foo")
            self.assertEqual(cmd.name, "Stop")
            self.assertEqual(cmd.__class__.__name__, "StopEngineCommand")

    @unittest.skip("Does not matter")
    def test_can_create_stop_command_w_class(self):
        engine = None
        with InternalCommandsRegistry(engine) as registry:
            cmd = registry.create_internal_command("Stop", "foo")
            # Note: this may or may not be important. the decorator breaks isinstance
            # but if that is the only problem it is irrelevant.
            # See https://stackoverflow.com/questions/7514968/making-isinstance-work-with-decorators
            # for possible fixes
            self.assertIsInstance(cmd, StopEngineCommand)

    def test_can_create_stop_command_w_instance_id(self):
        engine = None
        with InternalCommandsRegistry(engine) as registry:
            cmd = registry.create_internal_command("Stop", "foo")
            self.assertEqual(cmd.instance_id, "foo")

    def test_stop_command_is_auto_registered_in_engine(self):
        runner = EngineTestRunner(create_test_uod)
        with runner.run() as instance:
            cmd = instance.engine.registry.create_internal_command("Stop", "foo")
            self.assertEqual(cmd.name, "Stop")
            self.assertEqual(cmd.__class__.__name__, "StopEngineCommand")
