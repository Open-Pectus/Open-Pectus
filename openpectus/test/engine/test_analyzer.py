import unittest

from openpectus.lang.exec.analyzer import (
    SemanticAnalyzer,
    UnreachableCodeVisitor,
    InfiniteBlockVisitor,
    ConditionAnalyzerVisitor,
    CommandAnalyzerVisitor,
)
from openpectus.lang.exec.commands import CommandCollection, Command
from openpectus.lang.exec.tags import TagCollection, Tag
from test.engine.utility_methods import build_program


# TODO present PErrorInstructions as errors
# TODO present PErrors as errors

class CommandVisitorTest(unittest.TestCase):
    def test_command_defined(self):
        program = build_program("""
Foo
""")
        cmds = CommandCollection().with_cmd(Command("Foo"))
        analyzer = CommandAnalyzerVisitor(cmds)
        analyzer.visit(program)
        self.assertEqual(0, len(analyzer.items))

    def test_command_undefined(self):
        program = build_program("""
Foo
""")
        cmds = CommandCollection()
        analyzer = CommandAnalyzerVisitor(cmds)
        analyzer.visit(program)
        self.assertEqual(1, len(analyzer.items))

    def test_command_arg_valid(self):
        program = build_program("""
Foo: bar
""")
        cmds = CommandCollection().with_cmd(Command("Foo"))
        analyzer = CommandAnalyzerVisitor(cmds)
        analyzer.visit(program)
        self.assertEqual(0, len(analyzer.items))

    def test_command_arg_invalid(self):
        def is_valid_cmd(cmd_name):
            return cmd_name != 'bar'

        program = build_program("""
Foo: bar
""")
        cmds = CommandCollection().with_cmd(Command("Foo", is_valid_cmd))
        analyzer = CommandAnalyzerVisitor(cmds)
        analyzer.visit(program)
        self.assertEqual(1, len(analyzer.items))


class ConditionVisitorTest(unittest.TestCase):
    def test_tag_name_defined(self):
        program = build_program("""
Watch: A > 2
    Mark: a
""")
        tags = TagCollection().with_tag(Tag("A"))
        analyzer = ConditionAnalyzerVisitor(tags)
        analyzer.visit(program)
        self.assertEqual(0, len(analyzer.items))

    def test_tag_name_undefined(self):
        program = build_program("""
Watch: A > 2
    Mark: a
""")
        tags = TagCollection()
        analyzer = ConditionAnalyzerVisitor(tags)
        analyzer.visit(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("UndefinedTag", analyzer.items[0].id)

    def test_tag_unit_valid(self):
        program = build_program("""
Watch: A > 2
    Mark: a
""")
        tags = TagCollection().with_tag(Tag("A"))
        analyzer = ConditionAnalyzerVisitor(tags)
        analyzer.visit(program)
        self.assertEqual(0, len(analyzer.items))

    def test_tag_unit_unexpected(self):
        program = build_program("""
Watch: A > 2 mL
    Mark: a
""")
        tags = TagCollection().with_tag(Tag("A"))
        analyzer = ConditionAnalyzerVisitor(tags)
        analyzer.visit(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("UnexpectedUnit", analyzer.items[0].id)

    def test_tag_unit_missing(self):
        program = build_program("""
Watch: A > 2
    Mark: a
""")
        tags = TagCollection().with_tag(Tag("A", unit="ml"))
        analyzer = ConditionAnalyzerVisitor(tags)
        analyzer.visit(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("MissingUnit", analyzer.items[0].id)

    def test_tag_units_incompatible(self):
        program = build_program("""
Watch: A > 2 mL
    Mark: a
""")
        tags = TagCollection().with_tag(Tag("A", unit="sec"))
        analyzer = ConditionAnalyzerVisitor(tags)
        analyzer.visit(program)
        self.assertEqual(1, len(analyzer.items))
        self.assertEqual("IncompatibleUnits", analyzer.items[0].id)

    def test_tag_units_equal(self):
        program = build_program("""
Watch: A > 2 L
    Mark: a
""")
        tags = TagCollection().with_tag(Tag("A", unit="L"))
        analyzer = ConditionAnalyzerVisitor(tags)
        analyzer.visit(program)
        self.assertEqual(0, len(analyzer.items))

    def test_tag_units_compatible(self):
        program = build_program("""
Watch: A > 2 mL
    Mark: a
""")
        tags = TagCollection().with_tag(Tag("A", unit="L"))
        analyzer = ConditionAnalyzerVisitor(tags)
        analyzer.visit(program)
        self.assertEqual(0, len(analyzer.items))

    @unittest.skip("TODO")
    def test_tag_categorized_valid(self):
        pass

    @unittest.skip("TODO")
    def test_tag_categorized_invalid(self):
        pass


class UnreachableCodeVisitorTest(unittest.TestCase):
    def test_UnreachableCodeVisitor(self):
        program = build_program("""
Block: A
    Mark: a
    End block
    Mark: b
Mark: c
""")
        analyzer = UnreachableCodeVisitor()
        analyzer.visit(program)
        self.assertEqual(1, len(analyzer.items))


class InfiniteBlockVisitorTest(unittest.TestCase):
    def test_missing_global_end(self):
        program = build_program("""
Block: A
    Mark: a
Mark: c
""")
        sa = InfiniteBlockVisitor()
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
        sa = InfiniteBlockVisitor()
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
        sa = InfiniteBlockVisitor()
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
        sa = InfiniteBlockVisitor()
        sa.visit(program)
        self.assertEqual(1, len(sa.items))


class SemanticAnalyzerTest(unittest.TestCase):
    def test_basic(self):
        program = build_program("""
Mark: a
Mark: b
Mark: c
""")
        analyzer = SemanticAnalyzer(TagCollection(), CommandCollection())
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
        analyzer = SemanticAnalyzer(TagCollection(), CommandCollection())
        analyzer.analyze(program)
        xs = [e for e in analyzer.items if e.id == 'UnreachableCode']
        self.assertEqual(1, len(xs))
