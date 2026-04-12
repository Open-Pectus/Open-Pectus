import difflib
import logging
from time import time
from typing import Callable
import typing
import unittest


from opruntime.lang.models import serialize
from opruntime.lang.parser import Method, PcodeParser, MethodLineIdGenerator
import opruntime.lang.program as p
from opruntime.lang.interpreter import Interpreter, MethodEditError, SePath, InterpreterState, HotSwapVisitor

logging.basicConfig(format=' %(name)s :: %(levelname)-8s :: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.getLogger(Interpreter.__module__).setLevel(logging.DEBUG)
logging.getLogger(HotSwapVisitor.__module__).setLevel(logging.DEBUG)


def parse_method(method: Method | str) -> p.ProgramNode:
    if isinstance(method, str):
        method = Method.from_numbered_pcode(method)
    parser = PcodeParser(id_generator=MethodLineIdGenerator(method))
    #parser = PcodeParser()
    return parser.parse_method(method)

def print_method(method: Method, as_numbered_pcode=False, note=""):
    print("-- Method --")
    if note:
        print(note)
    print(method.as_numbered_pcode() if as_numbered_pcode else method.as_pcode())
    print()

def print_program(program: p.ProgramNode | None, note=""):
    print("-- Program --")
    # Consider showing always showing error state so it is not missed
    if note:
        print(note)
    if program is None:
        print("Program is None")
    else:
        if program.has_error(recursive=True):
            print("NOTE: Program has parse error(s):")
            # for error in program.collect_errors():
            #     print(error)
        print(program.as_tree())
    print()


code1 = """\
01 Mark: A
02 Block: B
03     Mark: B1
04     Mark: B2
05 
06     End block
07 Mark: C
08 
"""

code2 = """\
01 Mark: A
02 Block: B
03     Mark: B1
04     Mark: B2
05     Mark: B3
06     End block
07 Mark: C
08 Mark: D
"""


InterpreterAction = Callable[[], None]  # expose active_node instead of using that from generator
""" Something to do in each tick """
InterpreterPredicate = Callable[[], bool]  # expose active_node instead of using that from generator
"""" Called in each tick and can decide to stop the run by returning True """

class Runner():
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter

    def run_internal(
            self,
            start_tick=1,
            max_ticks=30,
            iterate_sub_ticks=False,
            action: InterpreterAction | None = None,
            stop_predicate: InterpreterPredicate | None = None,
            fail_if_max_ticks_is_reached=False
            ):

        tick_number = start_tick
        # if self.interpreter.generator is None:
        #     self.interpreter.generator = self.interpreter.create_generator()

        while tick_number <= max_ticks + start_tick - 1:
            logger.debug(f"Run Tick {tick_number}")
            tick_time = time()

            if stop_predicate is not None and stop_predicate():
                logger.info("Run ended because predicate was True")
                return

            t0 = time()
            if iterate_sub_ticks:
                for _ in self.interpreter.tick_iterate_subticks(tick_time, tick_number):
                    if stop_predicate is not None and stop_predicate():
                        logger.info("Run ended because predicate was True")
                        return
            else:
                self.interpreter.tick(tick_time, tick_number)

            t1 = time()
            td = t1-t0
            if td > 0.5:
                logger.error(f"Tick took too long: {td:.2f} seconds")

            if action:
                action()
            tick_number += 1

        if fail_if_max_ticks_is_reached:
            raise AssertionError(f"The run did not break before reaching {max_ticks=}")
        else:
            logger.info(f"Run ended because tick reached {max_ticks=}")

    def run(self,
            start_tick=1,
            max_ticks=30,
            action: InterpreterAction | None = None,
            stop_predicate: InterpreterPredicate | None = None
            ):
        self.run_internal(
                start_tick=start_tick,
                max_ticks=max_ticks,
                iterate_sub_ticks=True,
                action=action,
                stop_predicate=stop_predicate,
                fail_if_max_ticks_is_reached=False
            )

    def run_until(self,
                  stop_predicate: InterpreterPredicate,
                  start_tick=1,
                  max_ticks=30,
                  action: InterpreterAction | None = None
                  ):
        """ Like run but always fails if max_ticks is reached """
        self.run_internal(
            start_tick=start_tick,
            max_ticks=max_ticks,
            iterate_sub_ticks=True,
            action=action,
            stop_predicate=stop_predicate,
            fail_if_max_ticks_is_reached=True
        )

    def run_until_path(self,
                       path: str,
                       start_tick=1,
                       max_ticks=30,
                       action: InterpreterAction | None = None,
                       fail_if_max_ticks_is_reached=True
                       ):
        def path_predicate(sep: SePath) -> bool:
            return sep.path == path

        logger.info(f"Start running until path '{path}' is reached")
        return self.run_until_path_condition(
            path_predicate, start_tick=start_tick, max_ticks=max_ticks, action=action,
            fail_if_max_ticks_is_reached=fail_if_max_ticks_is_reached)

    def run_until_instruction(self,
                              node_id_or_key: str,
                              start_tick=1,
                              max_ticks=30,
                              action: InterpreterAction | None = None
                              ):
        def path_predicate(sep: SePath) -> bool:
            if "." in node_id_or_key:
                return sep.has_node_key(node_id_or_key)
            else:
                return sep.has_node_id(node_id_or_key)

        logger.info(f"Start running until instruction with node id or key '{node_id_or_key}' is reached")
        return self.run_until_path_condition(
            path_predicate, start_tick=start_tick, max_ticks=max_ticks, action=action, fail_if_max_ticks_is_reached=True)

    def run_until_path_condition(self,
                                 path_predicate: Callable[[SePath], bool],
                                 start_tick=1,
                                 max_ticks=30,
                                 action: InterpreterAction | None = None,
                                 fail_if_max_ticks_is_reached=False,
                                 ):
        tick_number = start_tick

        while tick_number <= max_ticks + start_tick - 1:
            logger.debug(f"Run Tick {tick_number}")
            tick_time = time()

            # if stop_predicate is not None and stop_predicate():
            #     logger.info("Run ended because predicate was True")
            #     return

            t0 = time()
            break_on_tick_completion = False
            for sep in self.interpreter.tick_iterate_subticks(tick_time, tick_number):
                #logger.debug(f"Checking path {sep.path}")
                if path_predicate(sep):
                    logger.info(f"Breaking run because path_predicate returned True for path '{sep.path}'...")
                    break_on_tick_completion = True

            if break_on_tick_completion:
                logger.info("Break run complete")
                return

            t1 = time()
            td = t1-t0
            if td > 0.5:
                logger.error(f"Tick took too long: {td:.2f} seconds")

            if action:
                action()
            tick_number += 1

        if fail_if_max_ticks_is_reached:
            raise AssertionError(f"The run did not break before reaching {max_ticks=}")
        else:
            logger.info(f"Run ended because tick reached {max_ticks=}")


# Helper methods to keep tests small
def create(method: str | Method) -> tuple[Interpreter, Runner]:
    """ Factory function to create interpreter and runner initialized with the given method """
    interpreter = Interpreter()
    if isinstance(method, str):
        method = Method.from_numbered_pcode(method)
    interpreter.set_method(method)
    return interpreter, Runner(interpreter)

def merge(interpreter: Interpreter, new_method: str | Method) -> tuple[Interpreter, Runner]:
    """ Adapter method to simplify test of merging and decouple tests from actual state organization.

    Important: New instances of interpreter and runner are returned. The original interpreter instance is not affected.  """
    logger.debug("\nLive-edit merge started")
    assert interpreter.method is not None
    if isinstance(new_method, str):
        new_method = Method.from_numbered_pcode(new_method)
    logger.debug(f"Current method:\n{interpreter.method.as_numbered_pcode()}\n")
    se_paths = [interpreter.main_sep.path] + [x.sep.path for x in interpreter.interrupts]
    logger.debug(f"Current se_paths:\n{'\n'.join(se_paths)}\n")

    logger.debug(f"New method:\n{new_method.as_numbered_pcode()}\n")
    new_interpreter = interpreter.from_merge(new_method)
    # Doing this advances the interrupt generators so their se_paths are initialized - but the main generator is not right
    # It is not critical - but it does indicate that the states are not completely equivalent
    # for _ in new_interpreter.tick_iterate_subticks(0, 0):
    #     pass
    # new_paths = [new_interpreter.main_sep.path] + [x.sep.path for x in new_interpreter.interrupts]
    # logger.debug(f"New paths:\n{'\n'.join(new_paths)}\n")

    logger.debug("Live-edit merge completed\n")
    return new_interpreter, Runner(new_interpreter)


class InterpreterTest(unittest.TestCase):

    # region Specialized asserts
    def setUp(self):
        logger.info("Test setUp")
        return super().setUp()


    def assertMethodsEqual(self, new_method: Method, old_method: Method):
        diffs = Method.compare(old_method, new_method)
        if len(diffs) > 0:
            for diff in diffs:
                logger.warning(diff)
            self.fail(f"""\
Methods are not equal:

{serialize(old_method)}

(old) VS (new)

{serialize(new_method)}""")

    def assertTreeStateEqual(self, new_state: dict[str, p.NodeState], old_state: dict[str, p.NodeState],
                             html_diff_filepath: str | None = None):
        new_lines = serialize(new_state).splitlines()
        old_lines = serialize(old_state).splitlines()
        diffs = difflib.unified_diff(a=new_lines, b=old_lines, n=8, lineterm="")
        if len(list(diffs)) > 0:
            logger.warning("---- states do not match:")
            for diff in diffs:
                logger.warning(diff)

            if html_diff_filepath is not None:
                differ = difflib.HtmlDiff()
                html = differ.make_file(
                    fromlines=new_lines,
                    tolines=old_lines,
                    fromdesc="New / edited",
                    todesc="Old / original",
                    # fromdesc="test_id: " + test_id + " @ ",
                    # todesc="time: " + datetime.now().isoformat(timespec="seconds"),
                    context=False)
                with open(html_diff_filepath, 'w') as f:
                    f.write(html)                    
                logger.warning(f"See html diff of state mismatch here: file:///{html_diff_filepath}")
            raise AssertionError("Tree states do not match. See log for details")

    # endregion

    # region Interpretation

    def test_run(self):
        interpreter, runner = create(code1)

        assert interpreter.program is not None
        print_program(interpreter.program)

        runner.run()

        self.assertEqual(["A", "B1", "B2", "C"], interpreter.marks)

    def test_run_break_run(self):
        interpreter, runner = create(code1)

        runner.run_until_instruction("03")

        self.assertEqual(["A", "B1"], interpreter.marks)

        runner.run(max_ticks=10)

        self.assertEqual(["A", "B1", "B2", "C"], interpreter.marks)

    def test_run_watch_inactive(self):
        code = """\
01 Mark: A
02 Watch: foo
03     Mark: B
07 Mark: C
"""

        interpreter, runner = create(code)
        assert interpreter.program is not None
        print_program(interpreter.program)

        runner.run()

        self.assertEqual(["A", "C"], interpreter.marks)
        self.assertEqual(interpreter.main_sep.path, "root")


    def test_run_watch_active(self):
        code = """\
01 Mark: A
02 Watch: true that
03     Mark: B
07 Mark: C
"""

        interpreter, runner = create(code)
        assert interpreter.program is not None
        print_program(interpreter.program)

        runner.run(max_ticks=10)

        self.assertIn(interpreter.marks, [["A", "B", "C"], ["A", "C", "B"]])

    def test_run_alarm_inactive(self):
        code = """\
01 Mark: A
02 Alarm: foo
03     Mark: B
07 Mark: C
"""

        interpreter, runner = create(code)
        assert interpreter.program is not None
        print_program(interpreter.program)

        runner.run(max_ticks=20)

        self.assertEqual(["A", "C"], interpreter.marks)

    def test_run_alarm_active(self):
        code = """\
01 Mark: A
02 Alarm: true that
03     Mark: B
07 Mark: C
"""

        interpreter, runner = create(code)
        assert interpreter.program is not None
        print_program(interpreter.program)

        def should_stop() -> bool:
            if "B" in interpreter.marks and "C" in interpreter.marks:
                return True
            return False

        cut_tick = 15
        runner.run(
            stop_predicate=should_stop,
            max_ticks=cut_tick
        )

        self.assertIn("B", interpreter.marks)
        self.assertIn("C", interpreter.marks)
        old_length = len(interpreter.marks)

        # self.assertIn(interpreter.marks, [["A", "B", "C"], ["A", "C", "B"]])

        runner.run(start_tick=cut_tick, max_ticks=5)

        # TODO may be exiting early because interrupt is exhaused mid way
        new_marks = interpreter.marks[old_length:]
        self.assertGreater(len(new_marks), 0)
        for c in new_marks:
            self.assertEqual(c, "B")

    def test_run_alarm_multiple_invocations(self):
        code = """\
01 Mark: A
02 Alarm: true that
03     Mark: B
07 Mark: C
"""

        interpreter, runner = create(code)
        assert interpreter.program is not None
        print_program(interpreter.program)

        def ends_with_3_bs() -> bool:
            if len(interpreter.marks) > 3:
                if interpreter.marks[-3:] == ["B", "B", "B"]:
                    return True
            return False

        runner.run_until(ends_with_3_bs)
        print("Marks:", interpreter.marks)

    def test_run_block_w_nested_watch_synchronized(self):
        code1 = """\
01 Mark: A
02 Block: B
03     Mark: B
04     Watch: true
05         Mark: C
08         End block
09 Mark: D
"""
        interpreter, runner = create(code1)
        runner.run()

        # End block in the watch acts as synchronization so C occurs before D
        self.assertEqual(interpreter.marks, ["A", "B", "C", "D"])

    def test_run_block_w_nested_watch_unsynchronized(self):
        code1 = """\
01 Mark: A
02 Block: B
03     Mark: B
04     Watch: true
05         Mark: C
07     End block
08     Mark: E
09     Mark: F
10 Mark: G
"""
# 06     Mark: D
        interpreter, runner = create(code1)
        runner.run()

        # This is a tricky example:
        # - C never gets to execute because End block aborts the Watch interrupt before it even starts
        # - E shouldn't really be there . not sure we want to fix that. It gets really complex in prod because
        #     the block needs to wait for 
        #self.assertEqual(interpreter.marks, ["A", "B", "E", "F"])
        #self.assertEqual(interpreter.marks, ["A", "B", "D", "C", "E", "F"])
        #self.assertEqual(interpreter.marks, ["A", "B", "F"])
        logger.debug("Actual marks:")
        logger.debug(interpreter.marks)
        self.assertEqual(interpreter.marks[0:2], ["A", "B"])
        self.assertNotIn("C", interpreter.marks) # the watch is aborted before it gets to run
        # E can be there or not but F should not
        self.assertNotIn("F", interpreter.marks)
        self.assertIn("G", interpreter.marks)

    def test_run_block_w_end_in_watch(self):
        code = """\
01 Watch: to-be-set
02     Mark: C
03     End block
04 Watch: true
05     Block: A
06         Mark: D
09 Mark: A
10 Mark: Activating watch
19 Mark: B
"""
        interpreter, runner = create(code)
        assert interpreter.program is not None
        watch = interpreter.program.get_first_child_or_throw(p.WatchNode)
        block = interpreter.program.get_first_child_or_throw(p.BlockNode)

        runner.run_until_instruction("10")

        logger.debug("Activating watch")
        watch.arguments = "true"

        runner.run()

        self.assertEqual(block.block_ended, True)
        self.assertEqual(block.lock_acquired, False)

    def test_run_block_lock(self):
        code = """\
01 Watch: true
02     Block: B1
03         Abc
04         End block
06 Block: B2
07     Mark: A
08     End block
09 Mark: B
"""
        interpreter, runner = create(code)
        assert interpreter.program is not None
        [block_b1, block_b2] = [b for b in interpreter.program.get_all_nodes() if isinstance(b, p.BlockNode)]
        self.assertEqual(block_b1.lock_acquired, False)
        self.assertEqual(block_b1.block_ended, False)
        self.assertEqual(block_b2.lock_acquired, False)
        self.assertEqual(block_b2.block_ended, False)

        runner.run_until_instruction("07.Mark")

        # B2 beats B1 to it because B1 is in Watch
        self.assertEqual(block_b1.lock_acquired, False)
        self.assertEqual(block_b1.block_ended, False)
        self.assertEqual(block_b2.lock_acquired, True)
        self.assertEqual(block_b2.block_ended, False)

        runner.run_until_instruction("03.Abc")

        self.assertEqual(block_b1.block_ended, False)
        self.assertEqual(block_b1.lock_acquired, True)
        self.assertEqual(block_b2.block_ended, True)
        self.assertEqual(block_b2.lock_acquired, False)

        runner.run()

        self.assertEqual(block_b1.block_ended, True)
        self.assertEqual(block_b1.lock_acquired, False)
        self.assertEqual(block_b2.block_ended, True)
        self.assertEqual(block_b2.lock_acquired, False)

    def test_run_block_nested_lock(self):
        code = """\
01 Watch: true
02     Block: B1
03         Abc
04         End block
06 Block: B2
07     Mark: A
08     Abc
10     Block: B3
11         Mark: B
12         End block
13     End block
"""
        interpreter, runner = create(code)
        assert interpreter.program is not None
        [block_b1, block_b2, block_b3] = [b for b in interpreter.program.get_all_nodes() if isinstance(b, p.BlockNode)]
        self.assertEqual(block_b2.lock_acquired, False)
        self.assertEqual(block_b2.block_ended, False)
        self.assertEqual(block_b3.lock_acquired, False)
        self.assertEqual(block_b3.block_ended, False)

        runner.run_until_instruction("07.Mark")

        self.assertEqual(block_b2.lock_acquired, True)
        self.assertEqual(block_b2.block_ended, False)
        self.assertEqual(block_b3.lock_acquired, False)
        self.assertEqual(block_b3.block_ended, False)

        runner.run_until_instruction("11.Mark")

        self.assertEqual(block_b2.lock_acquired, True)
        self.assertEqual(block_b2.block_ended, False)
        self.assertEqual(block_b3.lock_acquired, True)
        self.assertEqual(block_b3.block_ended, False)

        runner.run()

        self.assertEqual(block_b1.lock_acquired, False)
        self.assertEqual(block_b1.block_ended, True)
        self.assertEqual(block_b2.lock_acquired, False)
        self.assertEqual(block_b2.block_ended, True)
        self.assertEqual(block_b3.lock_acquired, False)
        self.assertEqual(block_b3.block_ended, True)

    def test_run_block_deeply_nested_lock(self):
        code = """\
01 Block: B1
02     Mark: A
03     Block: B2
04         Mark: B
05         Block: B3
06             Mark: C
07             End block
08         End block
09     End block
10 Mark: D
"""
        interpreter, runner = create(code)
        assert interpreter.program is not None
        [block_b1, block_b2, block_b3] = [b for b in interpreter.program.get_all_nodes() if isinstance(b, p.BlockNode)]
        self.assertEqual(block_b1.lock_acquired, False)
        self.assertEqual(block_b1.block_ended, False)
        self.assertEqual(block_b2.lock_acquired, False)
        self.assertEqual(block_b2.block_ended, False)
        self.assertEqual(block_b3.lock_acquired, False)
        self.assertEqual(block_b3.block_ended, False)

        runner.run_until_instruction("02.Mark")

        self.assertEqual(interpreter.main_sep, "root > root.child.0 > 01.Block > 01.Block.child.0 > 02.Mark")
        self.assertEqual(block_b1.lock_acquired, True)
        self.assertEqual(block_b1.block_ended, False)
        self.assertEqual(block_b2.lock_acquired, False)
        self.assertEqual(block_b2.block_ended, False)
        self.assertEqual(block_b3.lock_acquired, False)
        self.assertEqual(block_b3.block_ended, False)

        runner.run_until_instruction("04.Mark")

        self.assertEqual(interpreter.main_sep,
                         "root > root.child.0 > 01.Block > 01.Block.child.1 > 03.Block > 03.Block.child.0 > 04.Mark")
        self.assertEqual(block_b1.lock_acquired, True)
        self.assertEqual(block_b1.block_ended, False)
        self.assertEqual(block_b2.lock_acquired, True)
        self.assertEqual(block_b2.block_ended, False)
        self.assertEqual(block_b3.lock_acquired, False)
        self.assertEqual(block_b3.block_ended, False)

        runner.run_until_instruction("06.Mark")

        self.assertEqual(block_b1.lock_acquired, True)
        self.assertEqual(block_b1.block_ended, False)
        self.assertEqual(block_b2.lock_acquired, True)
        self.assertEqual(block_b2.block_ended, False)
        self.assertEqual(block_b3.lock_acquired, True)
        self.assertEqual(block_b3.block_ended, False)

        runner.run_until_instruction("08.End block")

        self.assertEqual(block_b1.lock_acquired, True)
        self.assertEqual(block_b1.block_ended, False)
        self.assertEqual(block_b2.lock_acquired, True)  # impl detail, note 1
        self.assertEqual(block_b2.block_ended, True)    # impl detail, note 2
        self.assertEqual(block_b3.lock_acquired, False)
        self.assertEqual(block_b3.block_ended, True)

        # note 1: Block ending is signalled but visit_BlockNode has not discovered it yet and released the lock
        # note 2: block_ended is the signal from visit_EndBlockNode to visit_BlockNode

        runner.run()

        self.assertEqual(block_b1.lock_acquired, False)
        self.assertEqual(block_b1.block_ended, True)
        self.assertEqual(block_b2.lock_acquired, False)
        self.assertEqual(block_b2.block_ended, True)
        self.assertEqual(block_b3.lock_acquired, False)
        self.assertEqual(block_b3.block_ended, True)

    def test_run_block_nested_unevenly(self):
        code = """\
01 Block: B1
02     Mark: A
03     Block: B2
04         Mark: B
05         End block
06         End block # dead code because it belongs to Block: B2
"""
        interpreter, runner = create(code)
        assert interpreter.program is not None

        [block_b1, block_b2] = [b for b in interpreter.program.get_all_nodes() if isinstance(b, p.BlockNode)]
        runner.run()

        self.assertEqual(block_b1.lock_acquired, True)
        self.assertEqual(block_b1.block_ended, False)
        self.assertEqual(block_b2.lock_acquired, False)
        self.assertEqual(block_b2.block_ended, True)

    def test_run_block_deeply_nested_lock_interrupt(self):
        code = """\
01 Watch: true
02     Abc
03     End block
04     End block
05     End block
06 Block: B2
07     Mark: A
10     Block: B3
11         Mark: B
12         Block: B4
13             Mark: C
"""
        interpreter, runner = create(code)
        assert interpreter.program is not None
        [block_b2, block_b3, block_b4] = [b for b in interpreter.program.get_all_nodes() if isinstance(b, p.BlockNode)]
        self.assertEqual(block_b2.lock_acquired, False)
        self.assertEqual(block_b2.block_ended, False)
        self.assertEqual(block_b3.lock_acquired, False)
        self.assertEqual(block_b3.block_ended, False)
        self.assertEqual(block_b4.lock_acquired, False)
        self.assertEqual(block_b4.block_ended, False)

        runner.run_until_instruction("07.Mark")

        self.assertEqual(block_b2.lock_acquired, True)
        self.assertEqual(block_b2.block_ended, False)
        self.assertEqual(block_b3.lock_acquired, False)
        self.assertEqual(block_b3.block_ended, False)
        self.assertEqual(block_b4.lock_acquired, False)
        self.assertEqual(block_b4.block_ended, False)

        runner.run_until_instruction("13.Mark")

        self.assertEqual(block_b2.lock_acquired, True)
        self.assertEqual(block_b2.block_ended, False)
        self.assertEqual(block_b3.lock_acquired, True)
        self.assertEqual(block_b3.block_ended, False)
        self.assertEqual(block_b4.lock_acquired, True)
        self.assertEqual(block_b4.block_ended, False)

        runner.run_until_instruction("03.End block")

        self.assertEqual(block_b2.lock_acquired, True)
        self.assertEqual(block_b2.block_ended, False)
        self.assertEqual(block_b3.lock_acquired, True)
        self.assertEqual(block_b3.block_ended, False)
        self.assertEqual(block_b4.lock_acquired, True)
        self.assertEqual(block_b4.block_ended, True)

        runner.run_until_instruction("04.End block")

        self.assertEqual(block_b2.lock_acquired, True)
        self.assertEqual(block_b2.block_ended, False)
        self.assertEqual(block_b3.lock_acquired, True)
        self.assertEqual(block_b3.block_ended, True)
        self.assertEqual(block_b4.lock_acquired, False)
        self.assertEqual(block_b4.block_ended, True)

        runner.run()

        self.assertEqual(block_b2.lock_acquired, False)
        self.assertEqual(block_b2.block_ended, True)
        self.assertEqual(block_b3.lock_acquired, False)
        self.assertEqual(block_b3.block_ended, True)
        self.assertEqual(block_b4.lock_acquired, False)
        self.assertEqual(block_b4.block_ended, True)

    def test_run_end_block_and_block_in_main(self):
        code = """\
01 Block: B
02     Mark: A
03     End block
04 Mark: B
"""
        interpreter, runner = create(code)
        assert interpreter.program is not None
        block = interpreter.program.get_first_child_or_throw(p.BlockNode)

        runner.run()

        self.assertEqual(block.block_ended, True)
        self.assertEqual(interpreter.main_sep.path, "root")

    def test_run_end_block_in_main_and_block_in_interrupt(self):
        code = """\
01 Watch: true
02     Block: B
03         Abc
04 Mark: A
05 End block
06 Mark: C
"""
        interpreter, runner = create(code)
        assert interpreter.program is not None
        watch = interpreter.program.get_first_child_or_throw(p.WatchNode)
        block = interpreter.program.get_first_child_or_throw(p.BlockNode)
        abc = interpreter.program.get_first_child_or_throw(p.AbcNode)
        runner.run_until(lambda: abc.abc_state == "A")

        watch.arguments = "true"
        runner.run()

        self.assertEqual(block.block_ended, True)
        #self.assertEqual(abc.abc_state, "A")

    def test_run_end_block_in_interrupt_and_block_in_main(self):
        code = """\
01 Watch: W1
02     Mark: A
03     End block
04 Block: B1
05     Abc
"""
        interpreter, runner = create(code)
        assert interpreter.program is not None
        watch = interpreter.program.get_first_child_or_throw(p.WatchNode)
        block = interpreter.program.get_first_child_or_throw(p.BlockNode)
        abc = interpreter.program.get_first_child_or_throw(p.AbcNode)
        runner.run_until(lambda: abc.abc_state == "A")

        watch.arguments = "true"
        runner.run()

        self.assertEqual(block.block_ended, True)

    def test_run_end_block_in_interrupt_and_block_in_another_interrupt(self):
        code = """\
01 Watch: W1
02     End block
03 Watch: true
04     Block: B1
05         Abc
"""
        interpreter, runner = create(code)
        assert interpreter.program is not None
        watch = interpreter.program.get_first_child_or_throw(p.WatchNode)
        block = interpreter.program.get_first_child_or_throw(p.BlockNode)
        abc = interpreter.program.get_first_child_or_throw(p.AbcNode)
        runner.run_until(lambda: abc.abc_state == "A")

        watch.arguments = "true"
        runner.run()

        self.assertEqual(block.block_ended, True)

    def test_run_watch_in_alarm(self):
        # it is not well defined - if alarm goes off every second, how often should watch run if its condition is true?
        # should alarm somehow wait for "contained" interrupts?
        code = """\
01 Mark: A
02 Alarm: true that
03     Mark: B
04     Watch: x
05         Mark: C
07 Mark: eof
"""

        interpreter, runner = create(code)
        assert interpreter.program is not None
        alarm_node = interpreter.program._children[1]
        assert isinstance(alarm_node, p.AlarmNode)
        watch_node = alarm_node._children[1]
        assert isinstance(watch_node, p.WatchNode)

        print_program(interpreter.program)

        runner.run(
            stop_predicate=lambda: alarm_node.run_count == 3,
            max_ticks=20
        )

        watch_node.arguments = "Now evaluates to True"
        runner.run(
            stop_predicate=lambda: alarm_node.run_count == 6,
            max_ticks=20
        )

        # self.assertIn("B", interpreter.marks)
        # self.assertIn("C", interpreter.marks)
        # old_length = len(interpreter.marks)

    def test_run_macro_def(self):
        code = """\
01 Mark: A
02 Macro: M
03     Mark: B
04     Mark: C
05 
06 Mark: D
"""
        interpreter, runner = create(code)
        assert interpreter.program is not None
        macro_node = interpreter.program._children[1]
        assert isinstance(macro_node, p.MacroNode)

        # print_program(interpreter.program)
        runner.run_until(lambda: "D" in interpreter.marks)

        # verify macro was defined
        self.assertNotEqual(len(interpreter.program.macros), 0)
        self.assertIs(macro_node, interpreter.program.macros[macro_node.macro_name])

    def test_run_macro_call(self):
        code = """\
01 Mark: A
02 Macro: M
03     Mark: B
04     Mark: C
05 
06 Call macro: M
07 Mark: D
"""
        interpreter, runner = create(code)
        assert interpreter.program is not None
        macro_node = interpreter.program._children[1]
        assert isinstance(macro_node, p.MacroNode)

        runner.run_until(lambda: "D" in interpreter.marks)

        # verify macro was called
        self.assertIn("B", interpreter.marks)
        self.assertIn("C", interpreter.marks)
        self.assertEqual(macro_node.run_started_count, 1)


    def test_run_macro_multiple_calls(self):
        code = """\
01 Mark: A
02 Macro: M
03     Mark: B
04     Mark: C
05 
06 Call macro: M
07 Mark: D
08 Call macro: M
09 Mark: E
"""
        interpreter, runner = create(code)
        assert interpreter.program is not None
        macro_node = interpreter.program._children[1]
        assert isinstance(macro_node, p.MacroNode)

        runner.run_until(lambda: "E" in interpreter.marks)

        # verify macro was called three times
        self.assertIn("B", interpreter.marks)
        self.assertIn("C", interpreter.marks)
        self.assertEqual(macro_node.run_started_count, 2)
        self.assertEqual(interpreter.marks, ["A", "B", "C", "D", "B", "C", "E"])

    def test_run_idle_program(self):
        # test that program node is idle when program is executed
        code = "01 Mark: A"
        interpreter, runner = create(code)
        runner.run()

        assert interpreter.program is not None
        self.assertEqual(True, interpreter.program.started)
        self.assertEqual(False, interpreter.program.completed)

    def test_run_idle_watch(self):
        # test that watch remains idle and (thus appendable) when it has run
        # that "watch remains idle" actually just means that it doesn't complete
        # because it has a whitespace line blocking it
        # in prod this may be different because analyzers help with this

        code = """\
01 Mark: A
02 Watch: true that
03     Mark: B
04 
07 Mark: C
"""

        interpreter, runner = create(code)
        assert interpreter.program is not None
        watch = interpreter.program.get_first_child_or_throw(p.WatchNode)
        blank = interpreter.program.get_first_child_or_throw(p.BlankNode)

        blank.test_has_only_trailing_whitespace = True

        runner.run()
        self.assertEqual(interpreter.marks, ["A", "C", "B"])
        self.assertEqual(False, watch.completed)

    # idle behavior: Modify running method II #732


    def test_run_idle_block(self):
        # a Block node is not really idle - it just appears that way when
        # is has no EndBlock or EndBlocks
        method = Method.from_numbered_pcode("""\
01 Block: A
02     Mark: B
03 Mark: C
""")

        interpreter, runner = create(method)

        runner.run()

        self.assertEqual(interpreter.marks, ["B"])
        self.assertEqual(interpreter.main_sep.path, "root > root.child.0 > 01.Block")

    @unittest.skip(reason="TODO")
    def test_idle_aka_editable_run(self):
        # hmm - idling refers to a code block that has kinda completed but remains open to modification
        # eg. a Watch child collection that has completed but its containing code block still runs
        # see issues:
        # #732
        # - Example 1. Watch remains in scope, even when it has run. Its body may be extended and the additional instructions are executed
        # - Example 2. Watch is editable until surrounding block is completed.
        # #721 
        # - Command in method with threshold not yet satisfied should not show up in run log and should remain editable

        # There are multiple aspects if idling/editability
        # 1. Run
        #    - interpreter must set started+completed on nodes so that on interruption, they will not re-run
        #    - children_complete must not be set until parent scope completes
        #      - when is that exactly? ProgramNode never completes, it just stops on Stop
        #        - Block instructions complete onEn Block(s)
        #        - Watch/Alarm by extension, the scope of child instructions of ProgramNode never completes
        #        by extension, the scope of child instructions of ProgramNode never completes
        #     ???? todo define, document and implement this properly
        #     TODO consider renaming HasChildren to CompoundNode or CompositeNode, this would help in documentation and reasoning
        # 2. Live-edit
        #    - the child collection of an instruction remain appendable as long as completed and self.children_complete
        #      are not set
        raise NotImplementedError()

    @unittest.skip(reason="TODO")
    def test_block_lock(self):
        # #715 Limit block concurrency
        raise NotImplementedError()

    @unittest.skip(reason="TODO")
    def test_run_timing(self):
        # Need quite a few tests to demonstrate how timing works accurately, regardless (or because?) of VisitResult
        # The gist is that we must have a reliable way to start and maintain and end accurate timing for all scopes
        # Idea: We might replace timing tags with node data - or at least have the timers return node timings. This
        # would let us implement it here in playground rather than as tags using then event system. but we'll see
        raise NotImplementedError()

    @unittest.skip(reason="TODO")
    def test_run_visitresult(self):
        # on run, we want one tick per "natural" progress and 1 sub-tick for each part
        # the test runner could allow stopping at sub-ticks
        # ProgramNode
        # - start 0 ContinueTick
        # - start_children 0.1 ContinueTick
        # - visit_children 0.2 ContinueTick
        #   -  each child child:
        #       yield visit(child) child visit decides whether to return EndTick or ContinueTick
        # - children complete ContinueTick (?)
        # Mark start 0 ContinueTick, end EndTick
        # Can we handle main-interrupt synchronization if using sub-ticks?
        # - when running normally, execute each iterator until it yields EndTick. This handles synchronization in a simple way
        #   This is implemented in interpreter.tick()
        # - in tests, support both modes:
        #   - tick - same as normal, runner only checks stop_predicate once every tick
        #   - sub-tick, runner checks predicate on each subtick. runner synchronizes iterators
        #
        # When iterating from cold state, we should preferably only reach EndTick once, and then be on
        # the active node. This is because, with no EndTick present in the loop visits and the skip
        # in visit for completed nodes, that should hopefully do it...
        raise NotImplementedError()

    # possibly test force/cancel - except that is more of an engine thing


# endregion


    # region Live-edit

    def test_run_edit_run_pre_block_active(self):
        interpreter, runner = create(code1)
        assert interpreter.program is not None

        runner.run(max_ticks=1)

        self.assertEqual(["A"], interpreter.marks)  # max_ticks=1
        self.assertEqual("root > root.child.0 > 01.Mark", interpreter.main_sep.path)

        interpreter2, runner2 = merge(interpreter, code2)
        runner2.run()

        self.assertEqual(["B1", "B2", "B3", "C", "D"], interpreter2.marks)

    def test_run_edit_run_block_active(self):
        interpreter, runner = create(code1)

        assert interpreter.program is not None

        runner.run_until_instruction("03")

        self.assertEqual(["A", "B1"], interpreter.marks)  # max_ticks=2

        interpreter2, runner2 = merge(interpreter, code2)

        runner2.run()

        self.assertEqual(["B2", "B3", "C", "D"], interpreter2.marks)

    def test_run_edit_run_block_child_active(self):
        interpreter, runner = create(code1)

        runner.run_until(lambda: "B1" in interpreter.marks)

        self.assertEqual(
            interpreter.main_sep.path,
            "root > root.child.1 > 02.Block > 02.Block.child.0 > 03.Mark")
        self.assertEqual(["A", "B1"], interpreter.marks)  # max_ticks=2

        interpreter2, runner2 = merge(interpreter, code2)

        assert interpreter2.program is not None
        mark_b1 = interpreter2.program.get_child_by_id("03")
        assert isinstance(mark_b1, p.MarkNode)
        self.assertEqual(mark_b1.arguments, "B1")
        self.assertEqual(mark_b1.completed, True)

        runner2.run()

        self.assertEqual(["B2", "B3", "C", "D"], interpreter2.marks)

    def test_run_edit_run_post_block_active(self):
        interpreter, runner = create(code1)
        assert interpreter.program is not None

        runner.run_until_instruction("07")

        self.assertEqual(["A", "B1", "B2", "C"], interpreter.marks)  # max_ticks=6

        with self.assertRaises(MethodEditError):
            merge(interpreter, code2)


    def test_run_edit_delete_block_child(self):
        new_code = """\
01 Mark: A
02 Block: B
03     Mark: B1
06     End block
07 Mark: C
08 
"""

        interpreter, runner = create(code1)
        assert interpreter.program is not None

        runner.run_until_instruction("01")

        self.assertEqual(["A"], interpreter.marks)

        interpreter2, runner2 = merge(interpreter, new_code)

        runner2.run()

        self.assertEqual(["B1", "C"], interpreter2.marks)

    def test_run_edit_delete_post_block_node(self):
        new_code = """\
01 Mark: A
02 Block: B
03     Mark: B1
04     Mark: B2
05 
06     End block
"""
        interpreter, runner = create(code1)
        assert interpreter.program is not None

        runner.run_until_instruction("01")
        self.assertEqual(["A"], interpreter.marks)

        interpreter2, runner2 = merge(interpreter, new_code)

        runner2.run()

        self.assertEqual(["B1", "B2"], interpreter2.marks)

    def test_run_edit_run_watch_never(self):
        code1 = """\
01 Mark: A
02 Watch: foo
03     Mark: B
07 Mark: C
"""
        code2 = """\
01 Mark: A
02 Watch: foo
03     Mark: B
07 Mark: C
08 Mark: D
"""
        interpreter, runner = create(code1)
        runner.run_until_instruction("01")

        interpreter2, runner2 = merge(interpreter, code2)
        runner2.run()

        self.assertEqual(interpreter2.marks, ["C", "D"])

    def test_run_edit_run_apply_state_for_nodes_not_run(self):
        code1 = """\
01 Mark: A
02 Mark: B
03 Mark: C
"""
        code2 = """\
01 Mark: A
02 Mark: B
03 Mark: D
"""
        interpreter, runner = create(code1)
        runner.run_until_instruction("01")
        self.assertEqual(interpreter.marks, ["A"])

        interpreter2, runner2 = merge(interpreter, code2)
        runner2.run()

        self.assertEqual(interpreter2.marks, ["B", "D"])

    def test_run_edit_run_watch_always(self):
        code1 = """\
01 Mark: A
02 Watch: true
03     Mark: B
07 Mark: C
"""
        code2 = """\
01 Mark: A
02 Watch: true
03     Mark: B
07 Mark: C
08 Mark: D
"""
        interpreter, runner = create(code1)
        runner.run_until_instruction("01")

        interpreter2, runner2 = merge(interpreter, code2)
        runner2.run()

        self.assertEqual(interpreter2.marks, ["C", "B", "D"])

    def test_run_edit_run_watch_with_Abc(self):
        code1 = """\
02 Watch: true
03     Abc
04 Mark: C
05 
"""
        code2 = """\
02 Watch: true
03     Abc
04 Mark: C
05 Mark: D
"""
        interpreter, runner = create(code1)        
        assert interpreter.program is not None
        abc = interpreter.program.get_first_child_or_throw(p.AbcNode)
        #self.assertEqual(interpreter.marks, ["A", "B", "D"])
        self.assertEqual(abc.abc_state, '')

        runner.run_until_instruction("04")
        self.assertEqual(abc.abc_state, 'A')

        interpreter2, runner2 = merge(interpreter, code2)
        assert interpreter2.program is not None
        abc2 = interpreter2.program.get_first_child_or_throw(p.AbcNode)

        self.assertEqual(abc2.abc_state, 'A')

        runner2.run()

        self.assertEqual(abc2.abc_state, 'C')

    def test_run_edit_run_alarm_multiple_invocations(self):
        code1 = """\
01 Mark: A
02 Alarm: true that
03     Mark: B
07 Mark: C
08 Noop: 7
09 
"""
        code2 = """\
01 Mark: A
02 Alarm: true that
03     Mark: B
07 Mark: C
08 Noop: 7
09 Mark: D
10 Noop: 9
"""

        method = Method.from_numbered_pcode(code1)
        interpreter = Interpreter()
        interpreter.set_method(method)
        runner = Runner(interpreter)

        assert interpreter.program is not None
        print_program(interpreter.program)

        def ends_with_3_bs() -> bool:
            if len(interpreter.marks) > 3:
                if interpreter.marks[-3:] == ["B", "B", "B"]:
                    return True
            return False

        #runner.run_until(lambda: "C" in interpreter.marks)
        runner.run_until(ends_with_3_bs)
        print("Marks:", interpreter.marks)
        self.assertEqual(interpreter.marks, ["A", "C", "B", "B", "B"])

        interpreter2, runner2 = merge(interpreter, code2)

        def noop_10_is_complete():
            assert interpreter2.program is not None
            for node in interpreter2.program.get_child_nodes(recursive=True):
                if node.name == "Noop" and node.arguments == "10":
                    if node.completed:
                        return True
            return False

        def ends_with_3_bs_v2() -> bool:
            if len(interpreter2.marks) > 3:
                if interpreter2.marks[-3:] == ["B", "B", "B"]:
                    return True
            return False

        runner2.run_until(lambda: "D" in interpreter2.marks and ends_with_3_bs_v2())

        print("Marks:", interpreter2.marks)
        self.assertEqual(interpreter2.marks[-4:], ["D", "B", "B", "B"])

    def test_run_edit_run_block_w_nested_watch_synchronized(self):
        code1 = """\
01 Mark: A
02 Block: B
03     Mark: B
04     Watch: true
05         Mark: C
08         End block
09 
"""
        code2 = """\
01 Mark: A
02 Block: B
03     Mark: B
04     Watch: true
05         Mark: C
06         Mark: D
08         End block
09 Mark: E
"""

        method = Method.from_numbered_pcode(code1)
        interpreter = Interpreter()
        interpreter.set_method(method)
        runner = Runner(interpreter)

        runner.run_until(lambda: "C" in interpreter.marks)

        self.assertEqual(interpreter.marks, ["A", "B", "C"])

        method2 = Method.from_numbered_pcode(code2)
        interpreter, runner = merge(interpreter, method2)

        print_program(interpreter.program)
        logger.debug("Active path: " + interpreter.main_sep.path)
        runner.run()

        self.assertEqual(interpreter.marks, ["D", "E"])



    def test_run_edit_run_idle_program_append(self):
        code1 = """\
01 Mark: A
02 
"""
        code2 = """\
01 Mark: A
02 Mark: B
03 
"""

        interpreter, runner = create(code1)
        assert interpreter.program is not None
        blank = interpreter.program.get_first_child_or_throw(p.BlankNode)

        # manually set this because we have no analyzers in playground
        blank.test_has_only_trailing_whitespace = True

        runner.run()
        self.assertEqual(interpreter.marks, ["A"])

        interpreter2, runner2 = merge(interpreter, code2)
        runner2.run()

        self.assertEqual(interpreter2.marks, ["B"])

    def test_run_edit_run_idle_watch_append(self):
        # Note: we don't have the full idle functionality in place, regarding appending to non-blank
        # lines. But until we define that, we can still test that if a Watch ends in a blank line that
        # is idle, then replacing it should work.
        # Except we also don't have any requirements regarding the parent of blank nodes - so this may 
        # not work or it may be incorrect
        code1 = """\
01 Mark: A
02 Watch: true
03     Mark: B
04 
05 Mark: C
"""
        code2 = """\
01 Mark: A
02 Watch: true
03     Mark: B
04     Mark: D
05 Mark: C
"""

        interpreter, runner = create(code1)
        assert interpreter.program is not None
        watch = interpreter.program.get_first_child_or_throw(p.WatchNode)
        blank = interpreter.program.get_first_child_or_throw(p.BlankNode)
        self.assertEqual(blank.id, "04")

        # manually set this because we have no analyzers in playground
        # note - this only makes sense if the node is a child of Watch. Otherwise it's
        # just incorrect to set "only trailing whitespace"
        blank.test_has_only_trailing_whitespace = True
        # so this is actually the case regardless of how many spaces there are on the blank line
        self.assertEqual(blank.parent, watch)

        runner.run()
        self.assertIn(interpreter.marks, [["A", "B", "C"], ["A", "C", "B"]])

        interpreter2, runner2 = merge(interpreter, code2)

        logger.debug("Acctive node: " + str(interpreter.main_sep))
        runner2.run()

        self.assertEqual(interpreter2.marks, ["D"])


    def test_run_edit_run_idle_block_extended_block_does_end(self):
        method1 = Method.from_numbered_pcode("""\
02 Block: B1
03     0.5 Mark: A
05 
06 Mark: C
""")

        method2 = Method.from_numbered_pcode("""\
02 Block: B1
03     0.5 Mark: A
04     1.0 Mark: B
05     End block
06 Mark: C
""")

        interpreter, runner = create(method1)
        assert interpreter.program is not None
        blank = interpreter.program.get_first_child_or_throw(p.BlankNode)
        blank.test_has_only_trailing_whitespace = True

        runner.run()
        self.assertEqual(["A"], interpreter.marks)

        interpreter2, runner2 = merge(interpreter, method2)

        runner2.run()
        self.assertEqual(["B", "C"], interpreter2.marks)

    def test_run_edit_run_line_awaiting_threshold_may_be_edited(self):
        # is implemented in prod in generic visit() by not setting node.started until threshold has passed
        pass


    def test_run_edit_run_alarm(self):
        code1 = """\
01 Mark: A
02 Alarm: true that
03     Mark: B
07 Mark: C
"""
        code2 = """\
01 Mark: A
02 Alarm: true that
03     Mark: B
07 Mark: C
08 Mark: D
"""
        interpreter, runner = create(code1)

        runner.run_until(lambda: "C" in interpreter.marks)
        self.assertIn(interpreter.marks, [["A", "B", "C"], ["A", "C", "B"], ["A", "C"]])
        print("Marks pre edit:", interpreter.marks)

        interpreter, runner = merge(interpreter, code2)

        def ends_with_3_bs() -> bool:
            if len(interpreter.marks) > 3:
                if interpreter.marks[-3:] == ["B", "B", "B"]:
                    return True
            return False

        runner.run_until(ends_with_3_bs)
        print("Marks post edit:", interpreter.marks)


    def test_run_edit_run_macro(self):
        code1 = """\
01 Mark: A
02 Macro: M
03     Mark: B
04     Mark: C
05 
06 Mark: D
07 Call macro: M
08 Mark: E
09 
"""
        code2 = """\
01 Mark: A
02 Macro: M
03     Mark: B
04     Mark: C
05 
06 Mark: D
07 Call macro: M
08 Mark: E
09 Call macro: M
10 Mark: F
"""
        method1 = Method.from_numbered_pcode(code1)
        interpreter = Interpreter()
        interpreter.set_method(method1)
        runner = Runner(interpreter)

        assert interpreter.program is not None
        macro_node = interpreter.program.get_first_child_or_throw(p.MacroNode)

        # print_program(interpreter.program)
        runner.run_until(lambda: "E" in interpreter.marks)
        self.assertEqual(["A", "D", "B", "C", "E"], interpreter.marks)

        # verify macro was defined
        self.assertNotEqual(len(interpreter.program.macros), 0)
        self.assertIs(macro_node, interpreter.program.macros[macro_node.macro_name])

        method2 = Method.from_numbered_pcode(code2)
        interpreter2, runner2 = merge(interpreter, method2)

        runner2.run_until(lambda: "F" in interpreter2.marks)
        self.assertEqual(["B", "C", "F"], interpreter2.marks)

    def test_run_edit_run_macro_new_merge(self):
        code1 = """\
01 Mark: A
02 Macro: M
03     Mark: B
04     Mark: C
05 
06 Mark: D
07 Call macro: M
08 Mark: E
09 
"""
        code2 = """\
01 Mark: A
02 Macro: M
03     Mark: B
04     Mark: C
05 
06 Mark: D
07 Call macro: M
08 Mark: E
09 Call macro: M
10 Mark: F
"""
        interpreter, runner = create(code1)
        assert interpreter.program is not None

        macro_node = interpreter.program.get_first_child_or_throw(p.MacroNode)
        macro_name = macro_node.macro_name
        macro_id = macro_node.id

        # print_program(interpreter.program)
        runner.run_until(lambda: "E" in interpreter.marks)
        self.assertEqual(["A", "D", "B", "C", "E"], interpreter.marks)

        # verify macro was defined
        self.assertNotEqual(len(interpreter.program.macros), 0)
        self.assertIs(macro_node, interpreter.program.macros[macro_name])

        # middle_state = interpreter.get_cold_state()
        # states should not be equal - but the comparison creates a nice diff view
        # self.assertTreeStateEqual(init_state.tree_state, middle_state.tree_state, "C:\\mjolner-code\\Novo\\runtime3\\opruntime\\test\\comparison.html")

        method2 = Method.from_numbered_pcode(code2)
        #interpreter2, runner2 = merge(interpreter, method2, transter_environment=False)
        new_state = interpreter._new_merge(method2)
        self.assertIn(macro_id, new_state.macros_registered)


    def test_run_edit_run_macro_redefinition(self):
        # Is redefinition different from editing macro after it was started?
        code1 = """\
01 Macro: M
02     Mark: B
03     Mark: C
04 
05 Mark: A
06 Call macro: M
07 Mark: D
08 
"""
        code2 = """\
01 Macro: M
02     Mark: B
03     Mark: C
04 
05 Mark: A
06 Call macro: M
07 Mark: D
11 Macro: M
12     Mark: B
13 
14 Mark: E
15 Call macro: M
16 Mark: F
"""
        method1 = Method.from_numbered_pcode(code1)
        interpreter = Interpreter()
        interpreter.set_method(method1)
        runner = Runner(interpreter)

        assert interpreter.program is not None
        macro_node = interpreter.program._children[0]
        assert isinstance(macro_node, p.MacroNode)

        # print_program(interpreter.program)
        runner.run_until(lambda: "D" in interpreter.marks)
        self.assertEqual(["A", "B", "C", "D"], interpreter.marks)
        
        # verify macro was defined
        self.assertNotEqual(len(interpreter.program.macros), 0)
        self.assertIs(macro_node, interpreter.program.macros[macro_node.macro_name])

        interpreter2, runner2 = merge(interpreter, code2)

        runner2.run_until(lambda: "F" in interpreter2.marks)
        self.assertEqual(["E", "B", "F"], interpreter2.marks)


    def method_breaks_live_edit_test(self, test_name: str, code: str, line_filter=None, skip_lines=[]):
        """ Run method multiple times in subtests with different break/resume positions and merges
        and verify that all end states are equal.

        Use line_filter with line id to run only a single line test, useful for debugging.

        Use skip_lines with line ids to altogether skip testing with these lines as breaks.
        Use this if some break points just don't make sense.
        """
        # use same style as self.method_breaks_test to generate method edit permutations
        # perform a base line run and collect end state
        # for each line in method:
        #   define pre_method with lines = method.lines[0: inx_of_line]
        #   run pre_method up to last(maybe the one before)
        #   live-edit the method back to org
        #   run to end, collect state and compare it to original end state
        # 	verify state

        logger.info("\n\n")
        logger.info(f"---- Running live-edit method test {test_name}")
        logger.info(f"---- Method\n{code}")

        # first do a complete baseline run and collect original state as initial_end_state
        logger.info("\n")
        logger.info("---- Starting baseline run")
        # Run original method and collect end state
        method_org = Method.from_numbered_pcode(code)
        if len(method_org.lines) < 3:
            raise ValueError("Method is too short. Must be at least 3 lines for this test")

        interpreter_org, runner_org = create(method_org)
        assert interpreter_org.program is not None

        runner_org.run(max_ticks=30)
        end_state_org = interpreter_org.get_cold_state()

        logger.debug("Baseline run ended with path: " + end_state_org.main_sep.path)
        logger.info("---- Baseline run complete\n")

        line_inx = -1
        for line in method_org.lines:
            line_inx += 1
            if line_inx == 0:
                continue  # skip test of empty method
            if line.id in skip_lines:
                logger.warning(f"Skipping line {line} - marked for skip")
                continue
            if line_filter and line_filter != line.id:
                logger.warning(f"Line filter {line_filter} is active - skipping line {line}")
                continue

            test_id = test_name + "_" + line.id
            with self.subTest(test_id):
                logger.info("\n")
                logger.info(f"---- Run method with break at {line.id=} | {line}")
                if line_inx + 1 >= len(method_org.lines):
                    continue

                pre_lines = method_org.lines[0: line_inx + 1]
                pre_method = Method(lines=pre_lines)
                logger.info(f"Partial method code:\n{pre_method.as_numbered_pcode()}")
                interpreter_pre, runner_pre = create(pre_method)

                try:
                    runner_pre.run_until_instruction(line.id)
                    logger.info(f"---- Stopped because {line.id=} was reached")
                except AssertionError as ae:
                    logger.debug("AssertionError during interpretation: {ae}")
                    if ae.args[0].startswith("The run did not break before reaching"):
                        logger.debug(f"Skipped check for line {line.id} {line.content}. The line was not reached.")
                        continue
                    raise
                except Exception as ex:
                    logger.error(f"Unhandled exception during interpretation: {ex}", exc_info=True)
                    raise

                interpreter_edit, runner_edit = merge(interpreter_pre, method_org)
                assert interpreter_edit.method is not None

                logger.info(f"Merged method code:\n{interpreter_edit.method.as_numbered_pcode()}")
                runner_edit.run()
                end_state_edit = interpreter_edit.get_cold_state()

                logger.info("---- Compare merged run against baseline run")
                self.assertMethodsEqual(end_state_edit.method, end_state_org.method)
                self.assertTreeStateEqual(
                    end_state_edit.tree_state,
                    end_state_org.tree_state,
                    "C:\\mjolner-code\\Novo\\runtime3\\opruntime\\test\\comparison.html")
                self.assertEqual(end_state_edit.main_sep.path, end_state_org.main_sep.path)
                logger.info("---- states identical for baseline run vs merge run")


    def test_live_edit_produces_identical_state_Watch(self):
        self.method_breaks_live_edit_test("Mark1", "01 Mark: A\n02 Mark: B\n03 Mark: C")
        #self.method_breaks_live_edit_test("Mark2", "01 Mark: A\n02 Mark: B\n03 \n04 Noop")

    def test_live_edit_produces_identical_state_Alarm(self):
        self.method_breaks_live_edit_test("Alarm never", "01 Mark: A\n02 Alarm: false\n03     Mark: C\n04     Mark: D")
        self.method_breaks_live_edit_test("Alarm 2", """\
01 Mark: A
02 Alarm: foo
03     Mark: B
07 Mark: C
""")

        self.method_breaks_cold_state_test("Alarm always", """\
01 Mark: A
02 Alarm: true,max_run_count_5
03     Mark: C
04     Mark: D")
""")

    def test_live_edit_produces_identical_state_Macro(self):
        self.method_breaks_live_edit_test("Macro def", """\
01 Mark: A
02 Macro: M
03     Mark: B
04     Mark: C
05 
06 Mark: D
""")

        self.method_breaks_live_edit_test("Macro call", """\
02 Macro: M
03     Mark: B
07 Call macro: M
""")

        self.method_breaks_live_edit_test("Macro call 2", """\
02 Macro: M
03     Mark: B
07 Call macro: M
08 Mark: C
09 Call macro: M
10 Mark: D
11 Call macro: M
""")

        self.method_breaks_live_edit_test("Macro call redefinition", """\
01 Macro: M
02     Mark: B
03     Mark: C
04 
05 Mark: A
06 Call macro: M
07 Mark: D
11 Macro: M
12     Mark: B
13 
14 Mark: E
15 Call macro: M
16 Mark: F
""")

        self.method_breaks_live_edit_test("Macro redefinition call edit", """\
01 Macro: M
02     Mark: A
03 Call macro: M
04 Macro: M
05     Mark: B
06 Call macro: M
""")

    def test_live_edit_produces_identical_state_Abc(self):
        self.method_breaks_live_edit_test("Abc", """\
01 Mark: A
02 Watch: true
03     Mark: B
04     Abc
05     Mark: C
06 Mark: D
07 Mark: E
08 Mark: F
""")

    def test_live_edit_produces_identical_state_Block(self):
        self.method_breaks_live_edit_test("Block 1", """\
02 Block: A
03     Mark: B
05     Mark: C
06     End block
07 Mark: E
08 Mark: F
""")

        self.method_breaks_live_edit_test("Block 2", """\
02 Block: A
03     Mark: B
05     Mark: C
07 Mark: E
08 Mark: F
""")

        self.method_breaks_live_edit_test("Block 3", """\
02 Watch: true
03     Mark: B
05     End block
07 Block: A
08     Mark: A
18 Mark: C
20 Mark: D
21 Mark: E
""", skip_lines=["05"])

        self.method_breaks_live_edit_test("Block 4", """\
01 Mark: A
02 Block: B
03     Mark: B
04     Watch: true
05         Mark: C
07     End block
08     Mark: E
09     Mark: F
10 Mark: G
""", skip_lines=["04", "05"])

    def test_live_edit_produces_identical_state_work(self):
        pass


    # endregion


    # region Cold-state


    @unittest.skip("Todo")
    def test_create_interpreter_from_persisted_state(self):
        pass

        # In total, we should have 3 ways to create Intepreter
        # 1) Empty state and method. This is the normal case. From here, the method
        #    can be edited while Stopped or merged while Running.
        # 2) State and method + new_method. This is the live editing/method merge case
        #    The results should be two interpreters. An unmodified instance that can continue
        #    if the merge fails and an updated one that can continue with the edited method
        # 3) Method and state from serialization/pickle/disk
        #    State includes:
        #    - Method
        #    - Tree state, from program.get_tree_state()        
        #    - main SePath
        #    - interrupts, incl SePath for each
        #    - macros
        #    Special care
        #    - all done
        #    Possibly also
        #    - Runtime records
        #    - Null nodes for nodes without source in method (injected, possibly others)
        #    - Stack - looks like we can remove this - still not completely sure though. There may be
        #      cases where End block in an interrupt should end a Block in the main flow or in another interrupt.
        #      This does not seem possible without the stack
        # MethodManager and Engine should coordinate construction of interpreters in these cases.

# call stack
# tracking + runtimeinfo
# child_index - on remove_child and append_child may sometimes need to change this value

        # in any case, we need to construct the NodeGenerator's for main program flow as well as any interrupts.

        # null nodes - is that relevant?
        # usage in openpectus:
        # - NullNode(Node), Marker type for temporary nodes, notably for Start which is executed before tracking
        #   is initialized
        # - InjectedNode, because neither InjectedNode nor any of its child nodes are inserted into
        #   the program (yet?), we create a custom null node and record for it
        #   self.tracking.create_injected_node_records(node)
        #   these nodes have custom data in records, runtimeinfo._injected_node_map, runtimeinfo._null_node_map
        #   this would also need to be persisted, right? Like the complete record list (TODO)


    def test_from_state_with_stateful_node(self):
        method = Method.from_pcode("Abc")  # special test node with 4 states
        interpreter = Interpreter()
        interpreter.set_method(method)
        assert interpreter.program is not None
        runner = Runner(interpreter)
        abc_node = interpreter.program.get_first_child_or_throw(p.AbcNode)

        def has_state_B() -> bool:
            return abc_node.abc_state == "B"

        runner.run_until(has_state_B)
        self.assertEqual(abc_node.abc_state, "B")

        state = interpreter.get_cold_state()
        runner.run()
        self.assertEqual(abc_node.abc_state, "C")
        self.assertEqual(abc_node.completed, True)

        # what about the side effects of interpreter1 - like marks
        # there should not be any that are not contained in
        #  context (tags), records, interrupts
        interpreter2 = Interpreter.from_cold_state(state)
        assert interpreter2.program is not None
        abc_node2 = interpreter2.program.get_first_child_or_throw(p.AbcNode)
        self.assertEqual(abc_node2.abc_state, "B")
        self.assertEqual(abc_node2.completed, False)

        runner2 = Runner(interpreter2)
        runner2.run()

        self.assertEqual(abc_node2.abc_state, "C")
        self.assertEqual(abc_node2.completed, True)

    def test_from_state_create_generator(self):
        interpreter, runner = create(code1)
        assert interpreter.program is not None

        cut_tick = 2
        runner.run(max_ticks=cut_tick)
        logger.info(f"Run until {cut_tick=} done")

        self.assertEqual(
            interpreter.main_sep.path,
            "root > root.child.1 > 02.Block > 02.Block.child.0 > 03.Mark")
        self.assertEqual(["A", "B1"], interpreter.marks)  # max_ticks=2
        tree_state = interpreter.program.extract_tree_state()
        logger.info("Tree state @B1")
        logger.info(serialize(tree_state))

        # this data should suffice to restart in a new run
        logger.info("")
        logger.info("Starting continue run")

        interpreter2, runner2 = create(code1)
        assert interpreter2.program is not None
        interpreter2.program.apply_tree_state(tree_state)
        runner2 = Runner(interpreter2)

        # what about the side effects of interpreter1 - like marks
        # there should not be any that are not contained in
        #  context (tags), records, interrupts
        runner2.run(start_tick=cut_tick + 1)

        self.assertEqual(["B2", "C"], interpreter2.marks)

    def test_from_state_Noop(self):
        # verify that restart from cold state starts over for a Noop instruction
        code1 = """\
01 Mark: A
02 Alarm: true that
03     Mark: B
08 Noop: 12
09 
"""

        method = Method.from_numbered_pcode(code1)
        interpreter = Interpreter()
        interpreter.set_method(method)
        runner = Runner(interpreter)

        assert interpreter.program is not None
        print_program(interpreter.program)

        def ends_with_3_bs() -> bool:
            if len(interpreter.marks) > 2:
                if interpreter.marks[-3:] == ["B", "B", "B"]:
                    return True
            return False

        runner.run_until(ends_with_3_bs)
        print("Marks:", interpreter.marks)
        self.assertEqual(interpreter.marks, ["A", "B", "B", "B"])

        tree_state = interpreter.program.extract_tree_state()
        marks = interpreter.marks  # represents context state
        logger.info(serialize(tree_state))
        print(serialize(tree_state))

        logger.info("")
        logger.info("Restarting from cold state")

        interpreter2: Interpreter = Interpreter()
        interpreter2.set_method(method)
        assert interpreter2.program is not None
        interpreter2.marks = marks
        interpreter2.program.apply_tree_state(tree_state)
        logger.info("State post merge")
        logger.info(serialize(interpreter2.program.extract_tree_state()))

        runner2 = Runner(interpreter2)
        runner2.run(start_tick=100, max_ticks=10)

        self.assertEqual(interpreter2.marks, ["A", "B", "B", "B"])


    def test_from_state_macro(self):
        code = """\
01 Mark: A
02 Macro: M
03     Mark: B
04     Mark: C
05 
06 Mark: D
07 Call macro: M
08 Mark: E
09 Call macro: M
10 Mark: F
"""
        interpreter, runner = create(code)
        assert interpreter.program is not None
        macro_node = interpreter.program._children[1]
        assert isinstance(macro_node, p.MacroNode)

        # start run to generate cold state data
        runner.run_until(lambda: "E" in interpreter.marks)
        self.assertEqual(["A", "D", "B", "C", "E"], interpreter.marks)

        # verify macro was defined
        self.assertNotEqual(len(interpreter.program.macros), 0)
        self.assertIs(macro_node, interpreter.program.macros[macro_node.macro_name])

        marks = interpreter.marks  # represents context state
        state = interpreter.get_cold_state()
        # logger.info("Interpreter state")
        # logger.info(serialize(state))

        # let interpreter run to end
        runner.run()
        end_state = interpreter.get_cold_state()

        logger.info("")
        logger.info("Starting continue run from cold state")

        interpreter2: Interpreter = Interpreter.from_cold_state(cold_state=state)
        interpreter2.marks = marks
        runner2 = Runner(interpreter2)
        runner2.run_until(lambda: "F" in interpreter2.marks)
        self.assertEqual(["A", "D", "B", "C", "E", "B", "C", "F"], interpreter2.marks)

        end_state2 = interpreter2.get_cold_state()

        # self.assertEqual(end_state.export_date, end_state2.export_date) # these are different by design
        self.assertMethodsEqual(end_state.method, end_state2.method)
        #self.assertEqual(end_state.active_instruction_id, end_state2.active_instruction_id)

        # test without setting context data. this would really be present in the physical machine connected to the engine
        interpreter3: Interpreter = Interpreter.from_cold_state(state)
        runner3 = Runner(interpreter3)
        runner3.run_until(lambda: "F" in interpreter3.marks)
        self.assertEqual(["B", "C", "F"], interpreter3.marks)

    def test_from_state_macro_redefinition(self):
        code = """\
01 Macro: M
02     Mark: A
13 Call macro: M
14 Mark: C
15 Macro: M
16     Mark: B
17     Mark: A
27 Mark: D
28 Call macro: M
29 Mark: E
"""
        self.method_breaks_cold_state_test("macro redefinition", code)

    # endregion

    def test_from_state_iterator_moves_to_active(self):

        # test for all(?) instructions that interpreter from_cold_state starts iterating the 
        # same node as original

        code = """\
01 Mark: A
01 Mark: B
"""

        interpreter = Interpreter()
        interpreter.set_method(Method.from_numbered_pcode(code))
        runner = Runner(interpreter)

        assert interpreter.program is not None

        # start run to generate cold state data
        runner.run_until(lambda: "A" in interpreter.marks)
        self.assertEqual(["A"], interpreter.marks)

        state = interpreter.get_cold_state()

        # complete the run
        runner.run()
        end_state = interpreter.get_cold_state()

        interpreter2 = Interpreter.from_cold_state(state)
        Runner(interpreter2).run()

        end_state2 = interpreter2.get_cold_state()

        self.assertEqual(end_state2.main_sep.path, end_state.main_sep.path)
        self.assertMethodsEqual(end_state2.method, end_state.method)
        self.assertTreeStateEqual(end_state2.tree_state, end_state.tree_state)


    def method_breaks_cold_state_test(self, test_name: str, code: str, line_filter=None, skip_lines=[]):
        """ Run method multiple times in subtests with different break/resume positions and cold state
        startups and verify that all end states are equal.

        Use line_filter with line id to run only a single line test, useful for debugging.

        Use skip_lines with line ids to altogether skip testing with these lines as breaks.
        Use this if some break point just don't make sense.
        """
        # for a given pcode method
        # - run it start to finish and collect its end state as initial_end_state
        # - for each method line
        #   - create interpreter and set method
        #   - run method from start until that line is executed
        #   - extract state as intermediate_state
        #   - complete the run and extract state as end_state
        #   - compare end_state to initial_end_state. If not identical, fail the test
        #   - create new interpreter with intermediate_state as cold state
        #   - start and complete the run and extract state as end_state2
        #   - compare states end_state and end_state2. If not identical, fail the test

        logger.info("\n\n")
        logger.info(f"---- Running method test {test_name}")
        logger.info(f"---- Method\n{code}")
        method = Method.from_numbered_pcode(code)

        # first do a complete baseline run and collect original state as initial_end_state
        logger.info("\n")
        logger.info("---- Starting baseline run")
        initial_interpreter, initial_runner = create(method)
        initial_runner.run()
        initial_end_state = initial_interpreter.get_cold_state()
        logger.info("---- Baseline run complete\n")

        for line in method.lines:
            if line.id in skip_lines:
                logger.warning(f"Skipping line {line} - marked for skip")
                continue
            if line_filter and line_filter != line.id:
                logger.warning(f"Line filter {line_filter} is active - skipping line {line}")
                continue

            intermediate_state: InterpreterState | None = None
            end_state: InterpreterState | None = None
            test_id = test_name + "_" + line.id
            with self.subTest(test_id):
                logger.info("\n")
                logger.info(f"---- Run method with break at {line.id=} | {line}")
                interpreter, runner = create(method)
                try:
                    runner.run_until_instruction(line.id)
                    logger.info(f"---- Stopped because {line.id=} was reached")
                except AssertionError as ae:
                    logger.debug("AssertionError during interpretation: {ae}")
                    if ae.args[0].startswith("The run did not break before reaching"):
                        logger.debug(f"Skipped check for line {line.id} {line.content}. The line was not reached")
                        continue
                    raise
                except Exception as ex:
                    logger.error(f"Unhandled exception during interpretation: {ex}", exc_info=True)
                    raise

                intermediate_state = interpreter.get_cold_state()

                logger.info("---- Running the remaining lines")
                runner.run()
                end_state = interpreter.get_cold_state()

                # match end_state with initial
                logger.info("---- Compare initial run against the break/continued run")
                self.assertMethodsEqual(end_state.method, initial_end_state.method)
                self.assertTreeStateEqual(
                    end_state.tree_state,
                    initial_end_state.tree_state,
                    "C:\\mjolner-code\\Novo\\runtime3\\opruntime\\test\\comparison.html"
                )
                logger.info("---- states identical for initial run vs break/continue run ")

                logger.info("\n")
                logger.info("---- Re-run test from cold state")
                logger.debug("Cold state is:\n" + serialize(intermediate_state))

                interpreter2 = Interpreter.from_cold_state(intermediate_state)
                interpreter2.marks = interpreter.marks
                runner2 = Runner(interpreter2)
                runner2.run()
                end_state2 = interpreter2.get_cold_state()

                logger.info("---- Compare cold state run against the break/continued run")
                if interpreter.marks != interpreter2.marks:
                    logger.warning("---- Marks differ")
                    logger.warning(interpreter.marks)
                    logger.warning(interpreter2.marks)
                else:
                    logger.info("---- Marks identical: " + str(interpreter.marks))

                self.assertMethodsEqual(end_state2.method, initial_end_state.method)
                self.assertTreeStateEqual(
                    end_state2.tree_state,
                    initial_end_state.tree_state,
                    "C:\\mjolner-code\\Novo\\runtime3\\opruntime\\test\\comparison.html")

                logger.info("---- states identical")
                logger.info(f"---- Test run for break at line {line.id} complete")


    def test_from_state_produces_identical_state_Mark(self):
        self.method_breaks_cold_state_test("Mark1", "01 Mark: A\n02 Mark: B")
        self.method_breaks_cold_state_test("Mark2", "01 Mark: A\n02 Mark: B\n03 Noop")

    def test_from_state_produces_identical_state_Watch(self):
        self.method_breaks_cold_state_test("Watch always", "01 Mark: A\n02 Watch: true-ish\n03     Mark: C\n04     Mark: D")
        self.method_breaks_cold_state_test("Watch never", "01 Mark: A\n02 Watch: false\n03     Mark: C\n04     Mark: D")
        self.method_breaks_cold_state_test("Watch 2", """\
01 Mark: A
02 Watch: foo
03     Mark: B
07 Mark: C
""")
        self.method_breaks_cold_state_test("Watch 3", """\
01 Mark: A
02 Watch: true
03     Mark: B
07 Mark: C
08 Mark: D
""")

    def test_from_state_produces_identical_state_Alarm(self):
        self.method_breaks_cold_state_test("Alarm never", "01 Mark: A\n02 Alarm: false\n03     Mark: C\n04     Mark: D")
        self.method_breaks_cold_state_test("Alarm 2", """\
01 Mark: A
02 Alarm: foo
03     Mark: B
07 Mark: C
""")

        self.method_breaks_cold_state_test("Alarm always", """\
01 Mark: A
02 Alarm: true,max_run_count_5
03     Mark: C
04     Mark: D")
""")

    def test_from_state_produces_identical_state_Macro(self):
        self.method_breaks_cold_state_test("Macro def", """\
01 Mark: A
02 Macro: M
03     Mark: B
04     Mark: C
05 
06 Mark: D
""")

        self.method_breaks_cold_state_test("Macro call", """\
02 Macro: M
03     Mark: B
07 Call macro: M
""")

        self.method_breaks_cold_state_test("Macro call 2", """\
02 Macro: M
03     Mark: B
07 Call macro: M
08 Mark: C
09 Call macro: M
10 Mark: D
11 Call macro: M
""")

    def test_from_state_produces_identical_state_Abc(self):
        self.method_breaks_cold_state_test("Abc", """\
01 Mark: A
02 Watch: true
03     Mark: B
04     Abc
05     Mark: C
06 Mark: D
07 Mark: E
08 Mark: F
""")

    def test_from_state_produces_identical_state_Block(self):
        self.method_breaks_cold_state_test("Block 1", """\
02 Block: A
03     Mark: B
05     Mark: C
06     End block
07 Mark: E
08 Mark: F
""")

        self.method_breaks_cold_state_test("Block 2", """\
02 Block: A
03     Mark: B
05     Mark: C
07 Mark: E
08 Mark: F
""")

        self.method_breaks_cold_state_test("Block 3", """\
02 Watch: true
03     Mark: B
05     End block
07 Block: A
08     Mark: A
18 Mark: C
20 Mark: D
21 Mark: E
""")

        self.method_breaks_cold_state_test("Block 4", """\
01 Mark: A
02 Block: B
03     Mark: B
04     Watch: true
05         Mark: C
07     End block
08     Mark: E
09     Mark: F
10 Mark: G
""", skip_lines=["04"])

    def test_from_state_produces_identical_state_work(self):
        pass

    def test_compare_method(self):
        test_id = 0

        def assert_methods(a: Method, b: Method, expect_match: bool):
            nonlocal test_id
            test_name = str(test_id)
            try:
                test_name = f"{test_id}_{a.lines[0].content[0:10]}..."
            except Exception:
                pass
            with self.subTest(test_name):
                test_id += 1

                differences = Method.compare(a, b)
                print("Differences", "\n".join(differences))
                if len(differences) == 0:
                    if expect_match:
                        pass
                    else:
                        #print("Differences", differences)
                        raise AssertionError("States matched but were not supposed to")
                else:
                    if expect_match:
                        #print("Differences", differences)
                        raise AssertionError("States did not match but were expected to")
                    else:
                        pass

        method_a = Method.from_numbered_pcode("01 Mark: A\n02 Mark: B\n04 \n05 Stop")
        method_a_identical = Method.from_numbered_pcode(method_a.as_numbered_pcode())
        method_b = Method.from_numbered_pcode("01 Mark: A\n02 Mark: C\n05 Stop")
        assert_methods(method_a, method_a, True)
        assert_methods(method_a, method_a_identical, True)
        assert_methods(method_a, method_b, False)
        assert_methods(method_b, method_b, True)


# region FFW

    # These tests verify the fast-forward behavior by asserting conditions when "the next instruction" has run.
    # The purpose is to ensure that when an interpreter is a certain state (either by method merge or by creating
    # it from cold state, some condition is True about the next executed instruction (node visit with
    # node.completed==False).
    #
    # These test are still here - but actually, "next instruction" is poorly defined because there is a next instruction
    # in the main generator and one per interrupt. This concept is captured better in SePath. Tests can use run_until_path()
    # which checks the path on every subtick and thus match even if the condition is only momentarily True.


    def assert_next_tick_visits_node_id(self, runner: Runner, node_id: str):
        self.assert_next_tick_visits_node_matching(runner, lambda n: n.id == node_id)

    def assert_next_tick_visits_node_matching(self, runner: Runner, node_predicate: Callable[[p.Node], bool]):
        """ Run the next tick and assert that at least one of the visited instructions matches node_predicate """
        logger.info("Running next tick and perform asserts on visited nodes...")
        next_node: p.Node | None = None
        nodes_visited: list[p.Node] = []
        has_match = False

        def on_visit_start(node: p.Node):
            nonlocal has_match, next_node
            next_node = node
            if node_predicate(node):
                has_match = True
            nodes_visited.append(node)

        runner.interpreter.on_visit_start = on_visit_start
        runner.run(max_ticks=1)
        logger.info("Running next tick complete")

        # pylance needs some help here
        next_node = typing.cast(p.Node | None, next_node)

        if next_node is None:
            raise AssertionError("No next instruction was available")
        if not has_match:
            visited_ids = ", ".join([n.id for n in nodes_visited])
            raise AssertionError(f"The next tick did not visit a node matching the predicate. Nodes visited: {visited_ids}")


    def test_ffw_Mark(self):
        code = """\
01 Mark: A
02 Mark: B
03 Mark: C
"""
        interpreter = Interpreter()
        interpreter.set_method(Method.from_numbered_pcode(code))
        runner = Runner(interpreter)

        assert interpreter.program is not None

        runner.run_until(lambda: "A" in interpreter.marks)
        self.assertEqual(["A"], interpreter.marks)
        state = interpreter.get_cold_state()
        self.assertEqual(str(state.main_sep), "root > root.child.0 > 01.Mark")

        interpreter2 = Interpreter.from_cold_state(state)
        runner2 = Runner(interpreter2)

        self.assert_next_tick_visits_node_id(runner2, "02")


    def test_ffw_Block_inside(self):
        code = """\
01 Block: A
02     Mark: B
03     End block
04 Mark: C
"""
        interpreter = Interpreter()
        interpreter.set_method(Method.from_numbered_pcode(code))
        runner = Runner(interpreter)

        assert interpreter.program is not None

        #runner.run()
        runner.run_until(lambda: "B" in interpreter.marks)
        state = interpreter.get_cold_state()
        self.assertEqual(state.main_sep, "root > root.child.0 > 01.Block > 01.Block.child.0 > 02.Mark")

        interpreter2 = Interpreter.from_cold_state(state)
        runner2 = Runner(interpreter2)
        assert interpreter2.program is not None

        self.assert_next_tick_visits_node_id(runner2, "03")

    def test_ffw_Block_End_block(self):
        code = """\
01 Block: A
02     Mark: B
03     End block
04 Mark: C
"""
        interpreter, runner = create(code)
        assert interpreter.program is not None

        end_block_path = "root > root.child.0 > 01.Block > 01.Block.child.1 > 03.End block"
        runner.run_until_path(end_block_path)
        state = interpreter.get_cold_state()
        self.assertEqual(state.main_sep, end_block_path)

        interpreter2 = Interpreter.from_cold_state(state)
        runner2 = Runner(interpreter2)

        self.assert_next_tick_visits_node_id(runner2, "04")

    def test_ffw_Watch(self):
        code = """\
01 Mark: A
02 Watch: true
03     Mark: B
04     Mark: D
05 Mark: C
06 Mark: E
"""
        interpreter = Interpreter()
        interpreter.set_method(Method.from_numbered_pcode(code))
        runner = Runner(interpreter)

        assert interpreter.program is not None

        runner.run_until_path("02.Watch.interrupt > 02.Watch > 02.Watch.invocation")
        self.assertEqual(interpreter.marks, ["A", "C", "B"])

        state = interpreter.get_cold_state()
        interpreter2 = Interpreter.from_cold_state(state)
        runner2 = Runner(interpreter2)
        self.assert_next_tick_visits_node_id(runner2, "04")

    def test_ffw_Alarm(self):
        code = """\
01 Mark: A
02 Alarm: true
03     Mark: B
04     Mark: D
05 Mark: C
06 Mark: E
"""
        interpreter = Interpreter()
        interpreter.set_method(Method.from_numbered_pcode(code))
        runner = Runner(interpreter)

        assert interpreter.program is not None

        runner.run_until_path("02.Alarm.interrupt > 02.Alarm > 02.Alarm.invocation.0")
        self.assertEqual(interpreter.marks, ["A", "C", "B"])

        state = interpreter.get_cold_state()

        # this is just a smoke test
        # Looks a litte strange but is ok. B is always included in the invocation.x path tick
        runner.run_until_path("02.Alarm.interrupt > 02.Alarm > 02.Alarm.invocation.2")
        self.assertEqual(interpreter.marks, ["A", "C", "B", "E", "D", "B", "D", "B"])

        interpreter2 = Interpreter.from_cold_state(state)
        runner2 = Runner(interpreter2)
        self.assert_next_tick_visits_node_id(runner2, "04")

        runner2.run_until_path("02.Alarm.interrupt > 02.Alarm > 02.Alarm.invocation.5")
        self.assertEqual(interpreter2.marks, ["E", "D", "B", "D", "B", "D", "B", "D", "B", "D", "B"])


    def test_ffw_Macro(self):
        code = """\
01 Macro: A
03     Mark: A1
04     Mark: A2
05 Call macro: A
06 Mark: E
"""
        interpreter = Interpreter()
        interpreter.set_method(Method.from_numbered_pcode(code))
        runner = Runner(interpreter)

        assert interpreter.program is not None

        runner.run_until_path("root > root.child.1 > 05.Call macro > 01.Macro.invocation.0 > 01.Macro.child.0 > 03.Mark")
        self.assertEqual(interpreter.marks, ["A1"])

        state = interpreter.get_cold_state()

        # this is just a smoke test
        runner.run_until_path("root > root.child.2 > 06.Mark")
        self.assertEqual(interpreter.marks, ["A1", "A2", "E"])

        interpreter2 = Interpreter.from_cold_state(state)
        runner2 = Runner(interpreter2)
        self.assert_next_tick_visits_node_id(runner2, "04")

        runner2.run()
        self.assertEqual(interpreter2.marks, ["A2", "E"])


# endregion
