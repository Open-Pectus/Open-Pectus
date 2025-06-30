import unittest

from openpectus.lang.exec.analyzer import (
    UnreachableCodeCheckAnalyzer,
    InfiniteBlockCheckAnalyzer,
    IndentationCheckAnalyzer,
    ThresholdCheckAnalyzer,
    WhitespaceCheckAnalyzer,
    ConditionCheckAnalyzer,
    SimulateCheckAnalyzer,
    CommandCheckAnalyzer,
    MacroCheckAnalyzer,
    SemanticCheckAnalyzer,
)
import openpectus.lang.model.ast as p
from openpectus.lang.exec.commands import CommandCollection, Command
from openpectus.lang.exec.tags import TagValueCollection, TagValue
from openpectus.lang.exec.argument_specification import ArgSpec
from openpectus.lang.exec.uod import RegexNamedArgumentParser
from openpectus.test.engine.utility_methods import build_program


class UnreachableCodeCheckAnalyzerTest(unittest.TestCase):
    def test_command_after_end_block(self):
        program = build_program("""
Block: A
    Mark: a
    End block
    Mark: b
Mark: c
""")
        analyzer = UnreachableCodeCheckAnalyzer()
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual(item.range, p.Range(p.Position(4, 4), p.Position(5, 0)))

    def test_command_after_end_blocks(self):
        program = build_program("""
Block: A
    Mark: a
    End blocks
    Mark: b
Mark: c
""")
        analyzer = UnreachableCodeCheckAnalyzer()
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual(item.range, p.Range(p.Position(4, 4), p.Position(5, 0)))

    def test_block_command_after_end_block(self):
        program = build_program("""
Block: A
    Mark: a
    End block
    Block: B
        Mark: b
Mark: c
""")
        analyzer = UnreachableCodeCheckAnalyzer()
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual(item.range, p.Range(p.Position(4, 4), p.Position(6, 0)))

    def test_command_after_stop(self):
        program = build_program("""
Mark: A
Stop
Mark: B
""")
        analyzer = UnreachableCodeCheckAnalyzer()
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual(item.range, p.Range(p.Position(3, 0), p.Position(4, 0)))

    def test_commands_after_stop(self):
        program = build_program("""
Mark: A
Stop
Mark: B

Mark: C
""")
        analyzer = UnreachableCodeCheckAnalyzer()
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual(item.range, p.Range(p.Position(3, 0), p.Position(6, 0)))


class InfiniteBlockCheckAnalyzerTest(unittest.TestCase):
    def test_missing_global_end(self):
        program = build_program("""
Block: A
    Mark: a
Mark: c
""")
        sa = InfiniteBlockCheckAnalyzer()
        sa.analyze(program)
        self.assertEqual(1, len(sa.items))

    def test_missing_end_nested(self):
        program = build_program("""
Block: A
    Block: B
        End block
""")
        sa = InfiniteBlockCheckAnalyzer()
        sa.analyze(program)
        print(sa)
        self.assertEqual(1, len(sa.items))

    def test_nested_end_blocks(self):
        program = build_program("""
Block: A
    Block: B
        End blocks
""")
        sa = InfiniteBlockCheckAnalyzer()
        sa.analyze(program)
        self.assertEqual(0, len(sa.items))

    def test_has_global_end(self):
        program = build_program("""
Watch: Run counter > 0
    End block

Block: A
    Mark: a
Mark: c
""")
        sa = InfiniteBlockCheckAnalyzer()
        sa.analyze(program)
        self.assertEqual(0, len(sa.items))

    def test_has_local_end(self):
        program = build_program("""
Block: A
    Mark: a
    Watch: Run counter > 0
        End block
Mark: c
""")
        sa = InfiniteBlockCheckAnalyzer()
        sa.analyze(program)
        self.assertEqual(0, len(sa.items))

    def test_has_no_local_end(self):
        program = build_program("""
Block: A
    Mark: a
    Watch: Run counter > 0
        End block
Mark: c
Block: B
    Mark: b
""")
        sa = InfiniteBlockCheckAnalyzer()
        sa.analyze(program)
        self.assertEqual(1, len(sa.items))

    def test_end_block_after_not_indented_comment(self):
        program = build_program("""
Block: A
    Mark: B
# Comment in block
    End block
""")
        sa = InfiniteBlockCheckAnalyzer()
        sa.analyze(program)
        self.assertEqual(0, len(sa.items))

    def test_has_stop(self):
        program = build_program("""
Block: A
    Mark: a
    Watch: Run counter > 0
        Stop
Mark: c
""")
        sa = InfiniteBlockCheckAnalyzer()
        sa.analyze(program)
        self.assertEqual(0, len(sa.items))

    def test_has_stop_in_second_warn_about_first(self):
        program = build_program("""
Block: A
    Mark: a

Block: B
    Mark: b
    Stop
""")
        sa = InfiniteBlockCheckAnalyzer()
        sa.analyze(program)
        self.assertEqual(1, len(sa.items))

    def test_has_stop_in_first_warn_about_second(self):
        program = build_program("""
Block: A
    Mark: a
    Stop

Block: B
    Mark: b
""")
        sa = InfiniteBlockCheckAnalyzer()
        sa.analyze(program)
        print(sa.items)
        self.assertEqual(1, len(sa.items))


class IndentationCheckAnalyzerTest(unittest.TestCase):
    def test_incorrect_indented_at_start(self):
        program = build_program("""
 Mark: A
""")
        analyzer = IndentationCheckAnalyzer()
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))

    def test_indented_at_start(self):
        program = build_program("""
    Mark: A
""")
        analyzer = IndentationCheckAnalyzer()
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))

    def test_block_incorrect_body_ok(self):
        program = build_program("""
  Block: A
    Mark: B
    Mark: C
    # Comment in block

# Comment
Mark: D
""")
        analyzer = IndentationCheckAnalyzer()
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual(item.range.start.line, 1)
        self.assertEqual(item.range.end.line, 4)

    def test_block_correct_body_partly_ok(self):
        program = build_program("""
Block: A
     Mark: B
    Mark: C
""")
        analyzer = IndentationCheckAnalyzer()
        analyzer.analyze(program)
        for item in analyzer.items:
            print(item)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual(item.range.start.line, 2)
        self.assertEqual(item.range.end.line, 3)


class ThresholdCheckAnalyzerTest(unittest.TestCase):
    def test_correct_order(self):
        program = build_program("""
0 Mark: A
1 Mark: B

Block: A
    0 Mark: C
    2 Mark: D
    End block

1.5 Mark: C
""")
        analyzer = ThresholdCheckAnalyzer()
        analyzer.analyze(program)
        self.assertEqual(0, len(analyzer.items))

    def test_invalid_order_program_node(self):
        program = build_program("""
1 Mark: A
0 Mark: B
""")
        analyzer = ThresholdCheckAnalyzer()
        analyzer.analyze(program)
        self.assertEqual(2, len(analyzer.items))

    def test_base_supresses_warning(self):
        program = build_program("""
1 Mark: a
Base: L
0 Mark: b
1 Mark: c
""")
        analyzer = ThresholdCheckAnalyzer()
        analyzer.analyze(program)
        self.assertEqual(0, len(analyzer.items))

    def test_base_supresses_first_warning(self):
        program = build_program("""
2 Mark: a
Base: L
1 Mark: b
0 Mark: c
""")
        analyzer = ThresholdCheckAnalyzer()
        analyzer.analyze(program)
        self.assertEqual(2, len(analyzer.items))


class WhitespaceCheckAnalyzerTest(unittest.TestCase):
    def test_leading_whitespace_is_ignored(self):
        program = build_program("""\

Mark: A
""")
        analyzer = WhitespaceCheckAnalyzer()
        analyzer.analyze(program)
        ws_node = program.get_first_child(p.BlankNode)
        assert ws_node is not None

        self.assertEqual(program._last_non_ws_line, 1)
        self.assertEqual(False, ws_node.has_only_trailing_whitespace)

    def test_trailing_whitespace_counted(self):
        program = build_program("""\
Mark: A

""")
        analyzer = WhitespaceCheckAnalyzer()
        analyzer.analyze(program)
        blank_node = program.get_first_child(p.BlankNode)
        assert blank_node is not None

        self.assertEqual(program._last_non_ws_line, 0)
        self.assertEqual(True, blank_node.has_only_trailing_whitespace)

    def test_middle_whitespace(self):
        program = build_program("""\
Mark: A

    # foo
Mark: B""")
        analyzer = WhitespaceCheckAnalyzer()
        analyzer.analyze(program)
        blank_node = program.get_first_child(p.BlankNode)
        assert blank_node is not None

        self.assertEqual(program._last_non_ws_line, 3)
        self.assertEqual(False, blank_node.has_only_trailing_whitespace)

    def test_trailing_whitespace(self):
        program = build_program("""\
Mark: A

# foo
""")
        analyzer = WhitespaceCheckAnalyzer()
        analyzer.analyze(program)
        blank_node = program.get_first_child(p.BlankNode)
        comment_node = program.get_first_child(p.CommentNode)
        assert blank_node is not None
        assert comment_node is not None

        self.assertEqual(program._last_non_ws_line, 0)
        self.assertEqual(True, blank_node.has_only_trailing_whitespace)
        self.assertEqual(True, comment_node.has_only_trailing_whitespace)

    @unittest.skip("this case is postponed, is not well defined")
    def test_trailing_whitespace_in_block(self):
        program = build_program("""\
Block: A
    Mark: B
    

""")
        # hmm can we require that this whitespace is indented correctly?
        # won't we have functionality that depend on this?
        analyzer = WhitespaceCheckAnalyzer()
        analyzer.analyze(program)

        self.assertEqual(2, len(program.children))
        block_node = program.get_first_child(p.BlockNode)
        assert block_node is not None
        blank_node = block_node.get_first_child(p.BlankNode)
        assert blank_node is not None
        comment_node = program.get_first_child(p.CommentNode)
        assert comment_node is not None

        self.assertEqual(program._last_non_ws_line, 0)
        self.assertEqual(True, blank_node.has_only_trailing_whitespace)
        self.assertEqual(True, comment_node.has_only_trailing_whitespace)


class ConditionCheckAnalyzerTest(unittest.TestCase):
    def test_tag_name_defined(self):
        program = build_program("""
Watch: A > 2
    Mark: a
""")
        tags = TagValueCollection([TagValue("A")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(0, len(analyzer.items))

    def test_tag_name_undefined(self):
        program = build_program("""
Watch: A > 2
    Mark: a
""")
        tags = TagValueCollection([])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual("UndefinedTag", item.id)
        self.assertEqual(1, item.range.start.line)
        self.assertEqual(7, item.range.start.character)
        self.assertEqual(1, item.range.end.line)
        self.assertEqual(8, item.range.end.character)

    def test_tag_unit_valid(self):
        program = build_program("""
Watch: A > 2
    Mark: a
""")
        tags = TagValueCollection([TagValue("A")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(0, len(analyzer.items))

    def test_tag_did_you_mean(self):
        program = build_program("""
Watch: Food > 2
    Mark: a
""")
        tags = TagValueCollection([TagValue("Foo")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual(item.data, {"type": "fix-typo", "fix": "Foo"})

    def test_tag_unit_unexpected(self):
        program = build_program("""
Watch: A > 2 mL
    Mark: a
""")
        tags = TagValueCollection([TagValue("A")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("UnexpectedUnit", analyzer.items[0].id)

    def test_tag_unit_missing(self):
        program = build_program("""
Watch: A > 2
    Mark: a
""")
        tags = TagValueCollection([TagValue("A", unit="mL")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("MissingUnit", analyzer.items[0].id)

    def test_tag_units_incompatible(self):
        program = build_program("""
Watch: A > 2 mL
    Mark: a
""")
        tags = TagValueCollection([TagValue("A", unit="s")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("IncompatibleUnits", analyzer.items[0].id)

    def test_tag_unit_invalid(self):
        program = build_program("""
Watch: A > 2 test
    Mark: a
""")
        tags = TagValueCollection([TagValue("A", unit="s")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("InvalidUnit", analyzer.items[0].id)

    def test_tag_units_equal(self):
        program = build_program("""
Watch: A > 2 L
    Mark: a
""")
        tags = TagValueCollection([TagValue("A", unit="L")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(0, len(analyzer.items))

    def test_tag_units_compatible(self):
        program = build_program("""
Watch: A > 2 mL
    Mark: a
""")
        tags = TagValueCollection([TagValue("A", unit="L")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(0, len(analyzer.items))

    def test_tag_unit_CV(self):
        # need to test CV comparison, CV being a custom unit unknown by pint
        program = build_program("""
Watch: A > 2 CV
    Mark: a
""")
        tags = TagValueCollection([TagValue("A", unit="CV")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(0, len(analyzer.items))

    def test_empty_argument(self):
        program = build_program("""
Watch: 
""")
        tags = TagValueCollection([])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("MissingTag", analyzer.items[0].id)

    def test_no_tag(self):
        program = build_program("""
Watch: <
""")
        tags = TagValueCollection([])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("MissingTag", analyzer.items[0].id)

    def test_no_comparison(self):
        program = build_program("""
Watch: A
""")
        tags = TagValueCollection([TagValue("A", unit="s")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("MissingOperator", analyzer.items[0].id)

    def test_no_rhs(self):
        program = build_program("""
Watch: A < 
""")
        tags = TagValueCollection([TagValue("A", unit="s")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("MissingValue", analyzer.items[0].id)

    def test_no_value(self):
        program = build_program("""
Watch: A < h
""")
        tags = TagValueCollection([TagValue("A", unit="s")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("MissingValue", analyzer.items[0].id)


class SimulateCheckAnalyzerTest(unittest.TestCase):
    def test_tag_name_defined(self):
        program = build_program("Simulate: A = 2")
        tags = TagValueCollection([TagValue("A")])
        analyzer = SimulateCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(0, len(analyzer.items))

    def test_tag_name_undefined(self):
        program = build_program("Simulate: A = 2")
        tags = TagValueCollection([])
        analyzer = SimulateCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual("UndefinedTag", item.id)
        self.assertEqual(0, item.range.start.line)
        self.assertEqual(10, item.range.start.character)
        self.assertEqual(0, item.range.end.line)
        self.assertEqual(11, item.range.end.character)

    def test_tag_unit_valid(self):
        program = build_program("Simulate: A = 2")
        tags = TagValueCollection([TagValue("A")])
        analyzer = SimulateCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(0, len(analyzer.items))

    def test_tag_did_you_mean(self):
        program = build_program("Simulate: Food = 2")
        tags = TagValueCollection([TagValue("Foo")])
        analyzer = SimulateCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual(item.data, {"type": "fix-typo", "fix": "Foo"})

    def test_tag_unit_unexpected(self):
        program = build_program("Simulate: A = 2 mL")
        tags = TagValueCollection([TagValue("A")])
        analyzer = SimulateCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("UnexpectedUnit", analyzer.items[0].id)

    def test_tag_unit_missing(self):
        program = build_program("Simulate: A = 2")
        tags = TagValueCollection([TagValue("A", unit="mL")])
        analyzer = SimulateCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("MissingUnit", analyzer.items[0].id)

    def test_tag_units_incompatible(self):
        program = build_program("Simulate: A = 2 mL")
        tags = TagValueCollection([TagValue("A", unit="s")])
        analyzer = SimulateCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("IncompatibleUnits", analyzer.items[0].id)

    def test_tag_unit_invalid(self):
        program = build_program("Simulate: A = 2 test")
        tags = TagValueCollection([TagValue("A", unit="s")])
        analyzer = SimulateCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("InvalidUnit", analyzer.items[0].id)

    def test_tag_units_equal(self):
        program = build_program("Watch: A > 2 L")
        tags = TagValueCollection([TagValue("A", unit="L")])
        analyzer = SimulateCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(0, len(analyzer.items))

    def test_tag_units_compatible(self):
        program = build_program("Watch: A = 2 mL")
        tags = TagValueCollection([TagValue("A", unit="L")])
        analyzer = SimulateCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(0, len(analyzer.items))

    def test_empty_argument(self):
        program = build_program("Simulate: ")
        tags = TagValueCollection([])
        analyzer = SimulateCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("MissingTag", analyzer.items[0].id)

    def test_no_tag(self):
        program = build_program("Simulate: =")
        tags = TagValueCollection([])
        analyzer = SimulateCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("MissingTag", analyzer.items[0].id)

    def test_no_assignment(self):
        program = build_program("Simulate: A")
        tags = TagValueCollection([TagValue("A", unit="s")])
        analyzer = SimulateCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("MissingOperator", analyzer.items[0].id)

    def test_no_rhs(self):
        program = build_program("Simulate: A = ")
        tags = TagValueCollection([TagValue("A", unit="s")])
        analyzer = SimulateCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("MissingValue", analyzer.items[0].id)

    def test_no_value(self):
        program = build_program("Simulate: A = h")
        tags = TagValueCollection([TagValue("A", unit="s")])
        analyzer = SimulateCheckAnalyzer(tags)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("MissingValue", analyzer.items[0].id)


class CommandCheckAnalyzerTest(unittest.TestCase):
    def test_command_defined(self):
        program = build_program("""
Foo
""")
        cmds = CommandCollection().with_cmd(Command("Foo"))
        analyzer = CommandCheckAnalyzer(cmds)
        analyzer.analyze(program)
        self.assertEqual(0, len(analyzer.items))

    def test_command_undefined(self):
        program = build_program("""
Foo
""")
        cmds = CommandCollection()
        analyzer = CommandCheckAnalyzer(cmds)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual(1, item.range.start.line)
        self.assertEqual(0, item.range.start.character)
        self.assertEqual(1, item.range.end.line)
        self.assertEqual(3, item.range.end.character)

    def test_command_undefined_w_arg(self):
        program = build_program("""
Foo: bar
""")
        cmds = CommandCollection()
        analyzer = CommandCheckAnalyzer(cmds)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual(1, item.range.start.line)
        self.assertEqual(0, item.range.start.character)
        self.assertEqual(1, item.range.end.line)
        self.assertEqual(3, item.range.end.character)

    def test_command_arg_valid(self):
        program = build_program("""
Foo: bar
""")
        cmds = CommandCollection().with_cmd(Command("Foo"))
        analyzer = CommandCheckAnalyzer(cmds)
        analyzer.analyze(program)
        self.assertEqual(0, len(analyzer.items))

    def test_command_arg_invalid(self):
        program = build_program("""
Foo: bar
""")
        cmds = CommandCollection().with_cmd(Command("Foo", lambda s: False))
        analyzer = CommandCheckAnalyzer(cmds)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual(1, item.range.start.line)
        self.assertEqual(5, item.range.start.character)
        self.assertEqual(1, item.range.end.line)
        self.assertEqual(8, item.range.end.character)

    def test_did_you_mean(self):
        program = build_program("""
Food: bar
""")
        cmds = CommandCollection().with_cmd(Command("Foo", lambda s: False))
        analyzer = CommandCheckAnalyzer(cmds)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual(item.data, {"type": "fix-typo", "fix": "Foo"})

    def test_command_no_arg(self):
        program = build_program("""
Foo
""")
        cmds = CommandCollection().with_cmd(Command("Foo", arg_parser=RegexNamedArgumentParser(regex=ArgSpec.NoArgsInstance.regex)))
        analyzer = CommandCheckAnalyzer(cmds)
        analyzer.analyze(program)
        self.assertEqual(0, len(analyzer.items))

    def test_command_no_arg_given_arg(self):
        program = build_program("""
Foo: bar
""")
        cmds = CommandCollection().with_cmd(Command("Foo", arg_parser=RegexNamedArgumentParser(regex=ArgSpec.NoArgsInstance.regex)))
        analyzer = CommandCheckAnalyzer(cmds)
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual(item.id, "CommandNoArguments")

class MacroCheckAnalyzerTest(unittest.TestCase):
    def test_valid_unused_macro(self):
        program = build_program("""
Macro: A
    Mark: a
""")
        analyzer = MacroCheckAnalyzer()
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))

    def test_invalid_macro(self):
        program = build_program("""
Macro:
    Mark: a
""")
        analyzer = MacroCheckAnalyzer()
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        print(analyzer.items)

    def test_valid_macro_w_call(self):
        program = build_program("""
Macro: A
    Mark: a
Call macro: A
""")
        analyzer = MacroCheckAnalyzer()
        analyzer.analyze(program)
        self.assertEqual(0, len(analyzer.items))

    def test_invalid_call_macro_to_undefined_macro(self):
        program = build_program("""
Call macro: A
""")
        analyzer = MacroCheckAnalyzer()
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))

    def test_macro_redefined(self):
        program = build_program("""
Macro: A
    Mark: a
Call macro: A
Macro: A
    Mark: b
Call macro: A
""")
        analyzer = MacroCheckAnalyzer()
        analyzer.analyze(program)
        print(analyzer.items)
        self.assertEqual(1, len(analyzer.items))

    def test_macro_redefined_first_definition_not_called(self):
        program = build_program("""
Macro: A
    Mark: a
Macro: A
    Mark: b
Call macro: A
""")
        analyzer = MacroCheckAnalyzer()
        analyzer.analyze(program)
        print(analyzer.items)
        self.assertEqual(2, len(analyzer.items))

    def test_macro_recursive(self):
        program = build_program("""
Macro: A
    Mark: a
    Call macro: A
Call macro: A
""")
        analyzer = MacroCheckAnalyzer()
        analyzer.analyze(program)
        print(analyzer.items)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual(analyzer.items[0].id, "MacroRecursive")

    def test_macro_calls_other_macro(self):
        program = build_program("""
Macro: A
    Macro: B
        Mark: a
    Call macro: B
Call macro: A
""")
        analyzer = MacroCheckAnalyzer()
        analyzer.analyze(program)
        self.assertEqual(0, len(analyzer.items))

    def test_macro_recursive_indirect_nested(self):
        program = build_program("""
Macro: A
    Macro: B
        Mark: a
        Call macro: A
    Call macro: B
Call macro: A
""")
        analyzer = MacroCheckAnalyzer()
        analyzer.analyze(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual(analyzer.items[0].id, "MacroRecursive")

    def test_macro_recursive_indirect_flat(self):
        program = build_program("""
Macro: B
    Mark: B

Macro: A
    Call macro: B

Macro: B
    Call macro: A

Call macro: A
""")
        analyzer = MacroCheckAnalyzer()
        analyzer.analyze(program)
        self.assertIn("MacroRecursive", [item.id for item in analyzer.items])


class SemanticCheckAnalyzerTest(unittest.TestCase):
    def test_basic(self):
        program = build_program("""
Mark: a
Mark: b
Mark: c
""")
        analyzer = SemanticCheckAnalyzer(TagValueCollection([]), CommandCollection())
        analyzer.analyze(program)
        self.assertEqual(0, len(analyzer.errors))

    def test_warning_UnreachableCode(self):
        program = build_program("""
Block: A
    Mark: a
    End block
    Mark: b
Mark: c
""")
        analyzer = SemanticCheckAnalyzer(TagValueCollection([]), CommandCollection())
        analyzer.analyze(program)
        xs = [e for e in analyzer.items if e.id == 'UnreachableCode']
        self.assertEqual(1, len(xs))
