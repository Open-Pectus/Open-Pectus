import datetime
import logging
import time
import unittest
from typing import Any
from openpectus.engine.models import EngineCommandEnum
from openpectus.lang.exec.tags_impl import ReadingTag, SelectTag
from openpectus.engine.hardware import RegisterDirection

import pint
from openpectus.lang.exec.tags import SystemTagName, Tag, TagDirection, format_time_as_clock
from openpectus.lang.exec.uod import (
    UnitOperationDefinitionBase,
    UodCommand,
    UodBuilder,
    RegexNumber,
)
from openpectus.test.engine.utility_methods import (
    EngineTestRunner,
    configure_test_logger, set_engine_debug_logging, set_interpreter_debug_logging
)


configure_test_logger()
set_engine_debug_logging()
set_interpreter_debug_logging()
logging.getLogger("openpectus.lang.exec.runlog").setLevel(logging.DEBUG)

# pint takes forever to initialize - long enough
# to throw off timing of the first instruction.
# so we initialize it first
_ = pint.Quantity("0 s")


delta = 0.1

def create_test_uod() -> UnitOperationDefinitionBase:
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

    def cmd_regex(cmd: UodCommand, number: str, number_unit: str) -> None:
        cmd.context.tags["CmdWithRegex_Flowrate"].set_value_and_unit(float(number), number_unit, time.time())
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
        .with_tag(Tag("Danger", value=True, unit=None, direction=TagDirection.Output, safe_value=False))
        .with_command(name="Reset", exec_fn=reset)
        .with_command(name="CmdWithArgs", exec_fn=cmd_with_args, arg_parse_fn=cmd_arg_parse)
        .with_command(name="overlap1", exec_fn=overlap_exec)
        .with_command(name="overlap2", exec_fn=overlap_exec)
        .with_command_overlap(['overlap1', 'overlap2'])
        .with_tag(ReadingTag("CmdWithRegex_Flowrate", "L/h"))
        .with_command_regex_arguments(
            name="CmdWithRegexArgs",
            arg_parse_regex=RegexNumber(units=['L/h', 'L/min', 'L/s']),
            exec_fn=cmd_regex)
    )
    uod = builder.build()
    uod.hwl.connect()
    return uod


class TestEngineTags(unittest.TestCase):
    # ---------- Lifetime -------------
    def test_tag_process_time(self):
        runner = EngineTestRunner(create_test_uod)
        with runner.run() as instance:
            e = instance.engine
            instance.start()
            instance.run_ticks(2)

            process_time = e.tags[SystemTagName.PROCESS_TIME]
            self.assertAlmostEqual(0.2, process_time.as_float(), delta=delta)

            e.schedule_execution(EngineCommandEnum.STOP)
            instance.run_ticks(10)
            self.assertAlmostEqual(0.3, process_time.as_float(), delta=delta)

            e.schedule_execution(EngineCommandEnum.START)
            instance.run_ticks(5)

            # is reset on system Start
            self.assertAlmostEqual(0.5, process_time.as_float(), delta=delta)

            e.schedule_execution(EngineCommandEnum.PAUSE)
            instance.run_ticks(5)

            # is paused while system is Paused
            self.assertAlmostEqual(0.6, process_time.as_float(), delta=delta)

            e.schedule_execution(EngineCommandEnum.UNPAUSE)
            instance.run_ticks(5)

            self.assertAlmostEqual(1.0, process_time.as_float(), delta=delta)

    def test_tag_run_time(self):
        runner = EngineTestRunner(create_test_uod)
        with runner.run() as instance:
            e = instance.engine
            instance.start()

            instance.run_ticks(2)

            run_time = e.tags[SystemTagName.RUN_TIME]
            self.assertAlmostEqual(0.2, run_time.as_float(), delta=delta)

            e.schedule_execution(EngineCommandEnum.STOP)
            instance.run_ticks(10)

            self.assertAlmostEqual(0.3, run_time.as_float(), delta=delta)

            e.schedule_execution(EngineCommandEnum.START)
            instance.run_ticks(5)

            # is reset on system Start
            self.assertAlmostEqual(0.5, run_time.as_float(), delta=delta)

            e.schedule_execution(EngineCommandEnum.PAUSE)
            instance.run_ticks(5)

            # not paused while system is Paused
            self.assertAlmostEqual(1.0, run_time.as_float(), delta=delta)

    def test_tag_block_time(self):
        p = """
Wait: 0.25s
Block: B1
    Wait: 0.25s
    End block
"""
        runner = EngineTestRunner(create_test_uod, p)
        with runner.run() as instance:
            e = instance.engine
            instance.start()

            instance.run_ticks(2)

            block_time = e.tags[SystemTagName.BLOCK_TIME]
            block = e.tags[SystemTagName.BLOCK]

            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(0.2, block_time.as_number(), delta=delta)

            instance.run_ticks(4)
            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(0.6, block_time.as_number(), delta=delta)

            instance.run_ticks(1)
            self.assertEqual("B1", block.get_value())
            self.assertAlmostEqual(0.1, block_time.as_number(), delta=delta)

            instance.run_ticks(6)
            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(0.1 + 0.6, block_time.as_number(), delta=delta)

    # @unittest.skip("Test is likely wrong. Should discuss nested block times")
    def test_tag_block_time_nested_blocks(self):
        p = """
Block: B1
    Wait: 0.15s
    Block: B2
        Wait: 0.05s
        End block
    Wait: 0.25s
    End block
"""
        runner = EngineTestRunner(create_test_uod, p)
        with runner.run() as instance:
            e = instance.engine
            instance.start()

            block_time = e.tags[SystemTagName.BLOCK_TIME]
            block = e.tags[SystemTagName.BLOCK]

            instance.run_ticks(2)

            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(0.2, block_time.as_number(), delta=delta)

            instance.run_until_event("block_start")
            self.assertEqual("B1", block.get_value())
            self.assertAlmostEqual(0.1, block_time.as_number(), delta=delta)
            instance.run_ticks(3)
            self.assertEqual("B1", block.get_value())
            self.assertAlmostEqual(0.4, block_time.as_number(), delta=delta)

            instance.run_until_event("block_start")
            self.assertEqual("B2", block.get_value())
            self.assertAlmostEqual(0.1, block_time.as_number(), delta=delta)

            instance.run_ticks(3)
            self.assertEqual("B2", block.get_value())
            self.assertAlmostEqual(0.4, block_time.as_number(), delta=delta)

            instance.run_until_event("block_end")
            # continue_engine(e, 1)
            self.assertEqual("B1", block.get_value())
            # TODO currently does not increment block B1 timer while B2 is active
            self.assertAlmostEqual(0.5, block_time.as_number(), delta=delta)  # 0.4 + 0.4 ???
            # self.assertAlmostEqual(0.5 + 0.4, block_time.as_number(), delta=delta)  # 0.4 + 0.4 ???
            # continue_engine(e, 4)
            # self.assertEqual("B1", block.get_value())
            # self.assertAlmostEqual(0.9, block_time.as_number(), delta=delta)

            # continue_engine(e, 1)
            # self.assertEqual(None, block.get_value())
            # self.assertAlmostEqual(0.2, block_time.as_number(), delta=delta)  # 0.9 + 0.2 ???

    def test_tag_block_time_restart(self):
        p = """
Wait: 0.25s
Block: B1
    Wait: 0.25s
    End block
"""
        runner = EngineTestRunner(create_test_uod, p)
        with runner.run() as instance:
            e = instance.engine
            instance.start()
            block_time = e.tags[SystemTagName.BLOCK_TIME]
            block = e.tags[SystemTagName.BLOCK]

            instance.run_ticks(2)
            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(0.2, block_time.as_number(), delta=delta)

            instance.run_ticks(4)
            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(0.6, block_time.as_number(), delta=delta)

            instance.run_ticks(1)
            self.assertEqual("B1", block.get_value())
            self.assertAlmostEqual(0.1, block_time.as_number(), delta=delta)

            instance.run_ticks(6)
            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(0.1 + 0.6, block_time.as_number(), delta=delta)

            e.schedule_execution(EngineCommandEnum.RESTART)
            instance.run_ticks(3)
            self.assertAlmostEqual(0.1, block_time.as_number(), delta=delta)  # is reset after restart

            # instance.run_until_condition(lambda: block.get_value() == "B1")
            instance.run_until_event("block_start")
            self.assertAlmostEqual(0.1, block_time.as_number(), delta=delta)  # nested timer is also reset

    def test_tag_block_time_stop_start(self):
        p = """
Wait: 0.25s
Block: B1
    Wait: 0.25s
    End block
"""
        runner = EngineTestRunner(create_test_uod, p)
        with runner.run() as instance:
            e = instance.engine
            instance.start()
            block_time = e.tags[SystemTagName.BLOCK_TIME]
            block = e.tags[SystemTagName.BLOCK]

            instance.run_ticks(2)
            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(0.2, block_time.as_number(), delta=delta)

            instance.run_ticks(4)
            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(0.6, block_time.as_number(), delta=delta)

            instance.run_ticks(1)
            self.assertEqual("B1", block.get_value())
            self.assertAlmostEqual(0.1, block_time.as_number(), delta=delta)

            instance.run_ticks(6)
            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(0.1 + 0.6, block_time.as_number(), delta=delta)

            e.schedule_execution(EngineCommandEnum.STOP)
            instance.run_ticks(3)

            e.schedule_execution(EngineCommandEnum.START)
            instance.run_ticks(1)
            self.assertAlmostEqual(0.1, block_time.as_number(), delta=delta)  # is reset after restart

            instance.run_until_event("block_start")
            self.assertAlmostEqual(0.1, block_time.as_number(), delta=delta)  # nested timer is also reset

    def test_tag_unit_conversion_handled_by_pint(self):
        p = """
CmdWithRegexArgs: 2 L/h
CmdWithRegexArgs: 2 L/min
CmdWithRegexArgs: 2 L/s
"""
        runner = EngineTestRunner(create_test_uod, p)
        with runner.run() as instance:
            e = instance.engine
            instance.start()
            flowrate = e.tags["CmdWithRegex_Flowrate"]  # [L/h]

            instance.run_ticks(1)
            self.assertEqual(0.0, flowrate.get_value())
            instance.run_ticks(2)
            self.assertEqual(2.0, flowrate.get_value())  # 2 L/h is 2 L/h
            instance.run_ticks(1)
            self.assertEqual(120.0, flowrate.get_value())  # 2 L/min is 120 L/h
            instance.run_ticks(1)
            self.assertEqual(7200.0, flowrate.get_value())  # 2 L/s is 7200 L/h



class TestFormatting(unittest.TestCase):

    def test_formatting(self):
        tag = Tag("foo")

        tag.format_fn = format_time_as_clock
        _date = datetime.datetime(
            year=2000, month=1, day=1, hour=6, minute=46, second=3, microsecond=111, tzinfo=datetime.UTC
        )
        tag.value = _date.timestamp()

        t = tag.as_readonly()

        self.assertEqual("06:46:03", t.value_formatted)
        self.assertIsNotNone(t.value_formatted)
