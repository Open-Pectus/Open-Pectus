import datetime
import logging
import time
import unittest
from typing import Any

from openpectus.engine.models import EngineCommandEnum, MethodStatusEnum
from openpectus.lang.exec.errors import EngineError
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
from openpectus.test.engine.test_helpers import TestHW
from openpectus.test.engine.utility_methods import (
    EngineTestRunner,
    configure_test_logger, set_engine_debug_logging, set_interpreter_debug_logging
)
from openpectus.lang.exec.units import as_decimal


configure_test_logger()
set_engine_debug_logging()
set_interpreter_debug_logging(include_runlog=True, include_events=True)

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
        cmd.context.tags["CmdWithRegex_Flowrate"].set_value_and_unit(as_decimal(number), number_unit, time.time())
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
        .with_hardware_register(
            "Danger",
            RegisterDirection.Write,
            path="Objects;2:System;2:Danger",
            safe_value=False,
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
        .with_tag(ReadingTag("CmdWithRegex_Flowrate", "L/h"))
        .with_command_regex_arguments(
            name="CmdWithRegexArgs",
            arg_parse_regex=RegexNumber(units=['L/h', 'L/min', 'L/s']),
            exec_fn=cmd_regex)
    )
    uod = builder.build()
    uod.hwl.connect()
    return uod


# Note: These tests are affected by the runner's _initial_increment.
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
Noop: 10
Block: A
    Wait: 2s
    Wait: 3s
    End block
Noop: 2
"""
        logging.getLogger("openpectus.lang.exec.tags_impl").setLevel(logging.DEBUG)
        delta = 0.4
        runner = EngineTestRunner(create_test_uod, p)
        with runner.run() as instance:
            e = instance.engine
            block_time = e.tags[SystemTagName.BLOCK_TIME]
            block = e.tags[SystemTagName.BLOCK]
            instance.start_run()

            t1 = instance.run_until_instruction("Noop", state="completed")
            t1_value = t1/10
            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(block_time.as_number(), t1_value, delta=0.2)

            instance.run_until_instruction("Wait", state="started", arguments="2s")
            self.assertEqual("A", block.get_value())
            self.assertAlmostEqual(0.1, block_time.as_number(), delta=delta)

            instance.index_step_back(1)
            instance.run_until_instruction("Wait", state="completed", arguments="2s")
            self.assertAlmostEqual(2, block_time.as_number(), delta=delta)

            instance.run_until_instruction("Wait", state="completed", arguments="3s", max_ticks=40)
            self.assertAlmostEqual(2 + 3, block_time.as_number(), delta=delta)

            instance.index_step_back(10)
            # instance.run_until_instruction("Block", state="completed")
            t2 = instance.run_until_instruction("Noop", arguments="2")
            t2_value = t2/10

            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(t1_value + 2 + 3 + t2_value, block_time.as_number(), delta=delta)


    def test_tag_pause(self):
        delta = 0.05
        logging.getLogger("openpectus.engine.engine").setLevel(logging.WARNING)
        code = """\
Wait: 0.5s
Pause: 0.5s
Mark: A
"""
        runner = EngineTestRunner(create_test_uod, code)
        with runner.run() as instance:
            e = instance.engine
            instance.start_run()

            run_time = e.tags[SystemTagName.RUN_TIME]
            block_time = e.tags[SystemTagName.BLOCK_TIME]
            scope_time = e.tags[SystemTagName.SCOPE_TIME]
            self.assertAlmostEqual(0.0, run_time.as_float(), delta=delta)
            self.assertAlmostEqual(0.0, block_time.as_float(), delta=delta)
            self.assertAlmostEqual(0.0, scope_time.as_float(), delta=delta)

            t1 = instance.run_until_instruction("Wait", state="completed")
            t1_value = t1/10

            print(f"{run_time.value=} | {block_time.value=} | {scope_time.value=}")

            # run_time is just one tick ahead of the others
            self.assertAlmostEqual(t1_value, run_time.as_float(), delta=delta)
            self.assertAlmostEqual(t1_value-.1, block_time.as_float(), delta=delta)
            self.assertAlmostEqual(t1_value-.1, scope_time.as_float(), delta=delta)

            t2 = instance.run_until_instruction("Pause", state="completed")
            t2_value = t2/10

            t3 = instance.run_until_instruction("Mark", state="completed")
            t3_value = t3/10

            print(f"{run_time.value=} | {block_time.value=} | {scope_time.value=}")

            self.assertAlmostEqual(t1_value + t2_value + t3_value, run_time.as_float(), delta=delta)   # not paused while system is Paused
            self.assertAlmostEqual(t1_value + t3_value + 0.1, block_time.as_float(), delta=delta)  # paused while system is Paused
            self.assertAlmostEqual(t1_value + t3_value + 0.1, scope_time.as_float(), delta=delta)  # paused while system is Paused

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
            instance.start_run()

            block_time = instance.engine.tags[SystemTagName.BLOCK_TIME]
            block = instance.engine.tags[SystemTagName.BLOCK]

            t1 = instance.run_until_instruction("Block", state="started", arguments="A")
            t1_time = t1/10
            #instance.logger.info(f"Block: {block.get_value()} | Block time: {block_time.as_float():.2f}")
            self.assertEqual("A", block.get_value())
            self.assertAlmostEqual(0, block_time.as_number(), delta=delta)

            t2 = instance.run_until_instruction("Block", state="started", arguments="B")
            t2_time = t2/10
            self.assertEqual("B", block.get_value())
            self.assertAlmostEqual(0, block_time.as_number(), delta=delta)

            instance.index_step_back(5)  # search back to Block: B which is before Wait: 3s
            t3 = instance.run_until_instruction("Block", state="completed", arguments="B", max_ticks=40)
            t3_time = t3/10
            # print(instance.get_runtime_table())

            self.assertEqual("A", block.get_value())
            self.assertAlmostEqual(t2_time + t3_time, block_time.as_number(), delta=delta)
            
            instance.index_step_back(5)  # search even further back to Block: A
            t4 = instance.run_until_instruction("Block", state="completed", arguments="A")
            t4_time = t4/10

            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(t1_time + t2_time + t3_time + t4_time, block_time.as_number(), delta=delta)

    def test_tag_block_time_restart(self):
        program = """\
Wait: 1s
Block: B1
    Wait: 2s
    End block
"""
        delta = 0.2
        runner = EngineTestRunner(create_test_uod, program)
        with runner.run() as instance:
            e = instance.engine
            instance.start()
            block_time = e.tags[SystemTagName.BLOCK_TIME]
            block = e.tags[SystemTagName.BLOCK]

            t1 = instance.run_until_instruction("Wait", state="completed", arguments="1s")
            t1_time = t1/10
            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(1, block_time.as_number(), delta=delta)

            t2 = instance.run_until_instruction("Block", state="started")
            t2_time = t2/10
            self.assertEqual("B1", block.get_value())
            self.assertAlmostEqual(0.0, block_time.as_number(), delta=delta)

            t3 = instance.run_until_instruction("Wait", state="completed", arguments="2s")
            t3_time = t3/10
            self.assertEqual("B1", block.get_value())
            self.assertAlmostEqual(2, block_time.as_number(), delta=delta)

            instance.index_step_back(2)
            t4 = instance.run_until_instruction("Block", state="completed")
            t4_time = t4/10
            self.assertEqual(None, block.get_value())
            # this is the important test for scope timers
            self.assertAlmostEqual(t1_time + t2_time + t3_time + t4_time, block_time.as_number(), delta=delta)

            instance.restart_and_run_until_started()
            self.assertAlmostEqual(0, block_time.as_number(), delta=delta)  # is reset after restart

            instance.index_step_back(1)
            instance.run_until_instruction("Wait", state="completed", arguments="1s")
            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(1, block_time.as_number(), delta=delta)

            instance.run_until_instruction("Block", state="started")
            self.assertEqual("B1", block.get_value())
            self.assertAlmostEqual(0, block_time.as_number(), delta=delta)  # is also reset after restart

    def test_tag_block_time_stop_start(self):
        program = """\
Wait: 1s
Block: B1
    Wait: 2s
    End block
"""
        delta = 0.2
        runner = EngineTestRunner(create_test_uod, program)
        with runner.run() as instance:
            e = instance.engine
            instance.start_run()
            block_time = e.tags[SystemTagName.BLOCK_TIME]
            block = e.tags[SystemTagName.BLOCK]

            t1 = instance.run_until_instruction("Wait", state="completed", arguments="1s")
            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(1, block_time.as_number(), delta=delta)

            t2 = instance.run_until_instruction("Block", state="started")
            self.assertEqual("B1", block.get_value())
            self.assertAlmostEqual(0, block_time.as_number(), delta=delta)

            instance.index_step_back(2)
            t3 = instance.run_until_instruction("Block", state="completed")
            self.assertEqual(None, block.get_value())
            duration = (t1+t2+t3)/10
            self.assertAlmostEqual(duration , block_time.as_number(), delta=delta)

            e.schedule_execution(EngineCommandEnum.STOP)
            instance.run_ticks(3)

            e.schedule_execution(EngineCommandEnum.START)
            instance.run_ticks(1)
            self.assertAlmostEqual(0, block_time.as_number(), delta=delta)  # is reset after restart

            instance.run_until_event("block_start")
            self.assertAlmostEqual(0, block_time.as_number(), delta=delta)  # nested timer is also reset

    def test_tag_block_time_pause(self):
        program = """\
Wait: 0.3s
Pause: 1s
Block: B1
    Wait: 0.4s
    Pause: 2s
    End block
Mark: A
"""
        delta = 0.2
        runner = EngineTestRunner(create_test_uod, program)
        with runner.run() as instance:
            e = instance.engine
            instance.start_run()
            run_time = e.tags[SystemTagName.RUN_TIME]
            block_time = e.tags[SystemTagName.BLOCK_TIME]
            block = e.tags[SystemTagName.BLOCK]

            t1 = instance.run_until_instruction("Pause", state="completed", arguments="1s")
            t1_time = t1/10
            # self.assertAlmostEqual(t1_time, 1.7, delta=delta)  # don't depend on this
            self.assertAlmostEqual(run_time.as_float(), t1_time, delta=delta)
            self.assertAlmostEqual(block_time.as_float(), t1_time - 1.0, delta=delta)

            t2 = instance.run_until_instruction("Block", state="started")
            t2_time = t2/10
            self.assertAlmostEqual(run_time.as_float(), t1_time + t2_time, delta=delta)
            self.assertEqual("B1", block.get_value())
            self.assertAlmostEqual(block_time.as_number(), 0, delta=delta)

            t3 = instance.run_until_instruction("Pause", state="completed", arguments="2s")
            t3_time = t3/10
            self.assertAlmostEqual(run_time.as_float(), t1_time + t2_time + t3_time, delta=delta)
            self.assertAlmostEqual(block_time.as_number(), t3_time - 2.0, delta=delta)

            t4 = instance.run_until_event("method_end")
            t4_time = t4/10
            self.assertAlmostEqual(run_time.as_float(), t1_time + t2_time + t3_time + t4_time, delta=delta)
            self.assertEqual(None, block.get_value())
            self.assertAlmostEqual(block_time.as_number(),
                                   t1_time - 1.0 + t3_time - 2.0 + t4_time,
                                   delta=delta)

    def test_tag_unit_conversion_handled_by_pint(self):
        program = """\
CmdWithRegexArgs: 2 L/h
CmdWithRegexArgs: 2 L/min
CmdWithRegexArgs: 2 L/s
"""
        runner = EngineTestRunner(create_test_uod, program)
        with runner.run() as instance:
            instance.start_run()

            flowrate = instance.engine.tags["CmdWithRegex_Flowrate"]  # [L/h]

            self.assertEqual(0.0, flowrate.get_value())

            instance.run_until_command("CmdWithRegexArgs", state="completed", arguments="2 L/h")
            self.assertEqual(2.0, flowrate.get_value())  # 2 L/h is 2 L/h

            instance.run_until_command("CmdWithRegexArgs", state="completed", arguments="2 L/min")
            self.assertEqual(120.0, flowrate.get_value())  # 2 L/min is 120 L/h

            instance.run_until_command("CmdWithRegexArgs", state="completed", arguments="2 L/s")
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

    def test_safe_values_are_written_on_stop(self):
        code = """\
Info: A
Stop
"""
        runner = EngineTestRunner(create_test_uod, code)
        with runner.run() as instance:
            instance.start()
            danger = instance.engine.tags["Danger"]
            instance.run_until_instruction("Info")
            danger.set_value(True, instance.engine._tick_time)

            instance.run_until_event("stop")
            self.assertEqual(danger.get_value(), False)

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


    # --- Totalizers ---

    # TODO remove - is unused
    def create_totalizer_uod(self) -> UnitOperationDefinitionBase:
        builder = (
            UodBuilder()
            .with_instrument("TestUod")
            .with_author("Test Author", "test@openpectus.org")
            .with_filename(__file__)
            .with_hardware(TestHW())
            .with_location("Test location")
            .with_hardware_register("FT01", RegisterDirection.Both, path="Objects;2:System;2:FT01")
            .with_hardware_register(
                "Reset",
                RegisterDirection.Both,
                path="Objects;2:System;2:RESET",
                from_tag=lambda x: 1 if x == "Reset" else 0,
                to_tag=lambda x: "Reset" if x == 1 else "N/A",
            )
            .with_hardware_register(
                "Danger",
                RegisterDirection.Write,
                path="Objects;2:System;2:Danger",
                safe_value=False,
            )
            # Readings
            .with_tag(ReadingTag("FT01", "L/h"))
            .with_tag(SelectTag("Reset", value="N/A", unit=None, choices=["Reset", "N/A"]))
            .with_tag(Tag("Danger", value=True, unit=None, direction=TagDirection.Output))
        )
        return builder.build()

    def test_totalizer_base_units_no_accumulator_allows_time_unit(self):
        runner = EngineTestRunner(self.create_test_uod, "Base: s\n0.1 Mark: A")
        with runner.run() as instance:
            instance.start_run()
            instance.run_ticks(5)
            method_status = instance.engine.tags[SystemTagName.METHOD_STATUS]
            self.assertEqual(method_status.get_value(), MethodStatusEnum.OK)

    def test_totalizer_base_units_no_accumulator_disallows_volume_unit(self):
        runner = EngineTestRunner(self.create_test_uod, "Base: L\n0.1 Mark: A", fail_on_log_error=False)
        with runner.run() as instance:
            instance.start_run()
            with self.assertRaises(EngineError):
                instance.run_ticks(5)
            method_status = instance.engine.tags[SystemTagName.METHOD_STATUS]
            self.assertEqual(method_status.get_value(), MethodStatusEnum.ERROR)

    def test_totalizer_base_units_with_accumulator_volume(self):
        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_author("Test Author", "test@openpectus.org")
               .with_filename(__file__)
               .with_hardware(TestHW(connected=True))
               .with_location("Test location")
               .with_tag(ReadingTag("Meter", "L"))
               .with_accumulated_volume(totalizer_tag_name="Meter")
               .build())

        with self.subTest("allows_time_unit"):
            runner = EngineTestRunner(uod, "Base: s\n0.1 Mark: A")
            with runner.run() as instance:
                instance.start_run()
                instance.run_ticks(5)
                method_status = instance.engine.tags[SystemTagName.METHOD_STATUS]
                self.assertEqual(method_status.get_value(), MethodStatusEnum.OK)

        with self.subTest("allows_volume_unit"):
            runner = EngineTestRunner(uod, "Base: L\n0.1 Mark: A")
            with runner.run() as instance:
                instance.start_run()
                instance.run_ticks(5)
                method_status = instance.engine.tags[SystemTagName.METHOD_STATUS]
                self.assertEqual(method_status.get_value(), MethodStatusEnum.OK)

        with self.subTest("disallows_cv_unit"):
            runner = EngineTestRunner(uod, "Base: CV\n0.1 Mark: A", fail_on_log_error=False)
            with runner.run() as instance:
                instance.start_run()
                with self.assertRaises(EngineError):
                    instance.run_ticks(5)
                method_status = instance.engine.tags[SystemTagName.METHOD_STATUS]
                self.assertEqual(method_status.get_value(), MethodStatusEnum.ERROR)

    def test_totalizer_base_units_with_accumulator_cv(self):
        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_author("Test Author", "test@openpectus.org")
               .with_filename(__file__)
               .with_hardware(TestHW(connected=True))
               .with_location("Test location")
               .with_tag(ReadingTag("Meter", "L"))
               .with_tag(ReadingTag("CV", "L"))
               .with_accumulated_cv(cv_tag_name="CV", totalizer_tag_name="Meter")
               .build())

        uod.tags["CV"].set_value(1.0, 0)

        with self.subTest("allows_time_unit"):
            runner = EngineTestRunner(uod, "Base: s\n0.1 Mark: A")
            with runner.run() as instance:
                instance.start_run()
                instance.run_ticks(5)
                method_status = instance.engine.tags[SystemTagName.METHOD_STATUS]
                self.assertEqual(method_status.get_value(), MethodStatusEnum.OK)

        with self.subTest("disallows_volume_unit"):
            runner = EngineTestRunner(uod, "Base: L\n0.1 Mark: A", fail_on_log_error=False)
            with runner.run() as instance:
                instance.start_run()
                with self.assertRaises(EngineError):
                    instance.run_ticks(5)
                method_status = instance.engine.tags[SystemTagName.METHOD_STATUS]
                self.assertEqual(method_status.get_value(), MethodStatusEnum.ERROR)

        with self.subTest("allows_cv_unit"):
            runner = EngineTestRunner(uod, "Base: CV\n0.1 Mark: A")
            with runner.run() as instance:
                instance.start_run()
                instance.run_ticks(5)
                method_status = instance.engine.tags[SystemTagName.METHOD_STATUS]
                self.assertEqual(method_status.get_value(), MethodStatusEnum.OK)

    def test_accumulated_volume(self):
        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_author("Test Author", "test@openpectus.org")
               .with_filename(__file__)
               .with_hardware(TestHW(connected=True))
               .with_location("Test location")
               .with_tag(CalculatedLinearTag("calc", "L"))
               .with_accumulated_volume(totalizer_tag_name="calc")
               .build())

        runner = EngineTestRunner(uod, "Base: s")
        with runner.run() as instance:
            instance.start_run()

            acc_vol = instance.engine.tags[SystemTagName.ACCUMULATED_VOLUME]
            self.assertEqual(acc_vol.as_float(), 0.0)
            self.assertEqual(acc_vol.unit, "L")

            t0 = instance.engine._clock.get_time()
            instance.run_ticks(10)
            t1 = instance.engine._clock.get_time()

            self.assertAlmostEqual(t1 - t0, 1, delta=0.05)
            self.assertAlmostEqual(acc_vol.as_float(), 1, delta=0.05)

    def test_accumulated_block_volume(self):
        delta = 0.15
        set_interpreter_debug_logging(include_events=True, include_runlog=True)

        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_author("Test Author", "test@openpectus.org")
               .with_filename(__file__)
               .with_hardware(TestHW(connected=True))
               .with_location("Test location")
               .with_tag(CalculatedLinearTag("calc", "L"))
               .with_accumulated_volume(totalizer_tag_name="calc")
               .build())

        program = """\
Base: s
Wait: 0.45s
Block: A
    0.85 End block
0.45 Mark: A
        """

        runner = EngineTestRunner(uod, program)
        with runner.run() as instance:
            instance.start_run()

            acc_vol = instance.engine.tags[SystemTagName.ACCUMULATED_VOLUME]
            block_vol = instance.engine.tags[SystemTagName.BLOCK_VOLUME]
            block = instance.engine.tags[SystemTagName.BLOCK]

            self.assertEqual(block.get_value(), None)
            self.assertEqual(acc_vol.as_float(), 0.0)
            self.assertEqual(acc_vol.unit, "L")
            self.assertEqual(block_vol.as_float(), 0.0)
            self.assertEqual(block_vol.unit, "L")

            t1 = instance.run_until_instruction("Wait", state="completed")
            # Note: the expected tag values here depends on the value used for initial_increment
            # t1_value = (t1 - 1)/10  # using initial_increment = 0
            t1_value = t1/10          # using initial_increment = interval (=0.1)
            print(f"{t1=} | {t1_value=}")

            self.assertEqual(block.get_value(), None)
            self.assertAlmostEqual(acc_vol.as_float(), t1_value, delta=delta)
            self.assertAlmostEqual(block_vol.as_float(), t1_value, delta=delta)

            t2 = instance.run_until_instruction("Block", state="started")
            t2_value = t2/10
            print(f"{t2=} | {t2_value=}")

            self.assertEqual(block.get_value(), "A")
            self.assertAlmostEqual(acc_vol.as_float(), t1_value + t2_value, delta=delta)
            self.assertAlmostEqual(block_vol.as_float(), t2_value, delta=delta)

            t3 = instance.run_ticks(5)  # just run a bit into the block
            assert t3 == 5
            t3_value = t3/10
            print(f"{t3=} | {t3_value=}")

            self.assertEqual(block.get_value(), "A")
            self.assertAlmostEqual(acc_vol.as_float(), t1_value + t2_value + t3_value, delta=delta)
            self.assertAlmostEqual(block_vol.as_float(), t2_value + t3_value, delta=delta)

            instance.index_step_back(2)
            t4 = instance.run_until_instruction("Block", state="completed")
            t4_value = t4/10
            print(f"{t4=} | {t4_value=}")

            self.assertEqual(block.get_value(), None)
            self.assertAlmostEqual(acc_vol.as_float(), t1_value + t2_value + t3_value + t4_value, delta=delta)
            # block_vol is reset to value before block A - so it matches acc_vol again
            self.assertAlmostEqual(block_vol.as_float(), t1_value + t2_value + t3_value + t4_value, delta=delta)

    def test_accumulated_column_volume(self):
        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_author("Test Author", "test@openpectus.org")
               .with_filename(__file__)
               .with_hardware(TestHW(connected=True))
               .with_location("Test location")
               .with_tag(ReadingTag("CV", "L"))
               .with_tag(CalculatedLinearTag("calc", "L"))
               .with_accumulated_cv(cv_tag_name="CV", totalizer_tag_name="calc")
               .build())

        program = """
Base: s
1 Mark: A
"""
        runner = EngineTestRunner(uod, program)
        with runner.run() as instance:
            instance.start_run()

            cv = instance.engine.tags["CV"]
            cv.set_value(2.0, 0)
            acc_cv = instance.engine.tags[SystemTagName.ACCUMULATED_CV]

            self.assertEqual(acc_cv.as_float(), 0.0)
            self.assertEqual(acc_cv.unit, "CV")


            t0 = instance.engine._clock.get_time()
            instance.run_ticks(10)
            t1 = instance.engine._clock.get_time()

            self.assertAlmostEqual(t1 - t0, 1, delta=0.1)
            self.assertAlmostEqual(acc_cv.as_float(), 1/2, delta=0.1)

    def test_accumulated_column_volume_base(self):
        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_author("Test Author", "test@openpectus.org")
               .with_filename(__file__)
               .with_hardware(TestHW(connected=True))
               .with_location("Test location")
               .with_tag(ReadingTag("CV", "L"))
               .with_tag(CalculatedLinearTag("calc", "L"))
               .with_accumulated_cv(cv_tag_name="CV", totalizer_tag_name="calc")
               .build())

        program = """
Base: CV
0.5 Mark: A
"""
        runner = EngineTestRunner(uod, program)
        with runner.run() as instance:
            instance.start_run()

            cv = instance.engine.tags["CV"]
            cv.set_value(2.0, 0)
            acc_cv = instance.engine.tags[SystemTagName.ACCUMULATED_CV]

            self.assertEqual(acc_cv.as_float(), 0.0)
            self.assertEqual(acc_cv.unit, "CV")

            instance.run_ticks(4)
            self.assertAlmostEqual(acc_cv.as_float(), 0.2, delta=0.1)
            self.assertEqual(instance.marks, [])

            # because base is column volume, the threshold has not yet passed

            instance.run_ticks(4)
            self.assertAlmostEqual(acc_cv.as_float(), 0.4, delta=0.1)
            self.assertEqual(instance.marks, [])

            # now it has

            instance.run_ticks(4)
            self.assertAlmostEqual(acc_cv.as_float(), 0.6, delta=0.1)
            self.assertEqual(instance.marks, ["A"])


    def test_accumulated_column_block_volume(self):
        # TODO flaky - still??        

        uod = (UodBuilder()
               .with_instrument("TestUod")
               .with_author("Test Author", "test@openpectus.org")
               .with_filename(__file__)
               .with_hardware(TestHW(connected=True))
               .with_location("Test location")
               .with_tag(ReadingTag("CV", "L"))
               .with_tag(CalculatedLinearTag("calc", "L"))
               .with_accumulated_cv(cv_tag_name="CV", totalizer_tag_name="calc")
               .build())

        program = """\
Base: s
Block: A
    0.5 Mark: A
    End block
Mark: B
        """
        runner = EngineTestRunner(uod, program)
        with runner.run() as instance:
            instance.start_run()

            cv = instance.engine.tags["CV"]
            cv.set_value(2.0, 0)
            acc_cv = instance.engine.tags[SystemTagName.ACCUMULATED_CV]
            block_cv = instance.engine.tags[SystemTagName.BLOCK_CV]
            block = instance.engine.tags[SystemTagName.BLOCK]

            self.assertEqual(acc_cv.as_float(), 0.0)
            self.assertEqual(acc_cv.unit, "CV")
            self.assertEqual(block_cv.as_float(), 0.0)
            self.assertEqual(block_cv.unit, "CV")

            t1 = instance.run_until_instruction("Base")
            t1_value = t1/10/2
            self.assertEqual(block.get_value(), None)
            self.assertAlmostEqual(acc_cv.as_float(), t1_value, delta=0.1)
            self.assertAlmostEqual(block_cv.as_float(), t1_value, delta=0.1)

            t2 = instance.run_until_instruction("Block", state="started")
            t2_value = t2/10/2
            self.assertEqual(block.get_value(), "A")
            self.assertAlmostEqual(acc_cv.as_float(), t1_value + t2_value, delta=0.1)
            self.assertAlmostEqual(block_cv.as_float(), t2_value, delta=0.1)

            t3 = instance.run_until_instruction("Mark", state="started", arguments="A")
            t3_value = t3/10/2
            self.assertEqual(block.get_value(), "A")
            self.assertAlmostEqual(acc_cv.as_float(), t1_value + t2_value + t3_value, delta=0.1)
            self.assertAlmostEqual(block_cv.as_float(), t2_value + t3_value, delta=0.1)

            t4 = instance.run_until_instruction("Mark", arguments="B")
            t4_value = t4/10/2
            self.assertEqual(block.get_value(), None)
            self.assertAlmostEqual(acc_cv.as_float(), t1_value + t2_value + t3_value + t4_value, delta=0.1)
            self.assertAlmostEqual(block_cv.as_float(), t1_value + t2_value + t3_value + t4_value, delta=0.1)


    def test_accumulated_column_volume_watch(self):
        program = """
Base: CV
Watch: Accumulated CV > 0.5 CV
    Mark: A
"""
        runner = EngineTestRunner(self.create_test_uod, program)
        with runner.run() as instance:
            instance.start_run()
            instance.run_until_instruction("Base", state="completed")

            multiplier = 3.0
            cv = instance.engine.tags["CV"]
            cv.set_value(multiplier, 0)
            acc_cv = instance.engine.tags[SystemTagName.ACCUMULATED_CV]
            self.assertEqual(acc_cv.as_float(), 0.0)
            self.assertEqual(acc_cv.unit, "CV")

            elapsed = instance.run_until_instruction("Mark", state="started")
            self.assertAlmostEqual(5 * multiplier, elapsed, delta=1)


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
