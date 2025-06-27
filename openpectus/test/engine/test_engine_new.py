import time
import unittest
from typing import Any
from openpectus.lang.exec.regex import RegexNumber
from openpectus.lang.exec.tags_impl import ReadingTag, SelectTag
from openpectus.engine.hardware import RegisterDirection

import pint
from openpectus.lang.exec.tags import SystemTagName, Tag, TagDirection
from openpectus.lang.exec.uod import UnitOperationDefinitionBase, UodCommand, UodBuilder
from openpectus.test.engine.utility_methods import (
    EngineTestRunner,
    configure_test_logger, set_engine_debug_logging, set_interpreter_debug_logging
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
        # Readings
        .with_tag(ReadingTag("FT01", "L/h"))
        .with_tag(SelectTag("Reset", value="N/A", unit=None, choices=["Reset", "N/A"]))
        .with_tag(Tag("Danger", value=True, unit=None, direction=TagDirection.Output, safe_value=False))
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


#     def test_restart_can_restart(self):
#         set_engine_debug_logging()
#         set_interpreter_debug_logging()
#         program = """
# Mark: A
# Increment run counter
# Restart
# """
#         e = self.engine
#         self.assertEqual(0, e.tags[SystemTagName.RUN_COUNTER].as_number())

#         run_engine(e, program, start_ticks + 2)

#         run_id_1 = e.tags[SystemTagName.RUN_ID].get_value()
#         self.assertEqual(e.tags[SystemTagName.SYSTEM_STATE].get_value(), SystemStateEnum.Restarting)
#         self.assertEqual(1, e.tags[SystemTagName.RUN_COUNTER].as_number())

#         self.assertEqual(e.interpreter.get_marks(), ["A"])

#         continue_engine(e, 1)

#         self.assertEqual(e.tags[SystemTagName.SYSTEM_STATE].get_value(), SystemStateEnum.Stopped)
#         self.assertIsNone(e.tags[SystemTagName.RUN_ID].get_value())
#         self.assertEqual(e.interpreter.get_marks(), [])
#         self.assertEqual(1, e.tags[SystemTagName.RUN_COUNTER].as_number())

#         continue_engine(e, 1)

#         run_id2 = e.tags[SystemTagName.RUN_ID].get_value()
#         self.assertEqual(e.tags[SystemTagName.SYSTEM_STATE].get_value(), SystemStateEnum.Running)
#         self.assertNotEqual(run_id_1, run_id2)
#         self.assertEqual(e.interpreter.get_marks(), [])
#         self.assertEqual(1, e.tags[SystemTagName.RUN_COUNTER].as_number())

#         continue_engine(e, 3)

#         self.assertEqual(e.interpreter.get_marks(), ["A"])
#         self.assertEqual(2, e.tags[SystemTagName.RUN_COUNTER].as_number())

#     def test_restart_stop_ticking_interpreter(self):

#         set_interpreter_debug_logging()
#         program = """
# Mark: A
# Restart
# Mark: X
# """
#         e = self.engine
#         run_engine(e, program, 1)

#         for _ in range(30):
#             continue_engine(e, 1)
#             self.assertTrue("X" not in e.interpreter.get_marks())

#     def test_restart_cancels_running_commands(self):
#         program = """
# Reset
# Restart
# """
#         e = self.engine
#         run_engine(e, program, start_ticks + 1)

#         system_state = e.tags[SystemTagName.SYSTEM_STATE]
#         self.assertEqual(system_state.get_value(), SystemStateEnum.Restarting)

#     def test_restart_can_stop(self):
#         set_engine_debug_logging()
#         set_interpreter_debug_logging()
#         program = """
# Mark: A
# Restart
# """
#         e = self.engine
#         run_engine(e, program, start_ticks + 1)

#         # when no commands need to be stopped, restart immediately moves to Stopped
#         system_state = e.tags[SystemTagName.SYSTEM_STATE]
#         self.assertEqual(system_state.get_value(), SystemStateEnum.Restarting)



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

            instance.run_until_instruction("Mark", "completed")
            self.assertEqual(['A'], instance.marks)

            # instance.run_until_event("method_end")
            # instance.run_until_event("method_end")
            # self.assertEqual(['A', 'A'], instance.marks)


            instance.run_until_condition(lambda : instance.marks == ['A', 'A'])
            instance.run_until_condition(lambda : instance.marks == ['A', 'A', 'A'])

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
            self.assertEqual(instance.marks, ['A', 'B', 'C', 'I'])

    def test_info_warning_error(self):
        pcode = """
Info: foo
Warning: bar
Error: baz
Stop
"""
        runner = EngineTestRunner(create_test_uod, pcode)
        with runner.run() as instance:
            instance.start()
            instance.run_until_event("stop")  # will raise on engine error
