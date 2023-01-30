import unittest

from lang.grammar.pgrammar import PGrammar
from lang.model.pprogram import (
    TimeExp,
    PNode,
    PProgram,
    PInstruction,
    PBlock,
    PEndBlock,
    PEndBlocks,
    PWatch,
    PAlarm,
    PCommand,
    PError
)


def build(s):
    p = PGrammar()
    p.parse(s)
    return p


def print_program(program: PProgram):    
    def print_node(node: PNode, indent: str):
        print(indent + type(node).__name__)
        for child in node.get_child_nodes():
            print_node(child, indent + "  ")

    print_node(program, "")
    print()


class BuilderTest(unittest.TestCase):
    def test_command(self):
        p = build("foo: bar=baz")
        program = p.build_model()
        p.printSyntaxTree(p.tree)
        self.assertIsNotNone(program)

        command: PCommand = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(command)
        self.assertEqual("foo", command.name)
        self.assertEqual("bar=baz", command.args)
        print_program(program)

    def test_block(self):
        p = build("block: foo")
        program = p.build_model()
        p.printSyntaxTree(p.tree)
        self.assertIsNotNone(program)

        block: PBlock = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(block)
        self.assertEqual("foo", block.name)
        print_program(program)

    def test_block_with_end_block(self):
        p = build("""block: foo
    end block""")
        program = p.build_model()
        p.printSyntaxTree(p.tree)
        self.assertIsNotNone(program)

        block: PBlock = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(block)
        self.assertEqual("foo", block.name)
        print_program(program)

        end_block = block.get_child_nodes()[0]
        self.assertIsInstance(end_block, PEndBlock)

    def test_block_with_invalid_indentation(self):
        p = build(" block: foo")
        program = p.build_model()
        p.printSyntaxTree(p.tree)
        self.assertIsNotNone(program)

        block = program.get_instructions()[0]
        self.assertIsNotNone(block)
        print_program(program)

        self.assertIsInstance(block, PError)

    def test_block_with_invalid_scope_indentation(self):
        p = build("    block: foo")
        program = p.build_model()
        p.printSyntaxTree(p.tree)
        self.assertIsNotNone(program)

        block = program.get_instructions()[0]
        self.assertIsNotNone(block)
        print_program(program)

        self.assertIsInstance(block, PError)

    def test_block_with_end_block_with_invalid_indentation(self):
        p = build("""block: foo
 end block""")
        program = p.build_model()
        p.printSyntaxTree(p.tree)
        self.assertIsNotNone(program)

        block: PBlock = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(block)
        self.assertEqual("foo", block.name)
        print_program(program)

        end_block = block.get_child_nodes()[0]
        self.assertIsInstance(end_block, PError)

    def test_block_with_end_block_with_missing_indentation(self):
        p = build("""block: foo
end block""")
        program = p.build_model()
        p.printSyntaxTree(p.tree)
        self.assertIsNotNone(program)

        block: PBlock = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(block)
        self.assertEqual("foo", block.name)
        print_program(program)

        end_block = block.get_child_nodes()[0]
        self.assertIsInstance(end_block, PError)

    def test_block_with_command_and_end_block(self):
        p = build("""block: foo
    cmd: args
    end block""")
        program = p.build_model()
        p.printSyntaxTree(p.tree)
        self.assertIsNotNone(program)
        print_program(program)

        block: PBlock = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(block)
        self.assertEqual("foo", block.name)

        children = block.get_child_nodes()
        assert isinstance(children[0], PCommand)
        cmd = children[0]
        self.assertEqual("cmd", cmd.name)
        self.assertEqual("args", cmd.args)

        assert isinstance(children[1], PEndBlock)

    def test_block_with_command(self):
        p = build(
            """Block: Equilibration
    0.96 Inlet PU01: VA01"""
        )
        program = p.build_model()
        p.printSyntaxTree(p.tree)
        self.assertIsNotNone(program)

        print_program(program)

        instructions = program.get_instructions()
        # TODO should program have both instructions? probably not. may have an iterator though
        self.assertEqual(2, len(instructions))
        self.assertIsInstance(instructions[0], PBlock)
        self.assertIsInstance(instructions[1], PCommand)

        block: PBlock = instructions[0]  # type: ignore
        self.assertEqual("Equilibration", block.name)
        self.assertEqual(0, block.indent)
        self.assertEqual(TimeExp.Empty(), block.time)

        cmd1 : PCommand = instructions[1]  # type: ignore
        self.assertEqual("Inlet PU01", cmd1.name)
        self.assertEqual("VA01", cmd1.args)
        self.assertEqual(4, cmd1.indent)
        self.assertEqual(TimeExp("0.96"), cmd1.time)

    def test_block_Equilibration_partial(self):
        p = build(
            """Block: Equilibration
    0.0 Inlet PU01: VA01
    0.0 Inlet PU02: VA06
    0.0 Inlet PU04: VA15
    0.0 PU01: 77.64 %
    0.0 PU02: 10.00 %
    0.0 PU04: 12.36 %"""
        )
        program = p.build_model()
        p.printSyntaxTree(p.tree)
        self.assertIsNotNone(program)

        print_program(program)

        instructions = program.get_instructions()
        self.assertEqual(7, len(instructions))
        self.assertIsInstance(instructions[0], PBlock)
        for i in [1, 2, 3, 4, 5]:
            self.assertIsInstance(instructions[i], PCommand)

        block: PBlock = instructions[0]  # type: ignore
        self.assertEqual("Equilibration", block.name)
        self.assertEqual(0, block.indent)
        self.assertEqual(TimeExp.Empty(), block.time)

        cmd1 : PCommand = instructions[1]  # type: ignore
        self.assertEqual("Inlet PU01", cmd1.name)
        self.assertEqual("VA01", cmd1.args)
        self.assertEqual(4, cmd1.indent)
        self.assertEqual(TimeExp("0.0"), cmd1.time)

    def test_block_Equilibration(self):
        p = build(
            """Block: Equilibration
    0.0 Inlet PU01: VA01
    0.0 Inlet PU02: VA06
    0.0 Inlet PU04: VA15
    0.0 PU01: 77.64 %
    0.0 PU02: 10.00 %
    0.0 PU04: 12.36 %
    2.95 Zero UV
    3.0 End block"""
        )
        program = p.build_model()
        p.printSyntaxTree(p.tree)
        self.assertIsNotNone(program)

        print_program(program)

        # "Zero UV" is command without args
        # "End block" and such are internal commands
        # check wiki for updated expressions

        instructions = program.get_instructions()
        self.assertIsInstance(instructions[0], PBlock)
        for i in [1, 2, 3, 4, 5, 6, 7]:
            self.assertIsInstance(instructions[i], PCommand)
        self.assertIsInstance(instructions[8], PEndBlock)


if __name__ == "__main__":
    unittest.main()
