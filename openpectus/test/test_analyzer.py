
import unittest
from lang.exec.analyzer import (
    SemanticAnalyzer,
    UnreachableCodeVisitor,
    InfiniteBlockVisitor
)

from .test_interpreter import build_program


class UnreachableCodeVisitorTest(unittest.TestCase):
    def test_UnreachableCodeVisitor(self):
        program = build_program("""
Block: A
    mark: a
    End block
    mark: b
mark: c
""")
        sa = UnreachableCodeVisitor()
        sa.visit(program)
        self.assertEqual(1, len(sa.items))


class InfiniteBlockVisitorTest(unittest.TestCase):
    def test_missing_global_end(self):
        program = build_program("""
Block: A
    mark: a
mark: c
""")
        sa = InfiniteBlockVisitor()
        sa.visit(program)
        self.assertEqual(1, len(sa.items))

    def test_has_global_end(self):
        program = build_program("""
Watch: Run counter > 0
    End block

Block: A
    mark: a
mark: c
""")
        sa = InfiniteBlockVisitor()
        sa.visit(program)
        self.assertEqual(0, len(sa.items))

    def test_has_local_end(self):
        program = build_program("""
Block: A
    mark: a
    Watch: Run counter > 0
        End block
mark: c
""")
        sa = InfiniteBlockVisitor()
        sa.visit(program)
        self.assertEqual(0, len(sa.items))

    def test_has_no_local_end(self):
        program = build_program("""
Block: A
    mark: a
    Watch: Run counter > 0
        End block
mark: c
Block: B
    mark: b
""")
        sa = InfiniteBlockVisitor()
        sa.visit(program)
        self.assertEqual(1, len(sa.items))


class SemanticAnalyzerTest(unittest.TestCase):
    def test_basic(self):
        program = build_program("""
mark: a
mark: b
mark: c
""")
        sa = SemanticAnalyzer()
        sa.visit_PProgram(program)
        self.assertEqual(0, len(sa.errors))

    def test_warning_UnreachableCode(self):
        program = build_program("""
Block: A
    mark: a
    End block
    mark: b
mark: c
""")
        sa = UnreachableCodeVisitor()
        sa.visit_PProgram(program)
        xs = [e for e in sa.items if e.id == 'UnreachableCode']
        self.assertEqual(1, len(xs))

    @unittest.skip("TODO")
    def test_condition_incompatible_units_warning(self):
        program = build_program("""
Watch: Block time > 3 L
    mark: a
""")

    @unittest.skip("TODO")
    def test_condition_undefined_tag_warning(self):
        program = build_program("""
Watch: Foo > 3
    mark: a
""")
        raise NotImplementedError
