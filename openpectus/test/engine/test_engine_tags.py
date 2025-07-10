import datetime
import logging
import platform
import time
import unittest
from typing import Any

from openpectus.engine.models import EngineCommandEnum
from openpectus.lang.exec.regex import RegexNumber
from openpectus.lang.exec.tags_impl import ReadingTag, SelectTag
from openpectus.engine.hardware import RegisterDirection

import pint
from openpectus.lang.exec.tags import SystemTagName, Tag, TagDirection, format_time_as_clock
from openpectus.lang.exec.uod import (
    UnitOperationDefinitionBase,
    UodCommand,
    UodBuilder,
)
from openpectus.test.engine.utility_methods import (
    EngineTestRunner,
    configure_test_logger, set_engine_debug_logging, set_interpreter_debug_logging
)


configure_test_logger()
set_engine_debug_logging()
set_interpreter_debug_logging(include_runlog=True)

# pint takes forever to initialize - long enough
# to throw off timing of the first instruction.
# so we initialize it first
_ = pint.Quantity("0 s")


delta = 0.1

def create_test_uod() -> UnitOperationDefinitionBase:  # noqa C901
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
        p = """\
Wait: 0.9s
Noop: 1
Block: A
    Wait: 2s
    Wait: 3s
    End block
Noop: 2
Wait: 0.99s
"""
        logging.getLogger("openpectus.lang.exec.tags_impl").setLevel(logging.DEBUG)
        delta = 0.4
        runner = EngineTestRunner(create_test_uod, p)
        with runner.run() as instance:
            e = instance.engine
            block_time = e.tags[SystemTagName.BLOCK_TIME]
            block = e.tags[SystemTagName.BLOCK]
            instance.start()

            instance.run_until_instruction("Noop", state="completed")
            self.assertEqual(None, block.get_value())
            self.assertGreater(block_time.as_number(), 1)

            instance.run_until_instruction("Wait", state="started", arguments="2s")
            # instance.run_until_instruction("Block", state="started", arguments="A")
            self.assertEqual("A", block.get_value())
            self.assertAlmostEqual(0.1, block_time.as_number(), delta=delta)

            instance.index_step_back(1)
            instance.run_until_instruction("Wait", state="completed", arguments="2s")
            self.assertAlmostEqual(2, block_time.as_number(), delta=delta)

            instance.run_until_instruction("Wait", state="completed", arguments="3s", max_ticks=40)
            self.assertAlmostEqual(2 + 3, block_time.as_number(), delta=delta)

            instance.index_step_back(10)
            #instance.run_until_instruction("Block", state="completed")
            instance.run_until_instruction("Noop", arguments="2")

            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(1 + 2 + 3 + 0.1, block_time.as_number(), delta=delta)


    def test_tag_pause(self):
        logging.getLogger("openpectus.engine.engine").setLevel(logging.WARNING)
        runner = EngineTestRunner(create_test_uod, "Wait: 10s")
        with runner.run() as instance:
            e = instance.engine
            instance.start()

            instance.run_ticks(2)

            run_time = e.tags[SystemTagName.RUN_TIME]
            block_time = e.tags[SystemTagName.BLOCK_TIME]
            scope_time = e.tags[SystemTagName.SCOPE_TIME]
            self.assertAlmostEqual(0.2, run_time.as_float(), delta=delta)
            self.assertAlmostEqual(0.1, block_time.as_float(), delta=delta)
            self.assertAlmostEqual(0.1, scope_time.as_float(), delta=delta)

            e.schedule_execution(EngineCommandEnum.STOP)
            instance.run_ticks(10)

            self.assertAlmostEqual(0.3, run_time.as_float(), delta=delta)
            self.assertAlmostEqual(0.3, block_time.as_float(), delta=delta)
            self.assertAlmostEqual(0.3, scope_time.as_float(), delta=delta)

            e.schedule_execution(EngineCommandEnum.START)
            instance.run_ticks(5)

            # is reset on system Start
            self.assertAlmostEqual(0.5, run_time.as_float(), delta=delta)
            self.assertAlmostEqual(0.5, block_time.as_float(), delta=delta)
            self.assertAlmostEqual(0.5, scope_time.as_float(), delta=delta)

            e.schedule_execution(EngineCommandEnum.PAUSE)
            instance.run_ticks(5)

            # not paused while system is Paused
            self.assertAlmostEqual(1.0, run_time.as_float(), delta=delta)
            # paused while system is Paused
            self.assertAlmostEqual(0.6, block_time.as_float(), delta=delta)
            self.assertAlmostEqual(0.6, scope_time.as_float(), delta=delta)


    def test_tag_block_time_nested_blocks(self):
        p = """\
Wait: 1s
Block: A
    Wait: 2s
    Block: B
        Wait: 3s
        End block
    Wait: 2s
    End block
Wait: 1s
"""
        delta = 0.2
        runner = EngineTestRunner(create_test_uod, p)
        with runner.run() as instance:
            e = instance.engine
            instance.start()

            instance.run_until_instruction("Wait", state="completed")

            block_time = e.tags[SystemTagName.BLOCK_TIME]
            block = e.tags[SystemTagName.BLOCK]
            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(1, block_time.as_number(), delta=delta)

            instance.run_until_instruction("Block", state="started", arguments="A")
            self.assertEqual("A", block.get_value())
            self.assertAlmostEqual(0.1, block_time.as_number(), delta=delta)

            instance.run_until_instruction("Wait", state="completed", arguments="2s")
            self.assertAlmostEqual(2, block_time.as_number(), delta=delta)

            instance.run_until_instruction("Block", state="started", arguments="B")
            self.assertEqual("B", block.get_value())
            self.assertAlmostEqual(0.1, block_time.as_number(), delta=delta)

            instance.run_until_instruction("Wait", state="completed", arguments="3s", max_ticks=50)
            self.assertAlmostEqual(3, block_time.as_number(), delta=delta)

            instance.index_step_back(3)  # search back to Block: B which is before Wait: 3s
            instance.run_until_instruction("Block", state="completed", arguments="B", increment_index=False)
            # print(instance.get_runtime_table())
            # return
            
            self.assertEqual("A", block.get_value())
            self.assertAlmostEqual(2 + 3, block_time.as_number(), delta=delta)

            instance.index_step_back(2)  # search even further back to Block: A
            instance.run_until_instruction("Block", state="completed", arguments="A")

            self.assertEqual(None, block.get_value())
            # Two times End block = 0.2
            self.assertAlmostEqual(2 + 3 + 2 + 1 + 0.2, block_time.as_number(), delta=delta)

    def test_tag_block_time_restart(self):
        p = """\
Wait: 1s
Block: B1
    Wait: 2s
    End block
"""
        delta = 0.25
        runner = EngineTestRunner(create_test_uod, p)
        with runner.run() as instance:
            e = instance.engine
            instance.start()
            block_time = e.tags[SystemTagName.BLOCK_TIME]
            block = e.tags[SystemTagName.BLOCK]

            instance.run_until_instruction("Wait", state="completed", arguments="1s")
            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(1, block_time.as_number(), delta=delta)

            instance.run_until_instruction("Block", state="started")
            self.assertEqual("B1", block.get_value())
            self.assertAlmostEqual(0.0, block_time.as_number(), delta=delta)

            instance.run_until_instruction("Wait", state="completed", arguments="2s")
            self.assertEqual("B1", block.get_value())
            self.assertAlmostEqual(2, block_time.as_number(), delta=delta)

            instance.index_step_back(2)
            instance.run_until_instruction("Block", state="completed")
            self.assertEqual(None, block.get_value())
            # this is the important test for scope timers
            self.assertAlmostEqual(1 + 2, block_time.as_number(), delta=delta)

            instance.restart_and_run_until_started()
            self.assertAlmostEqual(0.1, block_time.as_number(), delta=delta)  # is reset after restart

            instance.index_step_back(1)
            instance.run_until_instruction("Wait", state="completed", arguments="1s")
            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(1, block_time.as_number(), delta=delta)
            return

            instance.run_until_instruction("Block", state="started")
            self.assertEqual("B1", block.get_value())
            self.assertAlmostEqual(0.1, block_time.as_number(), delta=delta)  # is also reset after restart

    def test_tag_block_time_stop_start(self):
        p = """
Wait: 1s
Block: B1
    Wait: 2s
    End block
"""
        delta = 0.3
        runner = EngineTestRunner(create_test_uod, p)
        with runner.run() as instance:
            e = instance.engine
            instance.start()
            block_time = e.tags[SystemTagName.BLOCK_TIME]
            block = e.tags[SystemTagName.BLOCK]

            instance.run_until_instruction("Wait", state="completed", arguments="1s")
            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(1, block_time.as_number(), delta=delta)

            instance.run_until_instruction("Wait", state="started", arguments="2s")
            self.assertEqual("B1", block.get_value())
            self.assertAlmostEqual(0, block_time.as_number(), delta=delta)

            instance.index_step_back(2)
            instance.run_until_instruction("Block", state="completed")
            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(3, block_time.as_number(), delta=delta)

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
            instance.run_ticks(2)

            flowrate = e.tags["CmdWithRegex_Flowrate"]  # [L/h]

            self.assertEqual(0.0, flowrate.get_value())
            instance.run_ticks(1)
            self.assertEqual(2.0, flowrate.get_value())  # 2 L/h is 2 L/h
            instance.run_ticks(1)
            self.assertEqual(120.0, flowrate.get_value())  # 2 L/min is 120 L/h
            instance.run_ticks(1)
            self.assertEqual(7200.0, flowrate.get_value())  # 2 L/s is 7200 L/h


    def test_watch_has_scope_time(self):
        code = """\
Base: s
0.5 Info: A
Watch: Run Time > 0s
    0.5 Info: B
"""
        delta = 0.2
        runner = EngineTestRunner(create_test_uod, code)
        with runner.run() as instance:
            instance.start()
            scope_time = instance.engine.tags[SystemTagName.SCOPE_TIME]

            instance.run_until_instruction("Info", state="completed", arguments="A")
            self.assertAlmostEqual(0.6, scope_time.as_number(), delta=delta)

            instance.run_until_instruction("Info", state="awaiting_threshold", arguments="B", increment_index=False)
            self.assertAlmostEqual(0, scope_time.as_number(), delta=delta)

            instance.run_until_instruction("Info", state="completed", arguments="B")
            self.assertAlmostEqual(0.6, scope_time.as_number(), delta=delta)

    def test_simulation(self):
        code = """\
Simulate: Run Counter = 7
Simulate off: Run Counter
"""        
        runner = EngineTestRunner(create_test_uod, code)
        with runner.run() as instance:
            instance.start()
            run_counter = instance.engine.tags[SystemTagName.RUN_COUNTER]

            self.assertEqual(run_counter.as_number(), 0)

            instance.run_until_instruction("Simulate", state="completed", arguments="Run Counter = 7")
            self.assertEqual(run_counter.as_number(), 7)

            instance.run_until_instruction("Simulate off", state="completed", arguments="Run Counter")
            self.assertEqual(run_counter.as_number(), 0)

    def test_simulation_is_disabled_on_stop(self):
        code = """\
Simulate: Run Counter = 7
Stop
"""        
        runner = EngineTestRunner(create_test_uod, code)
        with runner.run() as instance:
            instance.start()
            run_counter = instance.engine.tags[SystemTagName.RUN_COUNTER]

            self.assertEqual(run_counter.as_number(), 0)
            
            instance.run_until_instruction("Simulate", state="completed")
            self.assertEqual(run_counter.as_number(), 7)
            
            # Stop should have this effect
            instance.run_until_condition(lambda : run_counter.as_number() == 0)


class TestAccumulation(unittest.TestCase):

    def create_test_uod(self):
        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_author("Test Author", "test@openpectus.org")
               .with_filename(__file__)
               # .with_hardware(TestHW())
               .with_hardware_none()
               .with_location("Test location")
               .with_tag(ReadingTag("CV", "L"))
               .with_tag(CalculatedLinearTag("calc", "L"))
               .with_accumulated_cv(cv_tag_name="CV", totalizer_tag_name="calc")
               .build())
        return uod

    def test_accumulated_column_volume_watch(self):
        program = """
Base: CV
Watch: Accumulated CV > 0.5 CV
    Mark: A
"""
        runner = EngineTestRunner(self.create_test_uod, program)
        with runner.run() as instance:
            instance.start()
            instance.run_ticks(1)

            multiplier = 3.0
            cv = instance.engine.tags["CV"]
            cv.set_value(multiplier, 0)
            acc_cv = instance.engine.tags[SystemTagName.ACCUMULATED_CV]
            self.assertEqual(acc_cv.as_float(), 0.0)
            self.assertEqual(acc_cv.unit, "CV")

            elapsed = instance.run_until_instruction("Mark", state="started")
            self.assertAlmostEqual(5 * multiplier, elapsed, delta=2)


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


class CalculatedLinearTag(Tag):
    """ Test tag that is used to simulate a value that is a linear function of time. """
    def __init__(self, name: str, unit: str | None, slope: float = 1.0) -> None:
        super().__init__(name, value=0.0, unit=unit, direction=TagDirection.NA)
        self.slope = slope

    def on_start(self, run_id: str):
        self.value = time.time() * self.slope

    def on_tick(self, tick_time: float, increment_time: float):
        self.value = time.time() * self.slope
