import unittest

from lang.grammar.pgrammar import PGrammar
from lang.model.pprogram import TimeExp, PProgram, PBlock, PCommand


def build(s):
    p = PGrammar()
    p.parse(s)
    return p


def print_program(program: PProgram):
    print(type(program).__name__)
    for i in program.get_instructions():
        indent = ""
        for x in range(i.indent):
            indent += " "
        print(indent + type(i).__name__)


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

    def test_block_command(self):
        p = build(
            """Block: Equilibration
    0.96 Inlet PU01: VA01"""
        )
        program = p.build_model()
        p.printSyntaxTree(p.tree)
        self.assertIsNotNone(program)

        print_program(program)

        instructions = program.get_instructions()
        # TODO should program have both instructions? probably not. may have an iterator
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

    @unittest.skip("To be defined")
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

        instructions = program.get_instructions()
        self.assertIsInstance(instructions[0], PBlock)
        for i in [1, 2, 3, 4, 5, 6, 7]:
            self.assertIsInstance(instructions[i], PCommand)


if __name__ == "__main__":
    unittest.main()
