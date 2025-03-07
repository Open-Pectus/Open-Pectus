import unittest

from openpectus.lang.grammar.pgrammar import PGrammar
from openpectus.lang.grammar.pprogramformatter import PProgramFormatter, print_program
from openpectus.lang.model.pprogram import (
    PCommandWithDuration,
    PDuration,
    PNode,
    PProgram,
    PBlank,
    PBlock,
    PEndBlock,
    PEndBlocks,
    PWatch,
    PAlarm,
    PMacro,
    PMark,
    PCallMacro,
    PCommand,
    PComment,
    PErrorInstruction,
    PCondition
)


def build(s):
    p = PGrammar()
    p.parse(s)
    return p


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

    def assertNodeHasType(self, node: PNode, expected_type: type):
        if not isinstance(node, expected_type):
            raise AssertionError(f"Invalid node type: {type(node).__name__}, expected: {expected_type.__name__}")

    def test_command(self):
        p = build("foo: bar=baz")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)

        command: PCommand = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(command)
        self.assertEqual("foo", command.name)
        self.assertEqual("bar=baz", command.args)
        # print_program(program)

    def test_start(self):
        p = build("Start")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        command: PCommand = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(command)
        self.assertEqual("Start", command.name)

    def test_increment_run_counter(self):
        p = build("Increment run counter")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        command: PCommand = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(command)
        self.assertEqual("Increment run counter", command.name)

    def test_run_counter(self):
        p = build("Run counter: 4")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        command: PCommand = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(command)
        self.assertEqual("Run counter", command.name)
        self.assertEqual("4", command.args)

    def test_block(self):
        p = build("Block: foo")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        block: PBlock = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(block)
        self.assertEqual("foo", block.name)
        # print_program(program)

    def test_macro(self):
        p = build("Macro: foo")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        macro: PMacro = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(macro)
        self.assertEqual("foo", macro.name)
        # print_program(program)

    @unittest.skip("Fix in #662")
    def test_invalid_macro_with_mark(self):
        p = build("""
Macro:
    Mark: a
""")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        macro: PMacro = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(macro)
        assert isinstance(macro, PMacro)
        self.assertEqual("foo", macro.name)
        mark = macro.children[0]  # type: ignore
        assert isinstance(mark, PMark)
        self.assertEqual("a", mark.name)

    def test_call_macro(self):
        p = build("Call macro: foo")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        call_macro: PCallMacro = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(call_macro)
        self.assertEqual("foo", call_macro.name)
        # print_program(program)

    def test_block_with_end_block(self):
        p = build(
            """Block: foo
    End block"""
        )
        program = p.build_model()
        # p.printSyntaxTree(p.tree)

        block: PBlock = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(block)
        self.assertEqual("foo", block.name)
        # print_program(program)

        end_block = block.get_child_nodes()[0]
        self.assertIsInstance(end_block, PEndBlock)

    def test_block_with_invalid_indentation(self):
        p = build(" Block: foo")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)

        block: PBlock = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(block)
        # print_program(program)
        self.assertIsInstance(block, PBlock)
        self.assertTrue(block.has_error())

    def test_block_with_invalid_scope_indentation(self):
        p = build("    Block: foo")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)

        block: PBlock = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(block)
        # print_program(program)
        self.assertIsInstance(block, PBlock)
        self.assertTrue(block.has_error())

    def test_block_with_end_block_with_invalid_indentation(self):
        p = build(
            """Block: foo
 End block"""
        )
        program = p.build_model()
        # p.printSyntaxTree(p.tree)

        block: PBlock = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(block)
        self.assertEqual("foo", block.name)
        # print_program(program)

        end_block = block.get_child_nodes()[0]
        self.assertIsInstance(end_block, PEndBlock)
        self.assertTrue(end_block.has_error())

    def test_block_with_end_block_with_missing_indentation(self):
        p = build(
            """Block: foo
End block"""
        )
        program = p.build_model()

        block: PBlock = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(block)
        self.assertEqual("foo", block.name)
        # print_program(program, show_errors=True)

        # TODO clarify - do we allow empty blocks?
        # Note: This may not be an error. It is an empty Block, followed
        # by an End block which happens to do nothing. An analyzer
        # might issue a warning about it.
        # The current implementation disallows empty blocks and thus
        # gives an indentation error on End block

        end_block = block.get_child_nodes()[0]
        self.assertIsInstance(end_block, PEndBlock)
        self.assertTrue(end_block.has_error())

    def test_block_with_mark_with_missing_indentation(self):
        p = build(
            """Block: foo
Mark: foo"""
        )
        program = p.build_model()
        # p.printSyntaxTree(p.tree)

        block: PBlock = program.get_instructions()[0]  # type: ignore
        self.assertIsNotNone(block)
        self.assertEqual("foo", block.name)
        # print_program(program, show_errors=True)

        mark = block.get_child_nodes()[0]
        self.assertIsInstance(mark, PMark)
        self.assertTrue(mark.has_error())

        # TODO: Note that Mark in contained in Block. May or may not be what we want in this case.

    def test_block_with_command_and_end_block(self):
        p = build(
            """Block: foo
    cmd: args
    End block"""
        )
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        # print_program(program)

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
        # p.printSyntaxTree(p.tree)
        # print_program(program)

        instructions = program.get_instructions()
        # TODO should program have both instructions? probably not. may have an iterator though
        self.assertEqual(2, len(instructions))
        self.assertIsInstance(instructions[0], PBlock)
        self.assertIsInstance(instructions[1], PCommand)

        block: PBlock = instructions[0]  # type: ignore
        self.assertEqual("Equilibration", block.name)
        self.assertEqual(0, block.indent)
        self.assertIsNone(block.time)
        self.assertFalse(block.has_error())

        cmd1: PCommand = instructions[1]  # type: ignore
        self.assertEqual("Inlet PU01", cmd1.name)
        self.assertEqual("VA01", cmd1.args)
        self.assertEqual(4, cmd1.indent)
        self.assertEqual(0.96, cmd1.time)
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
        # p.printSyntaxTree(p.tree)
        # print_program(program)

        instructions = program.get_instructions()
        self.assertEqual(7, len(instructions))
        self.assertIsInstance(instructions[0], PBlock)
        for i in [1, 2, 3, 4, 5]:
            self.assertIsInstance(instructions[i], PCommand)

        block: PBlock = instructions[0]  # type: ignore
        self.assertEqual("Equilibration", block.name)
        self.assertEqual(0, block.indent)
        self.assertIsNone(block.time)

        cmd1: PCommand = instructions[1]  # type: ignore
        self.assertEqual("Inlet PU01", cmd1.name)
        self.assertEqual("VA01", cmd1.args)
        self.assertEqual(4, cmd1.indent)
        self.assertEqual(0.0, cmd1.time)
        self.assertFalse(cmd1.has_error())

        cmd2: PCommand = instructions[2]  # type: ignore
        self.assertEqual("Inlet PU02", cmd2.name)
        self.assertEqual("VA06", cmd2.args)
        self.assertEqual(4, cmd2.indent)
        self.assertEqual(0.0, cmd2.time)
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
        # p.printSyntaxTree(p.tree)
        # print_program(program)

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

    def test_block_name_non_identifier(self):
        p = build("Block: 87")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        # print_program(program)
        block = program.get_instructions()[0]
        assert isinstance(block, PBlock)
        self.assertEqual(block.name, "87")
        self.assertFalse(program.has_error(recursive=True))

    def test_end_blocks(self):
        p = build("End blocks")
        program = p.build_model()
        instructions = program.get_instructions()
        self.assertIsInstance(instructions[0], PEndBlocks)

    def test_mark(self):
        p = build("Mark: A")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        # print_program(program)
        mark = program.get_instructions()[0]
        assert isinstance(mark, PMark)
        self.assertEqual(mark.name, "A")
        self.assertFalse(program.has_error(recursive=True))

    def test_mark_comment(self):
        p = build("Mark: A # foo")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        # print_program(program)
        mark = program.get_instructions()[0]
        self.assertIsInstance(mark, PMark)
        self.assertEqual(mark.comment, " foo")
        self.assertFalse(program.has_error(recursive=True))

    def test_mark_name_non_identifier(self):
        def test(code: str, name: str):
            with self.subTest(code):
                p = build(code)
                program = p.build_model()
                # p.printSyntaxTree(p.tree)
                # print_program(program)
                mark = program.get_instructions()[0]
                assert isinstance(mark, PMark)
                self.assertEqual(mark.name, name)
                self.assertFalse(program.has_error(recursive=True))

        test("Mark: 87", "87")
        test("Mark: 5 seconds have passed", "5 seconds have passed")
        test("Mark: B %", "B %")

    def test_indentation_error(self):
        code = """
    Mark: A
Mark: B"""
        # test that an indentation error (A) does not interfere with the scope
        # of following instructions (B)
        p = build(code)
        program = p.build_model()
        [a, b] = program.get_instructions()
        # print_program(program, show_errors=True)
        self.assertTrue(a.has_error())
        self.assertFalse(b.has_error())

    def test_blanks(self):
        p = build(
            """
Mark: A
        """
        )
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        # print_program(program)

        non_blanks = program.get_instructions()
        self.assertEqual(1, len(non_blanks))
        self.assertIsInstance(non_blanks[0], PMark)

        all = program.get_instructions(include_blanks=True)
        self.assertEqual(3, len(all))
        self.assertFalse(program.has_error(recursive=True))

    def test_sequential_macros(self):
        p = build(
            """
Macro: 1
    Mark: A1 Start
    Mark: B1 Start
Macro: 2
    Mark: A2 Start
    Mark: B2 Start
    Mark: C2 Start
Call macro: 1
        """
        )
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        # print_program(program)
        self.assertFalse(program.has_error(recursive=True))
        self.assertEqual(0, node_missing_start_position_count(program))

        self.assertProgramMatches(
            program,
            """
PProgram
    PMacro
        PMark
        PMark
    PMacro
        PMark
        PMark
        PMark
    PCallMacro
        """,
        )

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
        # p.printSyntaxTree(p.tree)
        # print_program(program)
        self.assertFalse(program.has_error(recursive=True))
        self.assertEqual(0, node_missing_start_position_count(program))

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

        # print_program(program, show_line_numbers=True)
        self.assertFalse(program.has_error(recursive=True))
        self.assertEqual(0, node_missing_start_position_count(program))

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

        # print_program(program)
        self.assertFalse(program.has_error(recursive=True))
        self.assertEqual(0, node_missing_start_position_count(program))

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

        # print_program(program)
        self.assertFalse(program.has_error(recursive=True))
        self.assertEqual(0, node_missing_start_position_count(program))

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
        # print_program(program)
        cmds = program.get_commands()
        self.assertEqual(6, len(cmds))

    def test_watch(self):
        p = build(
            """
Watch: Run counter > 0
    Mark: A"""
        )
        program = p.build_model()
        [watch, mark_a] = program.get_instructions(include_blanks=False)
        self.assertNodeHasType(watch, PWatch)        
        self.assertNodeHasType(mark_a, PMark)
        self.assertFalse(watch.has_error(recursive=True))
        self.assertIsNone(watch._inst_error)
        assert isinstance(watch, PWatch)
        assert watch.condition is not None
        self.assertEqual(7, watch.condition.start_column)
        self.assertEqual(21, watch.condition.end_column)        
        self.assertEqual(22, len("Watch: Run counter > 0"))
        # note that ranges do not include end_column, so we add 1
        self.assertEqual("Run counter > 0", "Watch: Run counter > 0"[7: 21+1])

    def test_watch_missing_condition(self):
        p = build(
            """
Watch
    Mark: A"""
        )
        program = p.build_model()
        [watch, mark] = program.get_instructions(include_blanks=False)

        self.assertNodeHasType(watch, PWatch)
        self.assertIsNone(watch._inst_error)
        self.assertNodeHasType(mark, PMark)
        self.assertTrue(watch.has_error())

    def test_watch_partial_condition(self):
        p = build(
            """
Watch:
    Mark: A"""
        )
        program = p.build_model()
        [watch, mark] = program.get_instructions(include_blanks=False)
        self.assertNodeHasType(watch, PWatch)
        self.assertNodeHasType(mark, PMark)
        self.assertIsNotNone(watch._inst_error)
        self.assertTrue(watch.has_error())

    def test_watch_partial_condition_w_comment(self):
        p = build(
            """
Watch: # foo
    Mark: A"""
        )
        program = p.build_model()
        [watch, mark] = program.get_instructions(include_blanks=False)
        self.assertNodeHasType(watch, PWatch)
        self.assertEqual(watch.comment, " foo")
        self.assertNodeHasType(mark, PMark)
        self.assertIsNotNone(watch._inst_error)
        self.assertTrue(watch.has_error())

    def test_watch_unit(self):
        p = build(
            """
Mark: a
Watch: counter > 0 mL
    Mark: b
Mark: c
incr counter
Watch: counter > 0 mL
    Mark: d
        """
        )
        program = p.build_model()

        # p.printSyntaxTree(p.tree)
        # print_program(program, show_line_numbers=True, show_errors=True)
        self.assertFalse(program.has_error(recursive=True))
        non_blanks = program.get_instructions()
        self.assertIsInstance(non_blanks[0], PMark)
        self.assertIsInstance(non_blanks[1], PWatch)
        self.assertIsInstance(non_blanks[1].get_child_nodes()[0], PMark)
        assert isinstance(non_blanks[1], PWatch)
        condition = non_blanks[1].condition
        assert condition is not None
        self.assertEqual("counter", condition.tag_name)
        self.assertEqual(">", condition.op)
        self.assertEqual("0", condition.tag_value)
        self.assertEqual("mL", condition.tag_unit)

    def test_watch_unit_percent(self):
        p = build(
            """
Watch: counter > 0 %
    Mark: A
"""
        )
        program = p.build_model()

        # p.printSyntaxTree(p.tree)
        # print_program(program, show_line_numbers=True, show_errors=True)
        self.assertFalse(program.has_error(recursive=True))
        non_blanks = program.get_instructions()
        self.assertIsInstance(non_blanks[0], PWatch)
        self.assertIsInstance(non_blanks[0].get_child_nodes()[0], PMark)
        assert isinstance(non_blanks[0], PWatch)
        condition = non_blanks[0].condition
        assert condition is not None
        self.assertEqual("counter", condition.tag_name)
        self.assertEqual(">", condition.op)
        self.assertEqual("0", condition.tag_value)
        self.assertEqual("%", condition.tag_unit)

    def test_watch_unitless(self):
        p = build(
            """
Mark: a
Watch: counter > 0
    Mark: b
Mark: c
incr counter
Watch: counter > 0
    Mark: d
        """
        )
        program = p.build_model()

        # p.printSyntaxTree(p.tree)
        # print_program(program, show_line_numbers=True, show_errors=True)
        self.assertFalse(program.has_error(recursive=True))
        non_blanks = program.get_instructions()
        self.assertIsInstance(non_blanks[0], PMark)
        self.assertIsInstance(non_blanks[1], PWatch)
        self.assertIsInstance(non_blanks[1].get_child_nodes()[0], PMark)
        assert isinstance(non_blanks[1], PWatch)
        condition = non_blanks[1].condition
        assert condition is not None
        self.assertEqual("counter", condition.tag_name)
        self.assertEqual(">", condition.op)
        self.assertEqual("0", condition.tag_value)
        self.assertEqual(None, condition.tag_unit)

    def test_navigation(self):
        p = build(
            """
Mark: a
Watch: counter > 0
    Mark: b
Mark: c
incr counter
Watch: counter > 0 ml
    Mark: d

        """
        )

        program = p.build_model()

        # print_program(program, show_blanks=True, show_errors=True, show_line_numbers=True)
        self.assertFalse(program.has_error(recursive=True))
        all = program.get_instructions(include_blanks=True)

        blank_1, mark_a, watch_1, mark_b, mark_c, incr, watch_2, mark_d, blank_2, blank_3 = all

        self.assertIsInstance(blank_1, PBlank)
        self.assertEqual(1, blank_1.line)

        self.assertIsInstance(mark_a, PMark)
        self.assertEqual(2, mark_a.line)

        self.assertIsInstance(watch_1, PWatch)
        self.assertEqual(3, watch_1.line)

        self.assertIsInstance(mark_b, PMark)
        self.assertEqual(4, mark_b.line)

        self.assertIsInstance(mark_c, PMark)
        self.assertEqual(5, mark_c.line)

        self.assertIsInstance(incr, PCommand)
        self.assertEqual(6, incr.line)

        self.assertIsInstance(watch_2, PWatch)
        self.assertEqual(7, watch_2.line)

        self.assertIsInstance(mark_d, PMark)
        self.assertEqual(8, mark_d.line)

        self.assertIsInstance(blank_2, PBlank)
        self.assertEqual(9, blank_2.line)

        self.assertIsInstance(blank_3, PBlank)
        self.assertEqual(10, blank_3.line)

    def test_alarm(self):
        p = build(
            """
Mark: A
Alarm: counter > 0
    Mark: b
Mark: c
Increment counter
Mark: d
""")
        program = p.build_model()

        self.assertFalse(program.has_error(recursive=True))
        n_mark_a, n_alarm, n_mark_b, n_mark_c, n_increment, n_mark_d = program.get_instructions()
        self.assertIsInstance(n_alarm, PAlarm)
        self.assertIsInstance(n_mark_a, PMark)
        self.assertIsInstance(n_mark_b, PMark)
        self.assertIsInstance(n_mark_c, PMark)
        self.assertIsInstance(n_mark_d, PMark)
        self.assertIsInstance(n_increment, PCommand)
        self.assertTrue(n_alarm.get_child_nodes()[0], n_mark_b)

        assert isinstance(n_alarm, PAlarm)
        condition = n_alarm.condition
        assert condition is not None
        self.assertEqual("counter", condition.tag_name)
        self.assertEqual(">", condition.op)
        self.assertEqual("0", condition.tag_value)
        self.assertEqual(None, condition.tag_unit)

    def test_program_mark(self):
        p = build(
            """
Mark:  a
        """
        )

        program = p.build_model()
        # print_program(program, show_blanks=True, show_errors=True, show_line_numbers=True)
        self.assertFalse(program.has_error(recursive=True))

    def test_program_watch(self):
        p = build(
            """
Watch A > 0     # missing colon
    Mark: a
        """
        )

        program = p.build_model()
        # print_program(program, show_blanks=True, show_errors=True, show_line_numbers=True)
        self.assertTrue(program.has_error(recursive=True))

    def test_command_comment(self):
        p = build(
            """
mycommand: a  # foo  
        """
        )

        program = p.build_model()
        # print_program(program, show_blanks=True, show_errors=True, show_line_numbers=True)
        self.assertFalse(program.has_error(recursive=True))

        all = program.get_instructions(include_blanks=True)
        blank_1, cmd, blank_2 = all
        self.assertIsInstance(cmd, PCommand)
        self.assertEqual(" foo  ", cmd.comment)

    def test_comment(self):
        p = build(
            """
# foo
# bar # baz
        """
        )

        program = p.build_model()
        # print_program(program, show_blanks=True, show_errors=True, show_line_numbers=True)
        self.assertFalse(program.has_error(recursive=True))

        all = program.get_instructions(include_blanks=True)

        blank_1, comment, comment2, blank_2 = all

        self.assertIsInstance(blank_1, PBlank)
        self.assertEqual(1, blank_1.line)

        self.assertIsInstance(comment, PComment)
        self.assertEqual(2, comment.line)
        self.assertEqual(" foo", comment.comment)

        self.assertIsInstance(comment2, PComment)
        self.assertEqual(3, comment2.line)
        # slight mishap here. we ignore it for now
        self.assertEqual(" bar# baz", comment2.comment)
        # self.assertEqual(" bar # baz", comment2.comment)

    def test_restart(self):
        p = build(
            """
Mark: A
Restart
        """
        )

        program = p.build_model()
        # print_program(program, show_blanks=True, show_errors=True, show_line_numbers=True)
        self.assertFalse(program.has_error(recursive=True))

        all = program.get_instructions(include_blanks=True)
        blank_1, mark, restart, blank_2 = all

        self.assertIsInstance(blank_1, PBlank)
        self.assertEqual(1, blank_1.line)

        self.assertIsInstance(mark, PMark)
        self.assertIsInstance(restart, PCommand)
        assert isinstance(restart, PCommand)
        self.assertEqual(restart.name, "Restart")

    def test_stop(self):
        p = build(
            """
Mark: A
Stop
        """
        )

        program = p.build_model()
        # print_program(program, show_blanks=True, show_errors=True, show_line_numbers=True)
        self.assertFalse(program.has_error(recursive=True))

        all = program.get_instructions(include_blanks=True)
        blank_1, mark, stop, blank_2 = all

        self.assertIsInstance(blank_1, PBlank)
        self.assertEqual(1, blank_1.line)

        self.assertIsInstance(mark, PMark)
        self.assertIsInstance(stop, PCommand)
        assert isinstance(stop,  PCommand)
        self.assertEqual(stop.name, "Stop")

    def test_pause(self):
        p = build("Pause")
        program = p.build_model()
        # print_program(program, show_blanks=True, show_errors=True, show_line_numbers=True)
        self.assertFalse(program.has_error(recursive=True))

        [pause] = program.get_instructions(include_blanks=True)

        self.assertIsInstance(pause, PCommandWithDuration)
        assert isinstance(pause,  PCommandWithDuration)
        self.assertEqual(pause.name, "Pause")
        self.assertEqual(pause.duration, None)

    def test_pause_w_arg(self):
        p = build("Pause: 2 min")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        # print_program(program, show_blanks=True, show_errors=True, show_line_numbers=True)
        self.assertFalse(program.has_error(recursive=True))

        [pause] = program.get_instructions(include_blanks=True)

        self.assertIsInstance(pause, PCommandWithDuration)
        assert isinstance(pause,  PCommandWithDuration)
        self.assertEqual(pause.name, "Pause")
        assert isinstance(pause.duration,  PDuration)
        self.assertEqual(pause.duration.time, 2.0)
        self.assertEqual(pause.duration.unit, "min")


    def test_hold(self):
        p = build("Hold")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        # print_program(program, show_blanks=True, show_errors=True, show_line_numbers=True)
        self.assertFalse(program.has_error(recursive=True))

        [hold] = program.get_instructions(include_blanks=True)

        self.assertIsInstance(hold, PCommandWithDuration)
        assert isinstance(hold,  PCommandWithDuration)
        self.assertEqual(hold.name, "Hold")
        self.assertEqual(hold.duration, None)

    def test_hold_w_arg(self):
        p = build("Hold: 27.35 s")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        # print_program(program, show_blanks=True, show_errors=True, show_line_numbers=True)
        self.assertFalse(program.has_error(recursive=True))

        [hold] = program.get_instructions(include_blanks=True)

        self.assertIsInstance(hold, PCommandWithDuration)
        assert isinstance(hold,  PCommandWithDuration)
        self.assertEqual(hold.name, "Hold")
        assert isinstance(hold.duration,  PDuration)
        self.assertEqual(hold.duration.time, 27.35)
        self.assertEqual(hold.duration.unit, "s")

    def test_hold_w_arg_error(self):
        p = build("Hold: 27.35")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        # print_program(program, show_blanks=True, show_errors=True, show_line_numbers=True)
        self.assertTrue(program.has_error(recursive=True))

        [hold] = program.get_instructions(include_blanks=True)

        self.assertIsInstance(hold, PCommandWithDuration)
        assert isinstance(hold,  PCommandWithDuration)
        self.assertEqual(hold.name, "Hold")
        assert isinstance(hold.duration,  PDuration)
        self.assertTrue(hold.duration.error)
        self.assertEqual(hold.duration.time, None)
        self.assertEqual(hold.duration.unit, None)

    def test_wait_must_have_duration(self):
        p = build("Wait")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        # print_program(program, show_blanks=True, show_errors=True, show_line_numbers=True)
        self.assertEqual(True, program.has_error(recursive=True))

        p = build("Wait: foo")
        program = p.build_model()
        self.assertEqual(True, program.has_error(recursive=True))

        # Not accepting '5x' and requires using units which is currently an analyzer phase
        # concern. Analyzers are not applied at this point
        p = build("Wait: 5x")
        program = p.build_model()
        self.assertEqual(False, program.has_error(recursive=True))

        # and finally, a well formed Wait has no errors
        p = build("Wait: 5s")
        program = p.build_model()
        self.assertEqual(False, program.has_error(recursive=True))

    def test_wait_w_arg(self):
        p = build("Wait:2h")
        program = p.build_model()
        # p.printSyntaxTree(p.tree)
        # print_program(program, show_blanks=True, show_errors=True, show_line_numbers=True)
        self.assertFalse(program.has_error(recursive=True))

        [wait] = program.get_instructions(include_blanks=True)

        self.assertIsInstance(wait, PCommandWithDuration)
        assert isinstance(wait,  PCommandWithDuration)
        self.assertEqual(wait.name, "Wait")
        assert isinstance(wait.duration,  PDuration)
        self.assertEqual(wait.duration.time, 2.0)
        self.assertEqual(wait.duration.unit, "h")
        self.assertFalse(program.has_error(recursive=True))

    def test_info_warning_error(self):
        p = build("""
Info:foo
Warning: bar
Error: baz
""")
        program = p.build_model()
        self.assertFalse(program.has_error(recursive=True))
        [info, warning, error] = program.get_instructions()
        assert isinstance(info, PCommand)
        self.assertEqual(info.args, "foo")
        assert isinstance(warning, PCommand)
        self.assertEqual(warning.args, "bar")
        assert isinstance(error, PCommand)
        self.assertEqual(error.args, "baz")


    @unittest.skip("Need a better error concept for this to make sense")
    def test_program_errors(self):
        p = build(
            """
Mark:  a  
Mark  b  # comment
Watch: counter >  
    Mark: c
Bad command
:
        """
        )

        program = p.build_model()

        # print_program(program, show_blanks=True, show_errors=True, show_line_numbers=True)
        self.assertFalse(program.has_error(recursive=True))
        all = program.get_instructions(include_blanks=True)

        blank_1, mark_a, mark_b, watch, mark_c, bad, err, blank_2 = all

        self.assertIsInstance(blank_1, PBlank)
        self.assertEqual(1, blank_1.line)

        self.assertIsInstance(mark_a, PMark)
        self.assertEqual(2, mark_a.line)

        # Note: this malformed Mark "Mark a" is parsed as command
        # It will still fail command name validation later on, though
        self.assertIsInstance(mark_b, PCommand)
        # self.assertIsInstance(mark_b, PErrorInstruction)
        self.assertEqual(3, mark_b.line)

        self.assertIsInstance(watch, PWatch)
        self.assertEqual(4, watch.line)
        assert isinstance(watch, PWatch)
        assert isinstance(watch.condition, PCondition)
        self.assertTrue(watch.condition.error)

        self.assertIsInstance(mark_c, PMark)
        self.assertEqual(5, mark_c.line)

        self.assertIsInstance(bad, PCommand)
        self.assertEqual(6, bad.line)

        self.assertIsInstance(err, PErrorInstruction)
        self.assertEqual(7, err.line)


if __name__ == "__main__":
    unittest.main()
