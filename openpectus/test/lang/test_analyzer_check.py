import unittest

from openpectus.lang.exec.analyzer import (
    MacroCheckAnalyzer,
    SemanticCheckAnalyzer,
    UnreachableCodeCheckAnalyzer,
    InfiniteBlockCheckAnalyzer,
    ConditionCheckAnalyzer,
    CommandCheckAnalyzer,
)
from openpectus.lang.exec.commands import CommandCollection, Command
from openpectus.lang.exec.tags import TagValueCollection, TagValue
from openpectus.test.engine.utility_methods import build_program


# TODO present PErrorInstructions as errors
# TODO present PErrors as errors

class CommandCheckAnalyzerTest(unittest.TestCase):
    def test_command_defined(self):
        program = build_program("""
Foo
""")
        cmds = CommandCollection().with_cmd(Command("Foo"))
        analyzer = CommandCheckAnalyzer(cmds)
        analyzer.visit(program)
        self.assertEqual(0, len(analyzer.items))

    def test_command_undefined(self):
        program = build_program("""
Foo
""")
        cmds = CommandCollection()
        analyzer = CommandCheckAnalyzer(cmds)
        analyzer.visit(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual(2, item.range_start.line)
        self.assertEqual(0, item.range_start.character)
        self.assertEqual(2, item.range_end.line)
        self.assertEqual(3, item.range_end.character)

    def test_command_undefined_w_arg(self):
        program = build_program("""
Foo: bar
""")
        cmds = CommandCollection()
        analyzer = CommandCheckAnalyzer(cmds)
        analyzer.visit(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual(2, item.range_start.line)
        self.assertEqual(0, item.range_start.character)
        self.assertEqual(2, item.range_end.line)
        self.assertEqual(3, item.range_end.character)

    def test_command_arg_valid(self):
        program = build_program("""
Foo: bar
""")
        cmds = CommandCollection().with_cmd(Command("Foo"))
        analyzer = CommandCheckAnalyzer(cmds)
        analyzer.visit(program)
        self.assertEqual(0, len(analyzer.items))

    def test_command_arg_invalid(self):
        program = build_program("""
Foo: bar
""")
        cmds = CommandCollection().with_cmd(Command("Foo", lambda s: False))
        analyzer = CommandCheckAnalyzer(cmds)
        analyzer.visit(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual(2, item.range_start.line)
        self.assertEqual(5, item.range_start.character)
        self.assertEqual(2, item.range_end.line)
        self.assertEqual(8, item.range_end.character)

class ConditionCheckAnalyzerTest(unittest.TestCase):
    def test_tag_name_defined(self):
        program = build_program("""
Watch: A > 2
    Mark: a
""")
        tags = TagValueCollection([TagValue("A")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.visit(program)
        self.assertEqual(0, len(analyzer.items))

    def test_tag_name_undefined(self):
        program = build_program("""
Watch: A > 2
    Mark: a
""")
        tags = TagValueCollection([])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.visit(program)
        self.assertEqual(1, len(analyzer.items))
        item = analyzer.items[0]
        self.assertEqual("UndefinedTag", item.id)
        # this requires some extra data collected during program build
        # self.assertEqual(2, item.range_start.line)
        # self.assertEqual(7, item.range_start.character)
        # self.assertEqual(2, item.range_end.line)
        # self.assertEqual(8, item.range_end.character)

    def test_tag_unit_valid(self):
        program = build_program("""
Watch: A > 2
    Mark: a
""")
        tags = TagValueCollection([TagValue("A")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.visit(program)
        self.assertEqual(0, len(analyzer.items))

    def test_tag_unit_unexpected(self):
        program = build_program("""
Watch: A > 2 mL
    Mark: a
""")
        tags = TagValueCollection([TagValue("A")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.visit(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("UnexpectedUnit", analyzer.items[0].id)

    def test_tag_unit_missing(self):
        program = build_program("""
Watch: A > 2
    Mark: a
""")
        tags = TagValueCollection([TagValue("A", unit="mL")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.visit(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("MissingUnit", analyzer.items[0].id)

    def test_tag_units_incompatible(self):
        program = build_program("""
Watch: A > 2 mL
    Mark: a
""")
        tags = TagValueCollection([TagValue("A", unit="s")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.visit(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("IncompatibleUnits", analyzer.items[0].id)

    def test_tag_units_equal(self):
        program = build_program("""
Watch: A > 2 L
    Mark: a
""")
        tags = TagValueCollection([TagValue("A", unit="L")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.visit(program)
        self.assertEqual(0, len(analyzer.items))

    def test_tag_units_compatible(self):
        program = build_program("""
Watch: A > 2 mL
    Mark: a
""")
        tags = TagValueCollection([TagValue("A", unit="L")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.visit(program)
        self.assertEqual(0, len(analyzer.items))

    def test_tag_unit_CV(self):
        # need to test CV comparison, CV being a custom unit unknown by pint
        program = build_program("""
Watch: A > 2 CV
    Mark: a
""")
        tags = TagValueCollection([TagValue("A", unit="CV")])
        analyzer = ConditionCheckAnalyzer(tags)
        analyzer.visit(program)
        self.assertEqual(0, len(analyzer.items))


    @unittest.skip("TODO")
    def test_tag_categorized_valid(self):
        pass

    @unittest.skip("TODO")
    def test_tag_categorized_invalid(self):
        pass


class UnreachableCodeCheckAnalyzerTest(unittest.TestCase):
    def test_UnreachableCodeVisitor(self):
        program = build_program("""
Block: A
    Mark: a
    End block
    Mark: b
Mark: c
""")
        analyzer = UnreachableCodeCheckAnalyzer()
        analyzer.visit(program)
        self.assertEqual(1, len(analyzer.items))


class InfiniteBlockCheckAnalyzerTest(unittest.TestCase):
    def test_missing_global_end(self):
        program = build_program("""
Block: A
    Mark: a
Mark: c
""")
        sa = InfiniteBlockCheckAnalyzer()
        sa.visit(program)
        self.assertEqual(1, len(sa.items))

    def test_has_global_end(self):
        program = build_program("""
Watch: Run counter > 0
    End block

Block: A
    Mark: a
Mark: c
""")
        sa = InfiniteBlockCheckAnalyzer()
        sa.visit(program)
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
        sa.visit(program)
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
        sa.visit(program)
        self.assertEqual(1, len(sa.items))


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

class MacroCheckAnalyzerTest(unittest.TestCase):
    def test_valid_macro(self):
        program = build_program("""
Macro: A
    Mark: a
""")
        analyzer = MacroCheckAnalyzer()
        analyzer.visit(program)
        self.assertEqual(0, len(analyzer.items))

    @unittest.skip("Fix in #662")
    def test_invalid_macro(self):
        program = build_program("""
Macro:
    Mark: a
""")
        analyzer = MacroCheckAnalyzer()
        analyzer.visit(program)
        self.assertEqual(1, len(analyzer.items))

    def test_valid_macro_w_call(self):
        program = build_program("""
Macro: A
    Mark: a
Call macro: A
""")
        analyzer = MacroCheckAnalyzer()
        analyzer.visit(program)
        self.assertEqual(0, len(analyzer.items))

    def test_invalid_call_macro_to_undefined_macro(self):
        program = build_program("""
Call macro: A
""")
        analyzer = MacroCheckAnalyzer()
        analyzer.visit(program)
        self.assertEqual(1, len(analyzer.items))

    # Add checks for valid and invalid recursive Macro definitions/calls
