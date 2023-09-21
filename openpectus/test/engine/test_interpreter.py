
import logging
import time
from typing import List, Any
import unittest

import pint
from openpectus.engine.eng import ExecutionEngine

from openpectus.lang.grammar.pprogramformatter import print_program
from openpectus.lang.grammar.pgrammar import PGrammar
from openpectus.lang.model.pprogram import PProgram
from openpectus.lang.exec.pinterpreter import InterpreterContext, PInterpreter
from openpectus.lang.exec.uod import UnitOperationDefinitionBase, UodBuilder
from openpectus.lang.exec.tags import Tag, DEFAULT_TAG_BASE, TagCollection
from openpectus.lang.exec.uod import UodCommand

TICK_INTERVAL = 0.1

logging.basicConfig(format=' %(name)s :: %(levelname)-8s :: %(message)s')
logger = logging.getLogger("Engine")
logger.setLevel(logging.DEBUG)


# def warmup_pint(self):
# pint takes forever to initialize - long enough
# to throw off timing of the first instruction.
# so we initialize it first
_ = pint.Quantity("0 sec")


def create_test_uod() -> UnitOperationDefinitionBase:

    def incr_counter(cmd: UodCommand, args: List[Any]):
        counter = cmd.context.tags["counter"]
        count = counter.as_number()
        count = count + 1
        counter.set_value(count)
        cmd.set_complete()

    return (
        UodBuilder()
        .with_instrument("TestUod")
        .with_no_hardware()
        # Readings
        .with_new_system_tags()
        .with_tag(Tag("counter", 0))
        .with_command(UodCommand.builder().with_name("incr counter").with_exec_fn(incr_counter))
        .build()
    )


def create_engine(uod: UnitOperationDefinitionBase | None = None) -> ExecutionEngine:
    if uod is None:
        uod = create_test_uod()
    e = ExecutionEngine(uod)
    e._configure()
    return e


def build_program(s) -> PProgram:
    p = PGrammar()
    p.parse(s)
    return p.build_model()


def print_log(i: PInterpreter):
    start = min([x.time for x in i.logs])
    print('\n'.join(
        f"{(x.time-start):.2f}\t{x.time:.2f}\t{x.unit_time}\t{x.message}" for x in i.logs))


def create_interpreter(
        program: PProgram,
        uod: UnitOperationDefinitionBase | None = None):
    # create interpreter without engine - for non-command programs

    if uod is None:
        uod = create_test_uod()

    engine = create_engine(uod)
    context = TestInterpreterContext(engine)

    return PInterpreter(program, context)


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
        interpreter.tick(tick_time)


def run_engine(engine: ExecutionEngine, pcode: PProgram, max_ticks: int = -1):
    print("Interpretation started")
    ticks = 0
    max_ticks = max_ticks

    engine._running = True
    engine.set_pprogram(pcode)

    while engine.is_running():
        ticks += 1
        if max_ticks != -1 and ticks > max_ticks:
            print(f"Stopping because max_ticks {max_ticks} was reached")
            engine._running = False
            return

        time.sleep(0.1)
        engine.tick()


class InterpreterTest(unittest.TestCase):

    def test_sequential_marks(self):
        program = build_program("""
mark: a
mark: b
mark: c
""")
        print_program(program)
        engine = create_engine()
        run_engine(engine, program, 10)

        self.assertEqual(["a", "b", "c"], engine.interpreter.get_marks())
        print_log(engine.interpreter)

    def test_command_incr_counter(self):
        program = build_program("""
mark: a
incr counter
""")
        print_program(program)
        engine = create_engine()

        self.assertEqual(0, engine.uod.tags["counter"].as_number())

        run_engine(engine, program, 10)

        self.assertEqual(1, engine.uod.tags["counter"].as_number())
        self.assertEqual("a", engine.interpreter.get_marks()[0])

    def test_watch_can_evaluate_tag(self):
        program = build_program("""
mark: a
watch: counter > 0
    mark: b
mark: c
incr counter
watch: counter > 0
    mark: d
""")
        engine = create_engine()
        run_engine(engine, program, 15)

        print_log(engine.interpreter)
        self.assertEqual(["a", "c", "b", "d"], engine.interpreter.get_marks())
        # Note that first watch is also activated and its body executed
        # even though it is not activated when first run. This represents the
        # interrupt nature of watches and alarms. So the behavior is not like this:
        # self.assertEqual(["a", "c", "d"], i.get_marks())

    def test_watch_nested(self):
        program = build_program("""
mark: a
watch: counter > 0
    mark: b
    watch: counter > 1
        mark: e
mark: c
incr counter
incr counter
watch: counter > 0
    mark: d
""")
        engine = create_engine()
        run_engine(engine, program, 15)

        print_log(engine.interpreter)
        #self.assertEqual(["a", "c", "b", "e", "d"], engine.interpreter.get_marks())
        self.assertEqual(["a", "c", "b", "d", "e"], engine.interpreter.get_marks())

    def test_watch_long_running_order(self):
        # specify order of highly overlapping instructions
        # between main program and a single interrupt handler
        program = build_program("""
mark: a
watch: Run counter > -1
    mark: a1
    mark: a2
    mark: a3
mark: b
mark: b1
mark: b2
mark: b3
""")
        engine = create_engine()
        run_engine(engine, program, 10)

        print_log(engine.interpreter)
        self.assertEqual(["a", "b", "a1", "b1", "a2", "b2", "a3", "b3"], engine.interpreter.get_marks())

    @unittest.skip("TODO")
    def test_watch_block_long_running_block_time(self):
        # question for another test: is Block time defined for alarm without block? Yes

        # specify block time for block in interrupt handler

        program = build_program("""
mark: a
watch: Run counter > -1
    Block: A
        mark: a1
        watch: Block time > 0.5 sec
            mark: a2
        watch: Block time > 1.0 sec
            mark: a3
        watch: Block time > 1.2 sec
            mark: a32
        watch: Block time > 1.3 sec
            mark: a33
        watch: Block time > 1.4 sec
            mark: a34
        watch: Block time > 1.5 sec
            mark: a4
            End block
mark: b
""")
        print_program(program)
        engine = create_engine()
        run_engine(engine, program, 15)

        print_log(engine.interpreter)

        # TODO fix intepretation error, watch instruction(s) not being executed

        self.assertEqual(["a", "b", "a1", "a2", "a3", "a4"], engine.interpreter.get_marks())

    def test_block(self):
        program = build_program("""
Block: A
    Mark: A1
    End block
    Mark: A2
Mark: A3
""")
        uod = create_test_uod()
        assert uod.system_tags is not None
        uod.system_tags[DEFAULT_TAG_BASE].set_value("sec")

        engine = create_engine(uod)
        run_engine(engine, program, 10)

        print_log(engine.interpreter)

        self.assertEqual(["A1", "A3"], engine.interpreter.get_marks())

    def test_block_nested(self):
        program = build_program("""
Block: A
    Mark: A1
    Block: B
        Mark: B1
        End block
        Mark: B2
    End block
    Mark: A2
Mark: A3
""")
        engine = create_engine()
        run_engine(engine, program, 15)

        self.assertEqual(["A1", "B1", "A3"], engine.interpreter.get_marks())

    def test_block_unterminated(self):
        program = build_program("""
Block: A
    Mark: A1
    Mark: A2
Mark: A3
""")
        engine = create_engine()
        run_engine(engine, program, 5)

        self.assertEqual(["A1", "A2"], engine.interpreter.get_marks())

    def test_block_time_watch(self):
        program = build_program("""
Block: A
    Mark: A1
    Watch: Block time > 1 sec
        End block
    Mark: A2
Mark: A3
""")
        engine = create_engine()
        run_engine(engine, program, 20)

        self.assertEqual(["A1", "A2", "A3"], engine.interpreter.get_marks())

    @unittest.skip("Base unit not yet implemented")
    def test_block_time_watch_using_base_unit(self):
        program = build_program("""
Block: A
    Mark: A1
    Watch: Block time > 1
        End block
    Mark: A2
Mark: A3
""")
        engine = create_engine()
        run_engine(engine, program, 20)

        self.assertEqual(["A1", "A2", "A3"], engine.interpreter.get_marks())

    @unittest.skip("Review with Eskild")
    def test_block_time_watch_2(self):
        program = build_program("""
Block: A
    Mark: A1
    Watch: Block time > 0 sec
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
        program = build_program("""
0.0 Mark: a
0.3 Mark: b
0.8 Mark: c
""")
        engine = create_engine()
        run_engine(engine, program, 20)
        i = engine.interpreter

        self.assertEqual(["a", "b", "c"], i.get_marks())
        print_log(i)

        log_a = next(x for x in i.logs if x.message == 'a')
        log_b = next(x for x in i.logs if x.message == 'b')
        log_c = next(x for x in i.logs if x.message == 'c')
        with self.subTest("a, b"):
            self.assert_time_equal(log_a.time + .3, log_b.time)
        with self.subTest("a, c"):
            self.assert_time_equal(log_a.time + .8, log_c.time)

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
        program = build_program("""
Mark: a
Block: A
    0.3 Mark: b
    End block
Block: B
    0.8 Mark: c
    End block
Mark: d
""")
        engine = create_engine()
        run_engine(engine, program, 25)
        i = engine.interpreter

        print_log(i)

        self.assertEqual(["a", "b", "c", "d"], i.get_marks())

        log_a = next(x for x in i.logs if x.message == 'a')
        log_b = next(x for x in i.logs if x.message == 'b')
        log_c = next(x for x in i.logs if x.message == 'c')
        log_d = next(x for x in i.logs if x.message == 'd')
        with self.subTest("a / b"):
            self.assert_time_equal(log_a.time + 0.3 + TICK_INTERVAL, log_b.time, 300)
        with self.subTest("b / c"):
            self.assert_time_equal(log_b.time + .8 + TICK_INTERVAL, log_c.time, 300)
        with self.subTest("c / d"):
            self.assert_time_equal(log_c.time + TICK_INTERVAL, log_d.time, 300)
        with self.subTest("a / d"):
            self.assert_time_equal(log_a.time + 1.1 + 6*TICK_INTERVAL, log_d.time, 300)

    @unittest.skip("TODO")
    def test_threshold_column_volume(self):
        raise NotImplementedError()

    @unittest.skip("TODO")
    def test_watch_tag_categorized_value(self):
        program = build_program("""
watch: LT01 = Full
    mark: a1
mark: b
""")
        i = create_interpreter(program=program)
        run_interpreter(i, 5)

        print_log(i)

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


class TestInterpreterContext(InterpreterContext):
    def __init__(self, engine: ExecutionEngine) -> None:
        super().__init__()
        self.engine = engine
        self._tags = engine.uod.system_tags.merge_with(engine.uod.tags)

    @property
    def tags(self) -> TagCollection:
        return self._tags

    def schedule_execution(self, name: str, args: str) -> None:
        self.engine.schedule_execution(name, args)
