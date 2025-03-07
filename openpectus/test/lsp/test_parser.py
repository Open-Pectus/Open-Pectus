
import re
from typing import Sequence, Type, TypeVar
import unittest

from openpectus.lsp.new_parser.parser import PcodeParser, Grammar
import openpectus.lsp.new_parser.program as p


def create_parser() -> PcodeParser:
    return PcodeParser(grammar=Grammar())

def parse_program(lines: Sequence[str]) -> p.ProgramNode:
    return create_parser().parse_program(lines)


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
        lines = []
        node = parser.parseline(line, 0, lines)
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

    # def test_instruction_must_start_with_non_number(self):
    #     line = "1Mark: A"
    #     # Fail with something like "1Mark is not a valid command name. Did you mean Mark?"
    #     node = self.assert_line_parses_as_node_type(line, p.ErrorInstructionNode)
    #     self.assertEqual("Mark", node.name_part)


    def test_can_parse_instruction_comment(self):
        line = "Mark: A # no comment"
        node = self.assert_line_parses_as_node_type(line, p.Node)
        self.assertEqual("Mark", node.name_part)
        self.assertEqual("A", node.arguments_part)
        self.assertEqual("no comment", node.comment_part)

    def test_can_parse_threshold_instruction_comment(self):
        line = "1.0 Mark: A # no comment"
        node = self.assert_line_parses_as_node_type(line, p.Node)
        self.assertEqual("Mark", node.name_part)
        self.assertEqual("A", node.arguments_part)
        self.assertEqual("no comment", node.comment_part)

    def test_can_parse_line(self):
        line = "1.0 Mark: A # no comment"
        node = self.assert_line_parses_as_node_type(line, p.Node)
        self.assertEqual("1.0", node.threshold_part)
        self.assertEqual("Mark", node.name_part)
        self.assertEqual("A", node.arguments_part)
        self.assertEqual("no comment", node.comment_part)
        self.assertEqual(p.Position(0, 0), node.position)

    def test_can_parse_indent_line(self):
        line = "  1.0 Mark: A # no comment"
        node = self.assert_line_parses_as_node_type(line, p.Node)
        self.assertEqual("1.0", node.threshold_part)
        self.assertEqual("Mark", node.name_part)
        self.assertEqual("A", node.arguments_part)
        self.assertEqual("no comment", node.comment_part)
        self.assertEqual(p.Position(0, 2), node.position)

    def test_can_parse_mark(self):
        line = "1.0 Mark: A # no comment"
        node = self.assert_line_parses_as_node_type(line, p.MarkNode)
        self.assertEqual("1.0", node.threshold_part)
        self.assertEqual("Mark", node.name_part)
        self.assertEqual("A", node.arguments_part)
        self.assertEqual("no comment", node.comment_part)
        self.assertEqual(p.Position(0, 0), node.position)

    def test_can_parse_line_block(self):
        line = "Block: A"
        _ = self.assert_line_parses_as_node_type(line, p.BlockNode)

    def test_can_detect_indent_error(self):

        def check(line: str, expectError: bool):
            with self.subTest(f"{line}: {expectError}"):
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
        lines = """
Block: A
    Mark: B
""".splitlines()

        program = parse_program(lines)
        block = program.get_first_child(p.BlankNode)
        assert block is not None


    def test_can_parse_demo(self):
        lines = """
Mark
Block: A
    Mark: B
    End block
Mark: C
""".splitlines()
        program = parse_program(lines)

        print(program)
