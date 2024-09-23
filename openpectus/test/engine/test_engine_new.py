import logging
import time
import unittest
from typing import Any
from openpectus.lang.exec.tags_impl import ReadingTag, SelectTag

import pint
from openpectus.lang.exec.tags import SystemTagName, Tag, TagDirection
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
        .with_hardware_register("FT01", "Both", path="Objects;2:System;2:FT01")
        .with_hardware_register(
            "Reset",
            "Both",
            path="Objects;2:System;2:RESET",
            from_tag=lambda x: 1 if x == "Reset" else 0,
            to_tag=lambda x: "Reset" if x == 1 else "N/A",
        )
        # Readings
        .with_tag(ReadingTag("FT01", "L/h"))
        .with_tag(SelectTag("Reset", value="N/A", unit=None, choices=["Reset", "N/A"]))
        .with_tag(Tag("Danger", value=True, unit=None, direction=TagDirection.OUTPUT, safe_value=False))
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


class TestEngineNew(unittest.TestCase):

    def test_run_until_condition(self):
        runner = EngineTestRunner(create_test_uod)
        with runner.run() as instance:
            run_time = instance.engine.tags[SystemTagName.RUN_TIME]

            instance.start()
            start = time.time()
            instance.run_until_condition(lambda: run_time.as_float() >= 1)
            end = time.time()
            self.assertAlmostEqual(end-start, 1.1, delta=0.2)

    def test_wait(self):
        code = """
Wait: 1s
Mark: A
"""
        runner = EngineTestRunner(create_test_uod, code)
        with runner.run() as instance:
            instance.start()
            ticks = instance.run_until_instruction("Mark")
            self.assertAlmostEqual(1+10+1+1, ticks, delta=2)

    def test_run_until_instruction(self):
        code = """
Mark: A
Wait: 1s
Pause: 1.5s
Mark: B
"""
        runner = EngineTestRunner(create_test_uod, code)
        with runner.run() as instance:
            instance.start()
            run_time = instance.engine.tags[SystemTagName.RUN_TIME]

            instance.run_until_instruction("Mark")
            # two ticks passed before the first "user" instruction. That is expected
            self.assertAlmostEqual(0.2, run_time.as_float(), delta=0.1)

            instance.run_until_instruction("Pause")

            #self.assertAlmostEqual(1.1, run_time.as_float(), delta=0.1)
            instance.run_until_instruction("Mark")

            with self.assertRaises(TimeoutError):
                instance.run_until_instruction("Mark")

    def test_run_until_instruction_block(self):
        code = """
Mark: A
Block: A
    Pause: 1s
    End block
    Wait: 1s
Mark: B
"""
        runner = EngineTestRunner(create_test_uod, code)
        with runner.run() as instance:
            instance.start()

            self.assertEqual([], instance.engine.interpreter.get_marks())

            instance.run_until_instruction("Block")
            self.assertEqual(['A'], instance.engine.interpreter.get_marks())

            with self.assertRaises(TimeoutError):
                instance.run_until_instruction("Wait")

            instance.run_until_instruction("Mark")

            # This is a little funky in that get_marks() uses the same record as source
            # as does run_until_instruction(). Thefore B is marked even "before" it runs
            self.assertEqual(['A', 'B'], instance.engine.interpreter.get_marks())

    def test_watch_restart(self):
        code = """
Watch: Run Counter >= 2
    Stop

Wait: 1s
Increment run counter
Restart
"""
        runner = EngineTestRunner(create_test_uod, code)

        with runner.run() as instance:
            run_counter = instance.engine.tags["Run Counter"]
            instance.start()
            # Run Counter is 0 by default, and indicates the number of completed runs
            self.assertEqual(0, run_counter.as_number())

            instance.run_until_instruction("Restart")
            self.assertEqual(1, run_counter.as_number())
            instance.run_until_event("start")

            print(instance.get_runtime_table("A"))

            instance.run_until_instruction("Restart")
            # Increment run counter should have incremented it - wtf?
            #self.assertEqual(2, run_counter.as_number())

            instance.run_until_event("start")
            instance.run_until_instruction("Watch")
            
            

            print(instance.get_runtime_table("B"))

            with self.assertRaises(TimeoutError):
                instance.run_until_instruction("Restart")

            print(instance.get_runtime_table("C"))


    def test_run_until_method_end(self):
        code = """
Mark: A
Mark: B
Mark: C
"""
        runner = EngineTestRunner(create_test_uod, code)
        logging.getLogger("openpectus.lang.exec.pinterpreter").setLevel(logging.DEBUG)

        with runner.run() as instance:
            instance.start()
            self.assertEqual([], instance.engine.interpreter.get_marks())
            instance.run_until_event("method_end")
            self.assertEqual(['A', 'B', 'C'], instance.engine.interpreter.get_marks())


    def test_run_until_stop(self):
        code = """
Mark: A
Stop
"""
        runner = EngineTestRunner(create_test_uod, code)
        logging.getLogger("openpectus.lang.exec.pinterpreter").setLevel(logging.DEBUG)

        with runner.run() as instance:
            instance.start()
            instance.run_until_event("stop")
            self.assertEqual([], instance.engine.interpreter.get_marks())


    def test_speed_perceived(self):
        pcode = """
Base: s
Mark: A
Wait: 15s
15 Mark: A2
Mark: B
"""
        runner = EngineTestRunner(create_test_uod, pcode=pcode, speed=30)
        with runner.run() as instance:
            instance.start()
            run_time = instance.engine.tags[SystemTagName.RUN_TIME]
            time.sleep(1)
            self.assertAlmostEqual(run_time.as_float(), 30, delta=3)

            time.sleep(1)
            self.assertAlmostEqual(run_time.as_float(), 60, delta=3)
            

    def test_speed_timer(self):
        pcode = """
Wait: 30s
Mark: B
"""
        runner = EngineTestRunner(create_test_uod, pcode=pcode, speed=30)
        with runner.run() as instance:
            run_time = instance.engine.tags[SystemTagName.RUN_TIME]
            instance.start()

            instance.run_until_instruction("Wait", "started")
            run_time.set_value(0, 0)

            instance.run_until_instruction("Mark")
            # Why the two ticks threshold?
            # Completing Wait takes a tick and 30 secs at speed 30 can vary one tick in evaluation
            run_time_value = run_time.as_float()
            self.assertAlmostEqual(33, run_time_value, delta=3)

    # speed is really important as it allows tests that wait much longer than a few ticks.
    # This allows testing timers much easier because we can use much larger periods - without
    # longer test runs. The key is that single ticks drown in long waiting times and becomes
    # irrelevant, just as they are in practice.

