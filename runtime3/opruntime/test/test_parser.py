import json
import re
from typing import Any, Type, TypeVar
import unittest


from opruntime.lang.interpreter import Interpreter
import opruntime.lang.program as p
from opruntime.lang.visitor import NodeVisitor
from opruntime.lang.parser import Method, PcodeParser, Grammar

def create_parser(uod_command_names: list[str] = []) -> PcodeParser:
    return PcodeParser(uod_command_names=uod_command_names)

def parse_program(pcode: str) -> p.ProgramNode:
    return create_parser().parse_pcode(pcode)


class TestRegexes(unittest.TestCase):
    def test_indent(self):
        r = re.compile(r'(?P<indent>\s+)?')
        self.assertEqual(r.pattern, Grammar.indent_re)

        m = r.match("")
        assert m is not None

        m = r.match(" ")
        assert m is not None
        self.assertIsNotNone("1", m.groupdict()['indent'])

        m = r.match("       ")
        assert m is not None
        self.assertIsNotNone("7", m.groupdict()['indent'])

    def test_threshold(self):
        r = re.compile(r'((?P<threshold>\d+(\.\d+)?)\s)?')
        self.assertEqual(r.pattern, Grammar.threshold_re)

        m = r.match("5 ")
        assert m is not None
        self.assertIsNotNone("5", m.groupdict()['threshold'])

        m = r.match("5.6 ")
        assert m is not None
        self.assertIsNotNone("5.6", m.groupdict()['threshold'])

    def test_instruction(self):
        r = re.compile(r'(?P<instruction_name>\b[a-zA-Z_][^:#]*)')
        self.assertEqual(r.pattern, Grammar.instruction_re)

        self.assertIsNotNone(r.match("foo"))
        # we require this to be able to distinguish instruction name from threshold
        self.assertIsNone(r.match("1foo"))

    def test_argument(self):
        r = re.compile(r'(: (?P<argument>[^#]+))?')
        self.assertEqual(r.pattern, Grammar.argument_re)

        m = r.match(": bar 27 : ")
        assert m is not None
        self.assertEqual("bar 27 : ", m.groupdict()['argument'])

    def test_instruction_argument(self):
        r = re.compile(r'(?P<instruction_name>\b[a-zA-Z_][^:#]*)(: (?P<argument>[^#]+))?')
        self.assertEqual(r.pattern, Grammar.instruction_re + Grammar.argument_re)

        m = r.match("Foo: bar 27 :")
        assert m is not None
        self.assertEqual("Foo", m.groupdict()['instruction_name'])
        self.assertEqual("bar 27 :", m.groupdict()['argument'])


# necessary to support python 3.11 in assert_line_parses_as_node_type below
TNode = TypeVar("TNode", bound=p.Node)


class TestParser(unittest.TestCase):

    # backport to support python 3.11
    def assert_line_parses_as_node_type(self, line: str, node_type: Type[TNode]) -> TNode:
    #def assert_line_parses_as_node_type[T: p.Node](self, line: str, node_type: Type[T]) -> T:
        parser = create_parser()
        node = parser._parse_line(line, 0)
        self.assertIsInstance(node, node_type)
        assert isinstance(node, node_type)
        return node

    def test_can_parse_empty_line(self):
        self.assert_line_parses_as_node_type("  ", p.BlankNode)

    def test_can_parse_instruction(self):
        line = "Mark"
        node = self.assert_line_parses_as_node_type(line, p.Node)
        self.assertEqual("Mark", node.name_part)

    def test_can_parse_instruction_w_argument(self):
        line = "Mark: A"
        node = self.assert_line_parses_as_node_type(line, p.Node)
        self.assertEqual("Mark", node.name_part)
        self.assertEqual("A", node.arguments_part)

    @unittest.skip("Not implemented. Requires using fallback regex")
    def test_instruction_must_start_with_non_number(self):
        line = "1Mark: A"
        # Fail with something like "1Mark is not a valid command name. Did you mean Mark?"
        node = self.assert_line_parses_as_node_type(line, p.ErrorInstructionNode)
        self.assertEqual("Mark", node.name_part)


    def test_can_parse_instruction_comment(self):
        line = "Mark: A # no comment"
        node = self.assert_line_parses_as_node_type(line, p.Node)
        self.assertEqual("Mark", node.name_part)
        self.assertEqual("A", node.arguments)
        self.assertEqual("no comment", node.comment_part)

    def test_can_parse_threshold_instruction_comment(self):
        line = "1.0 Mark: A # no comment"
        node = self.assert_line_parses_as_node_type(line, p.Node)
        self.assertEqual("Mark", node.name_part)
        self.assertEqual("A", node.arguments)
        self.assertEqual("no comment", node.comment_part)

    def test_can_parse_line(self):
        line = "1.0 Mark: A # no comment"
        node = self.assert_line_parses_as_node_type(line, p.Node)
        self.assertEqual("1.0", node.threshold_part)
        self.assertEqual("Mark", node.name_part)
        self.assertEqual("A", node.arguments)
        self.assertEqual("no comment", node.comment_part)
        self.assertEqual(p.Position(0, 0), node.position)

    def test_can_parse_indent_line(self):
        line = "  1.0 Mark: A # no comment"
        node = self.assert_line_parses_as_node_type(line, p.Node)
        self.assertEqual("1.0", node.threshold_part)
        self.assertEqual("Mark", node.name_part)
        self.assertEqual("A", node.arguments)
        self.assertEqual("no comment", node.comment_part)
        self.assertEqual(p.Position(0, 2), node.position)

    def test_can_parse_mark(self):
        line = "1.0 Mark: A # no comment"
        node = self.assert_line_parses_as_node_type(line, p.MarkNode)
        self.assertEqual("1.0", node.threshold_part)
        self.assertEqual("Mark", node.name_part)
        self.assertEqual("A", node.arguments)
        self.assertEqual("no comment", node.comment_part)
        self.assertEqual(p.Position(0, 0), node.position)

    def test_can_parse_line_block(self):
        line = "Block: A"
        _ = self.assert_line_parses_as_node_type(line, p.BlockNode)

    def test_can_detect_indent_error(self):

        def check(line: str, expectError: bool):
            with self.subTest(f"{line} | {expectError}"):
                node = self.assert_line_parses_as_node_type("", p.Node)
                self.assertFalse(node.indent_error)

        check("Mark", False)
        check("    Mark", False)
        check("        Mark", False)
        check(" Mark", True)
        check("  Mark", True)
        check("   Mark", True)
        check("       Mark", True)
        check("         Mark", True)


    def test_can_parse_block(self):
        code = """
Block: A
    Mark: B
"""

        program = parse_program(code)
        block = program.get_first_child(p.BlockNode)
        assert block is not None

    def test_can_parse_block_w_blanks(self):
        code = """
Block: A
    Mark: B

    Mark: C
"""

        program = parse_program(code)
        block = program.get_first_child(p.BlockNode)
        assert block is not None
        self.assertEqual(3, len(block.children))

    def test_can_parse_demo(self):
        code = """
Mark
Block: A
    Mark: B
    End block
Mark: C
"""
        program = parse_program(code)

        print(program)

    def test_can_parse_watch(self):
        code = """
Watch: Run Counter > 0
    Mark: B
"""

        program = parse_program(code)
        watch = program.get_first_child(p.WatchNode)
        assert watch is not None
        self.assertEqual("Run Counter > 0", watch.condition_part)
        assert watch.condition is not None
        self.assertEqual(">", watch.condition.op)
        self.assertEqual("Run Counter", watch.condition.lhs)
        self.assertEqual("0", watch.condition.rhs)
        self.assertEqual(False, watch.condition.error)

    def test_parse_condition(self):
        def check(condition_part: str, expected_valid: bool):
            with self.subTest(condition_part + " | " + str(expected_valid)):
                watch = p.WatchNode()
                watch.arguments_part = condition_part
                PcodeParser._parse_condition(node=watch)
                assert watch.condition is not None
                self.assertEqual(expected_valid, not watch.condition.error)

        # rhs must be int or float optionally followed by a unit
        check("Run Count > 0", True)
        check("x>0.98", True)
        check("x > 0.98 cm", True)
        check("x > 0.98cm", True)
        check("x > 5m2 ", True)
        check("x > 5%", True)

        # these are accepted because 0.98 is treated as a string
        # analyzers may consider this an error later on
        check("x>0,98", True)
        check(" x == 0,98 ", True)
        check(" foo == bar ", True)

        check(" foo ==  ", False)
        check("foo  ", False)
        check(" foo", False)

    def test_can_parse_alarm(self):
        code = """
Alarm: Foo > 0
    Stop
"""

        program = parse_program(code)
        alarm = program.get_first_child(p.AlarmNode)
        assert alarm is not None
        self.assertEqual("Foo > 0", alarm.condition_part)
        assert alarm.condition is not None
        self.assertEqual(">", alarm.condition.op)
        self.assertEqual("Foo", alarm.condition.lhs)
        self.assertEqual("0", alarm.condition.rhs)
        self.assertEqual(False, alarm.condition.error)

    def test_get_condition_ranges(self):
        parser = create_parser()

        code = """\
Alarm: Foo > 0
    Stop
"""
        program = parser.parse_pcode(code)
        alarm = program.get_first_child(p.AlarmNode)
        assert alarm is not None
        assert alarm.condition is not None

        self.assertEqual(7, alarm.condition.range.start.character)
        self.assertEqual(14, alarm.condition.range.end.character)

        self.assertEqual(7, alarm.condition.lhs_range.start.character)
        self.assertEqual(10, alarm.condition.lhs_range.end.character)

        self.assertEqual(11, alarm.condition.op_range.start.character)
        self.assertEqual(12, alarm.condition.op_range.end.character)

        self.assertEqual(13, alarm.condition.rhs_range.start.character)
        self.assertEqual(14, alarm.condition.rhs_range.end.character)

    @unittest.skip("not important now")
    def test_get_condition_ranges_alt_ws(self):
        parser = create_parser()

        code = """\
Alarm:  Foo   >=  0.4  
    Stop
"""
        program = parser.parse_pcode(code)
        alarm = program.get_first_child(p.AlarmNode)
        assert alarm is not None
        assert alarm.condition is not None

        self.assertEqual(8, alarm.condition.range.start.character)
        self.assertEqual(21, alarm.condition.range.end.character)

        self.assertEqual(8, alarm.condition.lhs_range.start.character)
        #self.assertEqual(11, alarm.condition.lhs_range.end.character)

        self.assertEqual(14, alarm.condition.op_range.start.character)
        self.assertEqual(16, alarm.condition.op_range.end.character)

        # working with these indices is a horrible mess. it's also not important

        #self.assertEqual(18, alarm.condition.rhs_range.start.character)
        self.assertEqual(21, alarm.condition.rhs_range.end.character)

    def test_engine_command(self):
        parser = create_parser()
        code = "Stop"
        program = parser.parse_pcode(code)
        stop = program.get_first_child(p.EngineCommandNode)
        assert stop is not None

    def test_invalid_command(self):
        parser = create_parser()
        code = "Bar"
        program = parser.parse_pcode(code)
        bar = program.get_first_child(p.ErrorInstructionNode)
        assert bar is not None

    def test_uod_command(self):
        parser = create_parser(["Reset"])
        code = "Reset"
        program = parser.parse_pcode(code)
        reset = program.get_first_child(p.UodCommandNode)
        assert reset is not None

    def test_parse_blocks(self):
        code = """\
Block: A
    Mark: B
Block: C
    Mark: D
"""
        program = parse_program(code)
        print(program.as_tree())
        block_a = program.children[0]
        assert isinstance(block_a, p.BlockNode)
        mark_b = block_a.children[0]
        assert isinstance(mark_b, p.MarkNode)

        block_c = program.children[1]
        assert isinstance(block_c, p.BlockNode)
        mark_d = block_c.children[0]
        assert isinstance(mark_d, p.MarkNode)


    def test_parse_block_w_blank_4(self):
        code = """\
Block: A
    Mark: B

    Mark: C
Mark: x
"""

        program = parse_program(code)
        self.assertEqual(2, len(program.children))

        block_node = program.children[0]
        assert isinstance(block_node, p.BlockNode)
        self.assertIsInstance(block_node.children[0], p.MarkNode)
        self.assertIsInstance(block_node.children[1], p.BlankNode)
        self.assertIsInstance(block_node.children[2], p.MarkNode)

        mark_x = program.children[1]
        self.assertIsInstance(mark_x, p.MarkNode)


    def test_block_with_blanks(self):
        code = """\
Mark: A
Block: B
    Mark: B1
    Mark: B2
    
    End block
Mark: C
"""
        program = parse_program(code)
        print(program.as_tree())
        self.assertEqual(3, len(program.children))
        block = program.children[1]
        assert isinstance(block, p.BlockNode)
        self.assertEqual(4, len(block.children))

    def test_parse(self):
        code = """\
01 Mark: A
02 Block: B
03     Mark: B1
04     Mark: B2
05     Mark: B3
06     End block
07 Mark: C
08 Mark: D
"""
        method = Method.from_numbered_pcode(code)
        program = parse_program(method.as_pcode())
        self.assertEqual(False, program.has_error(recursive=True))

    def test_parse_nested_blocks(self):
        code = """\
Block: A
    Mark: B
    Block: C
        Mark: D
        End block
Block: E
    Block: F
        End blocks
    Mark: G
"""
        program = parse_program(code)
        print(program.as_tree())
        block_a = program.children[0]
        block_e = program.children[1]
        assert isinstance(block_a, p.BlockNode)
        assert isinstance(block_e, p.BlockNode)

        mark_b = block_a.children[0]
        assert isinstance(mark_b, p.MarkNode)
        block_c = block_a.children[1]
        assert isinstance(block_c, p.BlockNode)
        mark_d = block_c.children[0]
        assert isinstance(mark_d, p.MarkNode)

        block_f = block_e.children[0]
        assert isinstance(block_f, p.BlockNode)
        endblocks_f = block_f.children[0]
        assert isinstance(endblocks_f, p.EndBlocksNode)

        mark_g = block_e.children[1]
        assert isinstance(mark_g, p.MarkNode)


class TestVisitor(unittest.TestCase):
    def test_can_visit_demo(self):
        code = """
Mark
Block: A
    Mark: B
    End block
Mark: C
"""
        program = parse_program(code)
        visitor = NodeVisitor()
        for node in visitor.visit(program):
            print(node)


    def test_can_navigate_demo(self):
        code = """
Mark
Block: A
    Mark: B
    End block
Mark: C
"""
        program = parse_program(code)

        visitor = NodeVisitor()
        for node in visitor.visit(program):
            print(node)
            print(".")

    def test_extract_state(self):
        code = """
Mark: A
Block: BA
    Mark: B
    Block: BB
        Mark: C
        End block
    Mark: D
    End block
Mark: E
Mark: F
"""
        program = parse_program(code)
        state = program.extract_tree_state()
        dump = json.dumps(state, indent=2)
        print(dump)

    def test_dict_serializability(self):

        class Foo(dict[str, Any]):
            a: str
            b: int

        foo = Foo(a="a", b=21)
        print("foo", foo)

        dump = json.dumps(foo, indent=2)
        print("dump", dump)

        bar = Foo(eval(dump))
        print("bar", bar)

        # adding untyped values
        foo["c"] = 0
        print("foo", foo)


    def test_interpreter(self):
        code = """
Mark: A
Block: Block
    Mark: B
    End block
Mark: C
Mark: D
"""
        interpreter = Interpreter()
        method = Method.from_pcode(code)
        interpreter.set_method(method)

        tick_no = 0
        for _ in range(50):
            interpreter.tick(0, tick_number=tick_no)
            tick_no += 1
