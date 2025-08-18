import json
from typing import Any, TypeVar
import unittest


from openpectus.lang.exec.visitor import NodeGenerator, NodeVisitor
from openpectus.lang.model.parser import PcodeParser
import openpectus.lang.model.ast as p


def create_parser(uod_command_names: list[str] = []) -> PcodeParser:
    return PcodeParser(uod_command_names=uod_command_names)

def parse_program(pcode: str) -> p.ProgramNode:
    return create_parser().parse_pcode(pcode)


# necessary to support python 3.11 in assert_line_parses_as_node_type below
TNode = TypeVar("TNode", bound=p.Node)


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
