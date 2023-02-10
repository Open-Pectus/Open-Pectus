import unittest

from lang.grammar.pgrammar import PGrammar
from lang.model.pprogram import (
    TimeExp,
    PNode,
    PProgram,
    PBlock,
    PEndBlock,
    # PEndBlocks,
    PWatch,
    # PAlarm,
    PMark,
    PCommand,
    PCondition
)

from lang.grammar.pprogramformatter import PProgramFormatter, FormattingOptions


def build(s):
    p = PGrammar()
    p.parse(s)
    return p


def print_program(
    program: PProgram, show_line_numbers: bool = False, show_errors: bool = False
):
    opts = FormattingOptions()
    opts.line_numbers = show_line_numbers
    opts.errors = show_errors
    out = PProgramFormatter(opts).format(program)
    print("\n")
    print(out)


def node_missing_start_position_count(node: PNode) -> int:
    count = 0
    if node.line is None:
        count += 1
    if node.indent is None:
        count += 1
    for n in node.get_child_nodes(recursive=True):
        count += node_missing_start_position_count(n)
    return count


class BuilderTest(unittest.TestCase):
    def assertProgramMatches(self, program: PProgram, expected: str):
        expected = expected.strip()
        out = PProgramFormatter().format(program)
        self.assertMultiLineEqual(expected, out)

    def test_command(self):
        p = build("foo: bar=baz")
        program = p.build_model()
        p.printSyntaxTree(p.tree)

        command: PCommand = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(command)
        self.assertEqual("foo", command.name)
        self.assertEqual("bar=baz", command.args)
        print_program(program)

    def test_block(self):
        p = build("block: foo")
        program = p.build_model()
        p.printSyntaxTree(p.tree)

        block: PBlock = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(block)
        self.assertEqual("foo", block.name)
        print_program(program)

    def test_block_with_end_block(self):
        p = build(
            """block: foo
    end block"""
        )
        program = p.build_model()
        p.printSyntaxTree(p.tree)

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

        block: PBlock = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(block)
        print_program(program)
        self.assertIsInstance(block, PBlock)
        self.assertTrue(block.has_error())

    @unittest.skip(
        "TODO error handling decision. should an instruction with errors affect the following lines?"
    )
    def test_block_with_invalid_scope_indentation(self):
        p = build("    block: foo")
        program = p.build_model()
        p.printSyntaxTree(p.tree)

        block: PBlock = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(block)
        print_program(program)
        self.assertIsInstance(block, PBlock)
        self.assertTrue(block.has_error())

    def test_block_with_end_block_with_invalid_indentation(self):
        p = build(
            """block: foo
 end block"""
        )
        program = p.build_model()
        p.printSyntaxTree(p.tree)

        block: PBlock = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(block)
        self.assertEqual("foo", block.name)
        print_program(program)

        end_block = block.get_child_nodes()[0]
        self.assertIsInstance(end_block, PEndBlock)
        self.assertTrue(end_block.has_error())

    @unittest.skip("TODO error handling decision. May not be an error")
    def test_block_with_end_block_with_missing_indentation(self):
        p = build(
            """block: foo
end block"""
        )
        program = p.build_model()
        p.printSyntaxTree(p.tree)

        block: PBlock = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(block)
        self.assertEqual("foo", block.name)
        print_program(program)

        end_block = block.get_child_nodes()[0]
        self.assertIsInstance(end_block, PEndBlock)
        self.assertTrue(end_block.has_error())

    def test_block_with_mark_with_missing_indentation(self):
        p = build(
            """block: foo
mark: foo"""
        )
        program = p.build_model()
        p.printSyntaxTree(p.tree)

        block: PBlock = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(block)
        self.assertEqual("foo", block.name)
        print_program(program, show_errors=True)

        mark = block.get_child_nodes()[0]
        self.assertIsInstance(mark, PMark)
        self.assertTrue(mark.has_error())

        # TODO: Note that Mark in contained in Block. May or may not be what we want in this case.

    def test_block_with_command_and_end_block(self):
        p = build(
            """block: foo
    cmd: args
    end block"""
        )
        program = p.build_model()
        p.printSyntaxTree(p.tree)
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
        self.assertFalse(block.has_error())

        cmd1: PCommand = instructions[1]  # type: ignore
        self.assertEqual("Inlet PU01", cmd1.name)
        self.assertEqual("VA01", cmd1.args)
        self.assertEqual(4, cmd1.indent)
        self.assertEqual(TimeExp("0.96"), cmd1.time)
        self.assertFalse(cmd1.has_error())

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

        cmd1: PCommand = instructions[1]  # type: ignore
        self.assertEqual("Inlet PU01", cmd1.name)
        self.assertEqual("VA01", cmd1.args)
        self.assertEqual(4, cmd1.indent)
        self.assertEqual(TimeExp("0.0"), cmd1.time)
        self.assertFalse(cmd1.has_error())

        cmd2: PCommand = instructions[2]  # type: ignore
        self.assertEqual("Inlet PU02", cmd2.name)
        self.assertEqual("VA06", cmd2.args)
        self.assertEqual(4, cmd2.indent)
        self.assertEqual(TimeExp("0.0"), cmd2.time)
        self.assertFalse(cmd2.has_error())

    def test_block_Equilibration(self):
        p = build("""
Block: Equilibration
    0.0 Inlet PU01: VA01
    0.0 Inlet PU02: VA06
    0.0 Inlet PU04: VA15
    0.0 PU01: 77.64 %
    0.0 PU02: 10.00 %
    0.0 PU04: 12.36 %
    2.95 Zero UV
    3.0 End block
    """)

        program = p.build_model()
        p.printSyntaxTree(p.tree)

        print_program(program)

        # check wiki for updated expressions

        instructions = program.get_instructions()
        self.assertIsInstance(instructions[0], PBlock)
        for i in [1, 2, 3, 4, 5, 6, 7]:
            instr = instructions[i]
            self.assertIsInstance(instr, PCommand)
            self.assertFalse(instr.has_error())
        instr = instructions[8]
        self.assertIsInstance(instr, PEndBlock)
        self.assertFalse(instr.has_error())

    def test_mark(self):
        p = build("Mark: A")
        program = p.build_model()
        p.printSyntaxTree(p.tree)

        print_program(program)
        mark = program.get_instructions()[0]
        self.assertIsInstance(mark, PMark)
        self.assertFalse(program.has_error(recursive=True))

    def test_blanks(self):
        p = build(
            """
Mark: A
        """
        )
        program = p.build_model()
        p.printSyntaxTree(p.tree)

        print_program(program)

        non_blanks = program.get_instructions()
        self.assertEqual(1, len(non_blanks))
        self.assertIsInstance(non_blanks[0], PMark)

        all = program.get_instructions(include_blanks=True)
        self.assertEqual(3, len(all))
        self.assertFalse(program.has_error(recursive=True))

    def test_sequential_blocks(self):
        p = build(
            """
Block: A1
    Mark: A1 Start
    End block
Block: A2
    Mark: A2 Start
    End block
        """
        )
        program = p.build_model()
        p.printSyntaxTree(p.tree)

        print_program(program)
        self.assertFalse(program.has_error(recursive=True))
        self.assertEquals(0, node_missing_start_position_count(program))

        self.assertProgramMatches(
            program,
            """
PProgram
    PBlock
        PMark
        PEndBlock
    PBlock
        PMark
        PEndBlock
        """,
        )

    def test_nested_blocks(self):
        p = build(
            """
Block: A
    Mark: A Start
    Block: A1
        Mark: A1 Start
        End block
    Block: A2
        Mark: A2 Start
        End block
    Mark: A End
    End block
        """
        )
        program = p.build_model()

        print_program(program, show_line_numbers=True)
        self.assertFalse(program.has_error(recursive=True))
        self.assertEquals(0, node_missing_start_position_count(program))

        self.assertProgramMatches(
            program,
            """
PProgram
    PBlock
        PMark
        PBlock
            PMark
            PEndBlock
        PBlock
            PMark
            PEndBlock
        PMark
        PEndBlock
        """,
        )

    def test_outdent(self):
        p = build(
            """
Block: A1
    Mark: A1 Start
Mark: foo
"""
        )
        program = p.build_model()

        print_program(program)
        self.assertFalse(program.has_error(recursive=True))
        self.assertEquals(0, node_missing_start_position_count(program))

        self.assertProgramMatches(
            program,
            """
PProgram
    PBlock
        PMark
    PMark
""",
        )

    def test_outdent_multiple(self):
        p = build(
            """
Block: A
    Mark: A Start
    Block: A1
        Mark: A1 Start
Mark: foo
"""
        )
        program = p.build_model()

        print_program(program)
        self.assertFalse(program.has_error(recursive=True))
        self.assertEquals(0, node_missing_start_position_count(program))

        self.assertProgramMatches(
            program,
            """
PProgram
    PBlock
        PMark
        PBlock
            PMark
    PMark
""",
        )

    def test_commands(self):
        p = build(
            """
Incr_counter
Incr counter
Incr_counter: foo
Incr counter: foo
Incr_counter: foo=bar
Incr counter: foo='bar',2
"""
        )
        # Note: grammer seems to require cmd_args with colon - otherwise the following line break causes error
        # This may be a problem when typing live
        program = p.build_model()
        print_program(program)
        cmds = program.get_commands()
        self.assertEqual(6, len(cmds))

    def test_watch(self):
        p = build(
            """
Watch: 1
    Mark: A
        """
        )
        program = p.build_model()

        print_program(program)

        non_blanks = program.get_instructions()
        self.assertIsInstance(non_blanks[0], PWatch)
        mark = non_blanks[0].get_child_nodes()[0]
        self.assertIsInstance(mark, PMark)
        self.assertFalse(program.has_error(recursive=True))

    def test_watch2(self):
        p = build(
            """
mark: a
watch: counter > 0
    mark: b
mark: c
incr counter
watch: counter > 0
    mark: d
        """
        )
        program = p.build_model()

        print_program(program)
        self.assertFalse(program.has_error(recursive=True))
        non_blanks = program.get_instructions()
        self.assertIsInstance(non_blanks[0], PMark)
        self.assertIsInstance(non_blanks[1], PWatch)
        self.assertIsInstance(non_blanks[1].get_child_nodes()[0], PMark)


class PConditionTest(unittest.TestCase):
    def test_parse(self):
        c = PCondition("foo>3")
        c.parse()
        self.assertEqual("foo", c.lhs)
        self.assertEqual(">", c.op)
        self.assertEqual("3", c.rhs)

        c = PCondition("foo>=3")
        c.parse()
        self.assertEqual("foo", c.lhs)
        self.assertEqual(">=", c.op)
        self.assertEqual("3", c.rhs)

        c = PCondition("foo != 3 ")
        c.parse()
        self.assertEqual("foo", c.lhs)
        self.assertEqual("!=", c.op)
        self.assertEqual("3", c.rhs)


if __name__ == "__main__":
    unittest.main()
