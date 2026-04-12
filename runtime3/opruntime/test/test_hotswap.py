
import unittest

from opruntime.test.test_interpreter import create, merge, InterpreterTest, parse_method
from opruntime.lang.hotswap import HotSwapVisitor
from opruntime.lang import program as p
from opruntime.lang.models import serialize

class TestHotswap(unittest.TestCase):

    def test_Abc(self):
        code1 = """\
01 Abc
02 Mark: A
03 
"""

        code2 = """\
01 Abc
02 Mark: A
03 Mark: B
"""

        interpreter, runner = create(code1)        
        assert interpreter.program is not None
        abc = interpreter.program.get_first_child_or_throw(p.AbcNode)

        runner.run_until(lambda: abc.abc_state == "B")

        middle_state = interpreter.get_cold_state()
        interpreter2, runner2 = merge(interpreter, code2)
        assert interpreter2.program is not None

        merge_middle_state = interpreter2.get_cold_state()
        abc2 = interpreter2.program.get_first_child_or_throw(p.AbcNode)

        print("middle_state", serialize(middle_state))
        print("merge_middle_state", serialize(merge_middle_state))

        self.assertEqual(abc2.abc_state, "B")

        # self.assertTreeStateEqual(
        #     middle_state.tree_state,
        #     merge_middle_state.tree_state,
        #     "C:\\mjolner-code\\Novo\\runtime3\\opruntime\\test\\comparison.html"
        # )

    def test_Mark_in_Watch(self):
        code1 = """\
01 Mark: A
02 Watch: true
03     Mark: B
05 Mark: D
"""

        code2 = """\
01 Mark: A
02 Watch: true
03     Mark: B
04     Mark: C
05 Mark: D
"""

        interpreter, runner = create(code1)        
        runner.run_until_path("02.Watch.interrupt > 02.Watch > 02.Watch.invocation > 02.Watch.child.0 > 03.Mark")

        interpreter2, runner2 = merge(interpreter, code2)
        runner2.run()

        self.assertIn("C", interpreter2.marks)

    def test_Abc_in_watch(self):
        code1 = """\
01 Mark: A
02 Watch: true
03     Abc
05 Mark: D
"""

        code2 = """\
01 Mark: A
02 Watch: true
03     Abc
04     Mark: C
05 Mark: D
"""

        interpreter, runner = create(code1)        
        assert interpreter.program is not None
        abc = interpreter.program.get_first_child_or_throw(p.AbcNode)
        runner.run_until_path("02.Watch.interrupt > 02.Watch > 02.Watch.invocation > 02.Watch.child.0 > 03.Abc")
        self.assertEqual(abc.abc_state, "A")

        interpreter2, runner2 = merge(interpreter, code2)
        assert interpreter2.program is not None
        
        # verify that merge has captured Abc custom node state
        abc2 = interpreter2.program.get_first_child_or_throw(p.AbcNode)
        self.assertEqual(abc2.abc_state, "A")
        
        runner2.run()

        self.assertEqual(abc2.abc_state, "C")
