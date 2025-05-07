import logging
import time
import unittest

import pint
from openpectus.engine.engine import Engine, EngineTiming
from openpectus.engine.models import EngineCommandEnum
from openpectus.lang.exec.clock import WallClock
from openpectus.lang.exec.errors import EngineError
from openpectus.lang.exec.pinterpreter import PInterpreter
from openpectus.lang.exec.tags import Tag, SystemTagName
from openpectus.lang.exec.timer import NullTimer
from openpectus.lang.exec.uod import UnitOperationDefinitionBase, UodBuilder, UodCommand
from openpectus.lang.grammar.pprogramformatter import print_parsed_program as print_program
import openpectus.lang.model.ast as p
from openpectus.lang.model.parser import PcodeParser
from openpectus.test.engine.utility_methods import (
    continue_engine, run_engine, build_program,
    configure_test_logger, set_engine_debug_logging, set_interpreter_debug_logging,
    print_runlog
)


configure_test_logger()
set_engine_debug_logging()
set_interpreter_debug_logging()


# pint takes forever to initialize - long enough
# to throw off timing of the first instruction.
# so we initialize it first
_ = pint.Quantity("0 sec")


def create_test_uod() -> UnitOperationDefinitionBase:
    def incr_counter(cmd: UodCommand, **kvargs):
        counter = cmd.context.tags["counter"]
        count = counter.as_number()
        count = count + 1
        counter.set_value(count, time.time())
        cmd.set_complete()

    return (
        UodBuilder()
        .with_instrument("TestUod")
        .with_author("Test Author", "test@openpectus.org")
        .with_filename(__file__)
        .with_hardware_none()
        .with_location("Test location")
        # Readings
        .with_tag(Tag(name="counter", value=0))
        .with_command(name="incr counter", exec_fn=incr_counter)
        .build()
    )


def create_engine(uod: UnitOperationDefinitionBase | None = None) -> Engine:
    if uod is None:
        uod = create_test_uod()
    e = Engine(uod, EngineTiming(WallClock(), NullTimer(), 0.1, 1.0))
    return e


def create_interpreter(
        program: p.ProgramNode,
        uod: UnitOperationDefinitionBase | None = None):
    # create interpreter without engine - for non-command programs

    if uod is None:
        uod = create_test_uod()

    engine = create_engine(uod)

    return PInterpreter(program, engine)


def run_interpreter(interpreter: PInterpreter, max_ticks: int = -1):
    print("Interpretation started")
    ticks = 0
    max_ticks = max_ticks
    interpreter.running = True

    while interpreter.running:
        ticks += 1
        if max_ticks != -1 and ticks > max_ticks:
            print(f"Stopping because max_ticks {max_ticks} was reached")
            interpreter.running = False
            return

        time.sleep(0.1)
        tick_time = time.time()
        interpreter.tick(tick_time, ticks)


class InterpreterTest(unittest.TestCase):

    def setUp(self):
        self.engine: Engine = create_engine()

    def tearDown(self):
        self.engine.cleanup()

    def test_sequential_marks(self):
        program = """
Mark: a
Mark: b
Mark: c
"""
        print_program(program)
        engine = self.engine
        run_engine(engine, program, 10)

        self.assertEqual(["a", "b", "c"], engine.interpreter.get_marks())

    def test_command_incr_counter(self):
        program = """
Mark: a
incr counter
"""
        print_program(program)
        engine = self.engine

        self.assertEqual(0, engine.uod.tags["counter"].as_number())

        run_engine(engine, program, 10)

        self.assertEqual(1, engine.uod.tags["counter"].as_number())
        self.assertEqual("a", engine.interpreter.get_marks()[0])

    def test_command_Increment_run_counter(self):
        # same as test_command_incr_counter() but using builtin system tag and command rather than uod variant.
        program = """
Mark: a
Increment run counter
"""
        print_program(program)
        engine = self.engine

        self.assertEqual(0, engine.tags[SystemTagName.RUN_COUNTER].as_number())

        run_engine(engine, program, 5)

        self.assertEqual(1, engine.tags[SystemTagName.RUN_COUNTER].as_number())
        self.assertEqual(["a"], engine.interpreter.get_marks())

    def test_command_Run_counter(self):
        program = "Run counter: 3"
        engine = self.engine

        self.assertEqual(0, engine.tags[SystemTagName.RUN_COUNTER].as_number())

        run_engine(engine, program, 5)

        self.assertEqual(3, engine.tags[SystemTagName.RUN_COUNTER].as_number())

    @unittest.skip("TODO")
    def test_condition_with_invalid_tag_fails(self):
        raise NotImplementedError()

    def test_watch_can_evaluate_tag(self):
        program = """
Mark: a
Watch: counter > 0
    Mark: b
Mark: c
incr counter
Watch: counter > 0
    Mark: d
"""
        engine = self.engine
        run_engine(engine, program, 15)

        self.assertEqual(["a", "c", "b", "d"], engine.interpreter.get_marks())
        # Note that first watch is also activated and its body executed
        # even though it is not activated when first run. This represents the
        # interrupt nature of watches and alarms. So the behavior is not like this:
        # self.assertEqual(["a", "c", "d"], i.get_marks())


    def test_macro(self):
        program = """
Mark: a
Macro: A
    Mark: b
    Mark: c
Macro: B
    Mark: d
    Mark: e
"""
        engine = self.engine
        run_engine(engine, program, 5)
        self.assertEqual(["a",], engine.interpreter.get_marks())


    def test_macro_with_call(self):
        program = """
Mark: a
Macro: A
    Mark: b
    Mark: c
Macro: B
    Mark: d
    Mark: e
Call macro: A
"""
        engine = self.engine
        run_engine(engine, program, 10)
        self.assertEqual(["a", "b", "c",], engine.interpreter.get_marks())


    def test_macro_with_multiple_calls(self):
        program = """
Mark: a
Macro: A
    Mark: b
    Mark: c
Macro: B
    Mark: d
    Mark: e
Call macro: A
Call macro: A
"""
        engine = self.engine
        run_engine(engine, program, 10)
        self.assertEqual(["a", "b", "c", "b", "c",], engine.interpreter.get_marks())


    def test_call_undefined_macro(self):
        program = """
Mark: a
Macro: B
    Mark: b
Call macro: A
"""
        engine = self.engine

        with self.assertRaises(EngineError):
            run_engine(engine, program, 5)
        self.assertEqual(["a",], engine.interpreter.get_marks())


    def test_macro_with_nested_calls(self):
        program = """
Mark: a
Macro: A
    Mark: b
    Mark: c
Macro: B
    Mark: d
    Call macro: A
Call macro: B
"""
        engine = self.engine
        run_engine(engine, program, 10)
        self.assertEqual(["a", "d", "b", "c",], engine.interpreter.get_marks())


    def test_call_cascading_macro(self):
        program = """
Mark: a
Macro: A
    Mark: b
    Mark: c
    Call macro: A
Call macro: A
"""
        engine = self.engine

        with self.assertRaises(EngineError):
            run_engine(engine, program, 10)
        self.assertEqual(["a",], engine.interpreter.get_marks())


    def test_call_indirect_cascading_macro(self):
        program = """
Mark: a
Macro: A
    Mark: b
    Mark: c
    Call macro: B
Macro: B
    Mark: d
    Call macro: A
Call macro: A
"""
        engine = self.engine

        with self.assertRaises(EngineError):
            run_engine(engine, program, 10)
        self.assertEqual(["a",], engine.interpreter.get_marks())


    def test_call_multiple_indirect_cascading_macro(self):
        program = """
Mark: a
Macro: A
    Mark: b
    Mark: c
    Call macro: B
Macro: B
    Mark: d
    Call macro: C
Macro: C
    Mark: e
    Call macro: A
Call macro: A
"""
        engine = self.engine

        with self.assertRaises(EngineError):
            run_engine(engine, program, 10)
        self.assertEqual(["a",], engine.interpreter.get_marks())

# --- Conditions ---


    def test_evaluate(self):
        self.engine.interpreter.context.tags.add(Tag("X", value=9, unit="%"))

        parent = p.ProgramNode()
        watch = p.WatchNode()
        parent.append_child(watch)
        watch.condition = p.Condition()
        watch.arguments_part = "X > 10%"
        PcodeParser._parse_condition(watch)

        result = self.engine.interpreter._evaluate_condition(watch)
        self.assertEqual(result, False)

    def test_watch_nested(self):
        program = """
Mark: a
Watch: counter > 0
    Mark: b
    Watch: counter > 1
        Mark: e
Mark: c
incr counter
incr counter
Watch: counter > 0
    Mark: d
"""
        engine = self.engine
        run_engine(engine, program, 15)

        # TODO abgiguous ...
        # self.assertEqual(["a", "c", "b", "e", "d"], engine.interpreter.get_marks())
        self.assertEqual(["a", "c", "b", "d", "e"], engine.interpreter.get_marks())

    def test_watch_restart(self):
        program = """
Mark: a
Watch: counter > 0
    Mark: b
Mark: c
incr counter
"""
        engine = self.engine
        run_engine(engine, program, 15)
        self.assertEqual(["a", "c", "b"], engine.interpreter.get_marks())

        engine.schedule_execution(EngineCommandEnum.STOP)
        continue_engine(engine, 5)

        # rerun program and assert "same" result
        engine.schedule_execution(EngineCommandEnum.START)
        continue_engine(engine, 15)
        self.assertEqual(["a", "c", "b"], engine.interpreter.get_marks())

    def test_watch_long_running_order(self):
        # specify order of highly overlapping instructions
        # between main program and a single interrupt handler
        program = """
Mark: a
Watch: Run Counter > -1
    Mark: a1
    Mark: a2
    Mark: a3
Mark: b
Mark: b1
Mark: b2
Mark: b3
"""
        engine = self.engine
        run_engine(engine, program, 10)

        self.assertEqual(["a", "b", "a1", "b1", "a2", "b2", "a3", "b3"], engine.interpreter.get_marks())

    @unittest.skip("Block in Watch not supported")
    def test_watch_block_long_running_block_time(self):
        # question for another test: is Block time defined for alarm without block? Yes

        # specify block time for block in interrupt handler

        program = """
Mark: a
Watch: Run counter > -1
    Block: A
        Mark: a1
        Watch: Block Time > 0.5 sec
            Mark: a2
        Watch: Block Time > 1.0 sec
            Mark: a3
        Watch: Block Time > 1.2 sec
            Mark: a32
        Watch: Block Time > 1.3 sec
            Mark: a33
        Watch: Block Time > 1.4 sec
            Mark: a34
        Watch: Block Time > 1.5 sec
            Mark: a4
            End block
Mark: b
"""
        print_program(program)
        engine = self.engine
        run_engine(engine, program, 15)

        self.assertEqual(["a", "b", "a1", "a2", "a3", "a4"], engine.interpreter.get_marks())

    def test_alarm_triggers_by_condition(self):
        program = """
Mark: a
Alarm: counter > 0
    Mark: b
Mark: c
incr counter
Mark: d
"""
        engine = self.engine
        run_engine(engine, program, 15)

        marks = engine.interpreter.get_marks()

        # most important
        self.assertEqual(["a", "c"], marks[:2])
        # also important but specific order is really an implementation detail
        self.assertTrue(marks[:4] == ["a", "c", "d", "b"] or marks[:4] == ["a", "c", "b", "d"])

    def test_alarm_can_retrigger(self):
        program = """
Mark: a
Alarm: counter > 0
    Mark: b
Mark: c
incr counter
Mark: d
Mark: e
Mark: f
"""
        engine = self.engine

        logger = logging.getLogger("openpectus.lang.exec.pinterpreter")
        logger.setLevel(logging.DEBUG)

        run_engine(engine, program, 15)

        print_runlog(engine)
        # print_runtime_records(engine)

        marks = engine.interpreter.get_marks()
        # most important
        self.assertEqual(["a", "c"], marks[:2])
        # least important - exact ordering is an implementation
        self.assertGreaterEqual(marks.count("b"), 2)

    def test_block(self):
        program = """
Block: A
    Mark: A1
    End block
    Mark: A2
Mark: A3
"""
        engine = self.engine
        run_engine(engine, program, 10)

        self.assertEqual(["A1", "A3"], engine.interpreter.get_marks())

    def test_block_nested(self):
        program = """
Block: A
    Mark: A1
    Block: B
        Mark: B1
        End block
        Mark: B2
    End block
    Mark: A2
Mark: A3
"""
        engine = self.engine
        run_engine(engine, program, 15)

        self.assertEqual(["A1", "B1", "A3"], engine.interpreter.get_marks())

    def test_block_unterminated(self):
        program = """
Block: A
    Mark: A1
    Mark: A2
Mark: A3
"""
        engine = self.engine
        run_engine(engine, program, 6)

        self.assertEqual(["A1", "A2"], engine.interpreter.get_marks())

    def test_block_time_watch(self):
        program = """
Block: A
    Mark: A1
    Watch: Block Time > 1 s
        End block
    Mark: A2
Mark: A3
"""
        engine = self.engine
        run_engine(engine, program, 20)

        self.assertEqual(["A1", "A2", "A3"], engine.interpreter.get_marks())


    def test_block_time_watch_complex(self):
        program = """
Block: A
    Mark: A1
    Watch: Block Time > 0.5 s
        Mark: A2
    Watch: Block Time > 1 s
        Mark: A3
        End block
    Mark: A4
Mark: A5
"""
        engine = self.engine
        run_engine(engine, program, 25)

        self.assertEqual(["A1", "A4", "A2", "A3", "A5"], engine.interpreter.get_marks())

    def test_block_end_block(self):
        program = """
Block: A
    Mark: A1
    End block
Mark: A2
"""
        engine = self.engine
        run_engine(engine, program, 10)

        self.assertEqual(["A1", "A2"], engine.interpreter.get_marks())

    def test_block_nested_end_block(self):
        program = """
Block: A
    Mark: A1
    Block: B
        Mark: B1
        End block
Mark: A2
"""
        engine = self.engine
        run_engine(engine, program, 15)

        self.assertEqual(["A1", "B1"], engine.interpreter.get_marks())

    def test_block_end_blocks(self):
        program = """
Block: A
    Mark: A1
    End blocks
Mark: A2
"""
        engine = self.engine
        run_engine(engine, program, 10)


        self.assertEqual(["A1", "A2"], engine.interpreter.get_marks())

    def test_block_nested_end_blocks(self):
        program = """
Block: A
    Mark: A1
    Block: B
        Mark: B1
        End blocks
Mark: A2
"""
        engine = self.engine
        run_engine(engine, program, 15)

        self.assertEqual(["A1", "B1", "A2"], engine.interpreter.get_marks())

    def test_base_command_sec(self):
        program = "Base: s"
        e = self.engine
        run_engine(e, program, 5)
        base_tag = e._system_tags[SystemTagName.BASE]
        self.assertEqual("s", base_tag.get_value())

    def test_base_command_min(self):
        program = "Base: min"
        e = self.engine
        run_engine(e, program, 5)
        base_tag = e._system_tags[SystemTagName.BASE]
        self.assertEqual("min", base_tag.get_value())

    def test_base_command_h(self):
        program = "Base: h"
        e = self.engine
        run_engine(e, program, 5)
        base_tag = e._system_tags[SystemTagName.BASE]
        self.assertEqual("h", base_tag.get_value())

    def test_base_default_is_set_to_minutes(self):
        e = self.engine
        base_tag = e._system_tags[SystemTagName.BASE]
        self.assertIsNotNone(base_tag)
        self.assertEqual(base_tag.unit, None)
        self.assertEqual(base_tag.value, "min")

    def test_base_can_set(self):
        e = self.engine
        base_tag = e._system_tags[SystemTagName.BASE]
        base_tag.set_value("s", e._tick_time)

    def test_base_threshold_uses_base_sec(self):
        program = "1 Mark: A1"
        e = self.engine
        base_tag = e._system_tags[SystemTagName.BASE]
        base_tag.set_value("s", e._tick_time)
        run_engine(e, program, 15)
        self.assertEqual(['A1'], e.interpreter.get_marks())

    def test_base_threshold_uses_base_min(self):
        program = "1 Mark: A1"
        e = self.engine
        base_tag = e._system_tags[SystemTagName.BASE]
        base_tag.set_value("min", e._tick_time)
        run_engine(e, program, 15)
        self.assertEqual([], e.interpreter.get_marks())

    def test_base_threshold_uses_default_base_min(self):
        program = "1 Mark: A1"
        e = self.engine
        run_engine(e, program, 15)
        self.assertEqual([], e.interpreter.get_marks())

    @unittest.skip("Review with Eskild")
    def test_block_time_watch_2(self):
        program = build_program("""
Block: A
    Mark: A1
    Watch: Block Time > 0 sec
        End block
    Mark: X
    Mark: A2
Mark: A3
""")
        # TODO review case with Eskild
        # We'll need look-ahead to avoid X being executed

        i = create_interpreter(program=program)
        run_interpreter(i, max_ticks=30)

        self.assertEqual(["A1", "A3"], i.get_marks())

    def test_threshold_time(self):
        program = """
Base: s
0.0 Mark: a
0.3 Mark: b
0.8 Mark: c
"""
        engine = self.engine
        run_engine(engine, program, 20)
        i = engine.interpreter

        self.assertEqual(["a", "b", "c"], i.get_marks())
        # print_log(i)

        # log_a = next(x for x in i.logs if x.message == 'a')
        # log_b = next(x for x in i.logs if x.message == 'b')
        # log_c = next(x for x in i.logs if x.message == 'c')
        # with self.subTest("a, b"):
        #     self.assert_time_equal(log_a.time + .3, log_b.time)
        # with self.subTest("a, c"):
        #     self.assert_time_equal(log_a.time + .8, log_c.time)

    def test_assert_time_equal(self):
        self.assert_time_equal(1, 1.2, 200)
        self.assert_time_equal(1.8, 1.5, 300)
        self.assertRaises(
            AssertionError,
            lambda: self.assert_time_equal(1.8, 1.3, 400)
        )

    def assert_time_equal(self, time_a: float, time_b: float, milis=200):
        """
        Assert that time difference is less than milis miliseconds.

        Note that the default value depends on the interpreter timer interval.
        """
        diff_milis = round(1000 * abs(time_a - time_b))
        if diff_milis > milis:
            s = f"Difference exceeded {milis} ms.\n" + \
                f"Difference: {diff_milis} ms.\n" + \
                f"time_a:      {time_a:.2f} s.\n" + \
                f"time_b:      {time_b:.2f} s.\n"
            raise AssertionError(s)
        else:
            print(f"Diff {diff_milis} accepted")

    def test_threshold_block_time(self):
        program = """
Base: s
Mark: a
Block: A
    0.3 Mark: b
    End block
Block: B
    0.8 Mark: c
    End block
Mark: d
"""
        engine = self.engine
        run_engine(engine, program, 25)

        i = engine.interpreter

        self.assertEqual(["a", "b", "c", "d"], i.get_marks())

    def test_wait(self):
        program = """
Mark: a
Wait: 0.5 s
Mark: b"""
        engine = self.engine
        run_engine(engine, program, 4)
        i = engine.interpreter
        self.assertEqual(["a"], i.get_marks())

        continue_engine(engine, 4)
        self.assertEqual(["a"], i.get_marks())

        continue_engine(engine, 3)

        self.assertEqual(["a", "b"], i.get_marks())

    @unittest.skip("TODO")
    def test_threshold_column_volume(self):
        raise NotImplementedError()

    @unittest.skip("TODO")
    def test_watch_tag_categorized_value(self):
        program = build_program("""
Watch: LT01 = Full
    Mark: a1
Mark: b
""")
        i = create_interpreter(program=program)
        run_interpreter(i, 5)

    @unittest.skip("TODO")
    def test_change_base_in_program(self):
        # base is also available in scope
        raise NotImplementedError()

    @unittest.skip("TODO")
    def test_change_base_in_scope(self):
        # base is global, a change should remain in place after scope completes
        raise NotImplementedError()


if __name__ == "__main__":
    unittest.main()
