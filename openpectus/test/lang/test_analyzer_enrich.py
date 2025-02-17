import re
import unittest

from openpectus.lang.exec.analyzer import (
    ConditionEnrichAnalyzer,
    DurationEnrichAnalyzer,
)
from openpectus.lang.model.pprogram import PCommandWithDuration, PCondition, PDuration, PWatch
from openpectus.lang import float_re, unit_re, identifier_re
from openpectus.test.engine.utility_methods import build_program as _build_program

def build_program_wo_analyzers(code: str):
    return _build_program(code, skip_enrich_analyzers=True)


class ConditionEnrichAnalyzerTest(unittest.TestCase):
    def test_watch_tag(self):
        program = build_program_wo_analyzers("""
Watch: counter > 0 mL
    Mark: b
""")
        analyzer = ConditionEnrichAnalyzer()
        watch = program.get_instructions()[0]
        assert isinstance(watch, PWatch)
        assert isinstance(watch.condition, PCondition)

        self.assertEqual(watch.condition.lhs, "counter")
        self.assertEqual(watch.condition.op, ">")
        self.assertEqual(watch.condition.rhs, "0 mL")

        self.assertEqual(watch.condition.tag_name, None)
        self.assertEqual(watch.condition.tag_value, None)
        self.assertEqual(watch.condition.tag_unit, None)

        analyzer.visit(program)

        self.assertEqual(watch.condition.tag_name, "counter")


    def test_watch_value_unit(self):
        program = build_program_wo_analyzers("""
Watch: counter > 0 mL
    Mark: b
""")
        analyzer = ConditionEnrichAnalyzer()
        watch = program.get_instructions()[0]
        assert isinstance(watch, PWatch) and isinstance(watch.condition, PCondition)
        analyzer.visit(program)

        self.assertEqual(watch.condition.tag_name, "counter")
        self.assertEqual(watch.condition.tag_value, "0")
        self.assertEqual(watch.condition.tag_unit, "mL")

    def test_float_re(self):
        def test(s):
            with self.subTest(s):
                m = re.match(float_re, s)
                self.assertIsNotNone(m)
        test("0")
        test("1.0")
        test("-0")
        test("-1")
        test("0.0")
        test("87,21")

    def test_unit_re(self):
        def test(s, expect_valid=True):
            with self.subTest(s):
                m = re.match('^' + unit_re + '$', s)
                if expect_valid:
                    self.assertIsNotNone(m)
                else:
                    self.assertIsNone(m)

        test("L")
        test("s")
        test("min")
        test("foo")
        test("%")
        test("kg/s")

        test("", False)
        test(".", False)
        test("0", False)
        test("0k", False)

    def test_identifier_re(self):
        def test(s, expect_valid=True):
            with self.subTest(s):
                m = re.match('^' + identifier_re + '$', s)
                if expect_valid:
                    self.assertIsNotNone(m)
                else:
                    self.assertIsNone(m)
        test("L")
        test("L2")
        test("L2")
        test("foo bar")
        test("foo2bar")
        test("foo bar baz")
        test("b 2")

        test("2", False)
        test("2b", False)
        test("2 b", False)
        test("", False)


    def test_watch_combinations(self):
        def test(code, expected_tag, expected_value, expected_unit):
            with self.subTest(code):
                program = build_program_wo_analyzers(code)
                analyzer = ConditionEnrichAnalyzer()
                watch = program.get_instructions()[0]
                assert isinstance(watch, PWatch) and isinstance(watch.condition, PCondition)
                analyzer.visit(program)

                self.assertEqual(watch.condition.tag_name, expected_tag)
                self.assertEqual(watch.condition.tag_value, expected_value)
                self.assertEqual(watch.condition.tag_unit, expected_unit)

        test("Watch: a > 0 s", "a", "0", "s")
        test("Watch: a >0", "a", "0", None)
        test("Watch: a > 0 ", "a", "0", None)
        test("Watch: foo bar > 0 mL ", "foo bar", "0", "mL")
        test("Watch: foo bar > 0   ", "foo bar", "0", None)


class DurationEnrichAnalyzerTest(unittest.TestCase):
    def test_pause_w_unit(self):
        program = build_program_wo_analyzers("Pause: 5 s")
        analyzer = DurationEnrichAnalyzer()
        pause = program.get_instructions()[0]
        assert isinstance(pause, PCommandWithDuration)
        assert isinstance(pause.duration, PDuration)

        self.assertEqual(pause.duration.duration_str, "5 s")
        self.assertEqual(pause.duration.time, None)
        self.assertEqual(pause.duration.unit, None)
        self.assertEqual(pause.duration.error, True)

        analyzer.visit(program)

        self.assertEqual(pause.duration.time, 5.0)
        self.assertEqual(pause.duration.unit, "s")
        self.assertEqual(pause.duration.error, False)

    def test_pause_wo_unit(self):
        program = build_program_wo_analyzers("Pause: 3.14")
        analyzer = DurationEnrichAnalyzer()
        pause = program.get_instructions()[0]
        assert isinstance(pause, PCommandWithDuration)
        assert isinstance(pause.duration, PDuration)

        self.assertEqual(pause.duration.duration_str, "3.14")
        self.assertEqual(pause.duration.time, None)
        self.assertEqual(pause.duration.unit, None)
        self.assertEqual(pause.duration.error, True)

        analyzer.visit(program)

        # Note: Changed in #437. Cannot see how duration could ever be valid without a unit
        # self.assertEqual(pause.duration.time, 3.14)
        # self.assertEqual(pause.duration.unit, None)
        # self.assertEqual(pause.duration.error, False)
        self.assertEqual(pause.duration.duration_str, "3.14")
        self.assertEqual(pause.duration.time, None)
        self.assertEqual(pause.duration.unit, None)
        self.assertEqual(pause.duration.error, True)
