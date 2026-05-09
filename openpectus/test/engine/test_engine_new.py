import os
import time
import unittest
from typing import Any
from openpectus.aggregator.models import SystemStateEnum
from openpectus.lang.exec.regex import RegexNumber
from openpectus.lang.exec.tags_impl import ReadingTag, SelectTag
from openpectus.engine.hardware import RegisterDirection

import pint
from openpectus.lang.exec.tags import SystemTagName, Tag, TagDirection
from openpectus.lang.exec.uod import UnitOperationDefinitionBase, UodCommand, UodBuilder
from openpectus.test.engine.utility_methods import (
    EngineTestRunner,
    configure_test_logger,
    set_engine_debug_logging, set_interpreter_debug_logging
)


configure_test_logger()
set_engine_debug_logging()
set_interpreter_debug_logging()

# pint takes forever to initialize - long enough
# to throw off timing of the first instruction.
# so we initialize it first
_ = pint.Quantity("0 s")


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
        .with_tag(Tag("CmdWithRegex_Area", value=""))
        .with_command_regex_arguments(
            name="CmdWithRegexArgs",
            arg_parse_regex=RegexNumber(units=['m2']),
            exec_fn=cmd_regex)
    )
    uod = builder.build()
    uod.hwl.connect()
    return uod

class TestRunnerTest(unittest.TestCase):

    def test_run_ticks_wo_start_run(self):
        delta = 0.05
        runner = EngineTestRunner(create_test_uod)
        with runner.run() as instance:
            run_time = instance.engine.tags[SystemTagName.RUN_TIME]

            # demonstrates the rationality for the start_run() method that is also exposed as run(autostart=True)
            instance.start()
            self.assertEqual(instance.engine._tick_number, -1)
            instance.run_ticks(1)
            self.assertEqual(instance.engine._tick_number, 0)
            self.assertEqual(run_time.as_float(), 0.0)

            # from here, everything is ready
            tick_0 = instance.engine._tick_number
            t0 = time.time()
            reported_ticks = instance.run_ticks(10)
            tick_1 = instance.engine._tick_number
            t1 = time.time()

            self.assertEqual(reported_ticks, 10)
            self.assertAlmostEqual(t1 - t0, 1.0, delta=delta)
            self.assertEqual(tick_1 - tick_0, 10)

            # this depends on using interval as initial increment rather than 0
            self.assertAlmostEqual(run_time.as_float(), 1.0, delta=delta)

    def test_run_ticks(self):
        delta = 0.05
        runner = EngineTestRunner(create_test_uod)
        with runner.run() as instance:
            run_time = instance.engine.tags[SystemTagName.RUN_TIME]
            instance.start_run()

            tick_0 = instance.engine._tick_number
            t0 = time.time()
            reported_ticks = instance.run_ticks(10)
            tick_1 = instance.engine._tick_number
            t1 = time.time()

            self.assertEqual(reported_ticks, 10)
            self.assertAlmostEqual(t1 - t0, 1.0, delta=delta)
            self.assertEqual(tick_1 - tick_0, 10)

            # this depends on using interval as initial increment rather than 0
            self.assertAlmostEqual(run_time.as_float(), 1.0, delta=delta)
            print("run_time", run_time.as_float())

    @unittest.skipIf(bool(os.environ.get("OPENPECTUS_ENGINE_SKIP_SLOW_TESTS")), reason="Skipping slow tests as configured")
    def test_run_ticks_100(self):
        delta = 0.05
        tick_count = 100
        runner = EngineTestRunner(create_test_uod)
        with runner.run() as instance:
            run_time = instance.engine.tags[SystemTagName.RUN_TIME]
            instance.start_run()

            tick_0 = instance.engine._tick_number
            t0 = time.time()
            reported_ticks = instance.run_ticks(tick_count)
            tick_1 = instance.engine._tick_number
            t1 = time.time()

            duration = tick_count * 0.1

            self.assertEqual(reported_ticks, tick_count)
            self.assertAlmostEqual(t1 - t0, duration, delta=delta)
            self.assertEqual(tick_1 - tick_0, tick_count)

            # this depends on using interval as initial increment rather than 0
            self.assertAlmostEqual(run_time.as_float(), duration, delta=delta)

    # TODO
    def test_initial_increment(self):
        # test relevant cases for the initial value of increment
        # on start
        # after each pause
        # timer when entering its scope
        raise NotImplementedError()

    def test_run_until_condition(self):
        runner = EngineTestRunner(create_test_uod)
        with runner.run() as instance:
            run_time = instance.engine.tags[SystemTagName.RUN_TIME]
            instance.start_run()

            start = time.time()
            instance.run_until_condition(lambda: run_time.as_float() >= 5, max_ticks=60)
            end = time.time()
            self.assertAlmostEqual(end-start, 5, delta=0.2)

    def test_run_until_condition2(self):
        runner = EngineTestRunner(create_test_uod)
        with runner.run() as instance:
            instance.start_run()

            tick_0 = instance.engine._tick_number
            time_0 = time.time()

            reported_ticks = instance.run_until_condition(
                lambda: instance.engine._tick_number == 10,
                max_ticks=20)

            tick_1 = instance.engine._tick_number
            time_1 = time.time()

            self.assertEqual(reported_ticks, 10)
            self.assertAlmostEqual(time_1 - time_0, 1.1, delta=0.1)
            self.assertEqual(tick_1 - tick_0, 10)

class TestEngineNew(unittest.TestCase):


    def test_wait(self):
        code = """
Wait: 1s
"""
        runner = EngineTestRunner(create_test_uod, code)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Wait", "started", increment_index=False)
            ticks = instance.run_until_instruction("Wait", "completed")
            self.assertAlmostEqual(10, ticks, delta=2)

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

            instance.run_until_instruction("Mark")
            instance.run_until_instruction("Pause")
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
            # self.assertEqual(2, run_counter.as_number())

            instance.run_until_event("start")
            instance.run_until_instruction("Watch")

            print(instance.get_runtime_table("B"))

            # not sure about this
            # with self.assertRaises(TimeoutError):
            #     instance.run_until_instruction("Restart")

            print(instance.get_runtime_table("C"))


    # --- Restart ---


    def test_restart_can_restart(self):
        set_engine_debug_logging()
        set_interpreter_debug_logging()
        code = """\
Mark: A
Increment run counter
Restart
"""
        runner = EngineTestRunner(create_test_uod, code)

        with runner.run() as instance:
            sys_state = instance.engine.tags[SystemTagName.SYSTEM_STATE]
            run_counter = instance.engine.tags[SystemTagName.RUN_COUNTER]
            run_id = instance.engine.tags[SystemTagName.RUN_ID]
            instance.start()

            instance.run_until_condition(lambda : sys_state.get_value() == SystemStateEnum.Restarting)
            run_id_1 = run_id.get_value()
            self.assertIsNotNone(run_id.get_value())
            self.assertEqual(["A"], instance.marks)
            self.assertEqual(1, run_counter.as_number())

            instance.run_until_condition(lambda : sys_state.get_value() == SystemStateEnum.Stopped)
            self.assertIsNone(run_id.get_value())
            self.assertEqual([], instance.marks)
            self.assertEqual(1, run_counter.as_number())

            instance.run_until_condition(lambda : sys_state.get_value() == SystemStateEnum.Running)
            run_id_2 = run_id.get_value()
            self.assertIsNotNone(run_id_2)
            self.assertNotEqual(run_id_1, run_id_2)
            self.assertEqual([], instance.marks)
            self.assertEqual(1, run_counter.as_number())

            instance.run_until_instruction("Increment run counter", state="completed")
            self.assertEqual(["A"], instance.marks)
            self.assertEqual(2, run_counter.as_number())

    def test_restart_cancels_running_commands(self):
        set_engine_debug_logging()

        code1 = """\
Reset
"""
        code2 = """\
Reset
Restart
"""
        reset_ticks = 0
        runner = EngineTestRunner(create_test_uod, code1)
        with runner.run() as instance:
            instance.start_run()

            instance.index_step_back(1)
            reset_ticks = instance.run_until_command("Reset", state="completed")
            instance.logger.info(f"Reset ticks: {reset_ticks}")

        # verify that total duration is faster than reset_ticks - because command is cancelled
        runner = EngineTestRunner(create_test_uod, code2)
        with runner.run() as instance:
            instance.start_run()

            total_ticks = instance.run_until_instruction("Restart")
            instance.logger.info(f"Total ticks: {total_ticks}")
            self.assertLess(total_ticks, reset_ticks)

    def test_restart_can_stop(self):
        set_engine_debug_logging()
        set_interpreter_debug_logging()
        code = """
Mark: A
Restart
"""
        runner = EngineTestRunner(create_test_uod, code)
        with runner.run() as instance:
            sys_state = instance.engine.tags[SystemTagName.SYSTEM_STATE]
            instance.start()
            instance.run_until_condition(lambda: sys_state.get_value() == SystemStateEnum.Restarting)
            instance.run_until_condition(lambda: sys_state.get_value() == SystemStateEnum.Stopped)

    def test_mark_in_alarm_body_runs_in_each_alarm_instance(self):
        code = """
Alarm: Block Time > 0s
    Mark: A
    Wait: 0.5s
"""
        runner = EngineTestRunner(create_test_uod, code)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Alarm", "started")

            # print(instance.get_runtime_table("start"))
            # print_runtime_records(instance.engine, "A")

            instance.run_until_instruction("Mark", "completed")
            self.assertEqual(['A'], instance.marks)
            # print_runtime_records_alt(instance.engine, "B")

            instance.run_until_condition(lambda : instance.marks == ['A', 'A'])
            # print_runtime_records_alt(instance.engine, "C")

            instance.run_until_condition(lambda : instance.marks == ['A', 'A', 'A'])
            # print_runtime_records_alt(instance.engine, "D")
            # print_runlog(instance.engine)

    def test_watch_in_alarm_body_runs_in_each_alarm_instance(self):
        code = """
Alarm: Block Time > 0s
    Watch: Block Time > 0.5s
        Mark: A
    Wait: 0.5s
"""
        runner = EngineTestRunner(create_test_uod, code)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Alarm", "started")

            print(instance.get_runtime_table("start"))

            instance.run_until_instruction("Mark", "completed")
            self.assertEqual(['A'], instance.marks)

            instance.run_until_condition(lambda : instance.marks == ['A', 'A'])

            # This does not work because the alarm node is way up in the record list.
            # we would need aonther way to wait for alarm, including a new find_instruction
            # variant that locates the alarm record at indexes the states in there instead
            # of the normal one that indexes full records.
            # the same goes for any other node inside the alarm body
            # instance.run_until_instruction("Alarm", "started")

    def test_run_until_method_end(self):
        code = """
Mark: A
Mark: B
Mark: C
"""
        runner = EngineTestRunner(create_test_uod, code)

        with runner.run() as instance:
            instance.start()
            self.assertEqual([], instance.marks)
            instance.run_until_event("method_end")
            self.assertEqual(['A', 'B', 'C'], instance.engine.interpreter.get_marks())


    def test_run_until_stop(self):
        code = """
Mark: A
Stop
"""
        runner = EngineTestRunner(create_test_uod, code)

        with runner.run() as instance:
            instance.start()
            instance.run_until_event("stop")
            self.assertEqual([], instance.marks)


    @unittest.skip("speed > 1 not implemented")
    def test_speed_perceived(self):
        pcode = """
Base: s
Mark: A
Wait: 15s
15 Mark: A2
Mark: B
"""
        runner = EngineTestRunner(create_test_uod, pcode, speed=30)
        with runner.run() as instance:
            instance.start()
            run_time = instance.engine.tags[SystemTagName.RUN_TIME]
            time.sleep(1)
            self.assertAlmostEqual(run_time.as_float(), 30, delta=3)

            time.sleep(1)
            self.assertAlmostEqual(run_time.as_float(), 60, delta=3)

    @unittest.skip("speed > 1 not implemented")
    def test_speed_timer(self):
        pcode = """
Wait: 30s
Mark: B
"""
        runner = EngineTestRunner(create_test_uod, pcode, speed=30)
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

# --- Inject ---


    def test_inject_command(self):
        pcode = """
Mark: A
Mark: B
Mark: C
"""
        runner = EngineTestRunner(create_test_uod, pcode)
        with runner.run() as instance:
            instance.start()
            instance.run_until_instruction("Mark", state="completed")
            self.assertEqual(['A'], instance.marks)

            instance.engine.inject_code("Mark: I")

#            instance.run_until_condition(lambda: 'B' in instance.marks)
            instance.run_until_instruction("Mark", state="completed")

            instance.run_until_event("method_end")
            self.assertIn(instance.marks, [['A', 'B', 'I', 'C'], ['A', 'B', 'C', 'I']])


    def test_inject_thresholds_1(self):
        pcode = """
Mark: A
0.25 Mark: B
Mark: C
"""
        runner = EngineTestRunner(create_test_uod, pcode)
        with runner.run() as instance:
            instance.start()

            instance.engine.tags[SystemTagName.BASE].set_value("s", instance.engine._tick_time)

            instance.run_until_instruction("Mark", state="completed", arguments="A")
            self.assertEqual(['A'], instance.marks)

            instance.engine.inject_code("Mark: I")
            instance.run_until_event("method_end")
            self.assertIn(instance.marks, (['A', 'B', 'I', 'C'], ['A', 'I', 'B', 'C']))


    def test_inject_thresholds_2(self):
        pcode = """
Mark: A
0.2 Mark: B
Mark: C
"""
        runner = EngineTestRunner(create_test_uod, pcode)
        with runner.run() as instance:
            instance.start()

            instance.engine.tags[SystemTagName.BASE].set_value("s", instance.engine._tick_time)

            instance.run_until_instruction("Mark", state="completed", arguments="A")
            self.assertEqual(['A'], instance.marks)

            instance.engine.inject_code("0.4 Mark: I")
            instance.run_until_condition(lambda: 'B' in instance.marks)
            self.assertEqual(instance.marks, ['A', 'B'])

            instance.run_until_event("method_end")
            self.assertIn(instance.marks, [['A', 'B', 'C', 'I'], ['A', 'B', 'I', 'C']])

    def test_info_warning_error(self):
        pcode = """
Info: foo
Warning: bar
Error: baz
Stop
"""
        runner = EngineTestRunner(create_test_uod, pcode, fail_on_log_error=False)
        with runner.run() as instance:
            instance.start()
            instance.run_until_event("stop")  # will raise on engine error
