import unittest

from lang.grammar.pgrammar import PGrammar
from lang.model.pprogram import (
    PProgram,
    PWatch,
    PMark,
    PCommand,
    PBlank
)

from lang.grammar.pprogramformatter import print_program


def build_program(s) -> PProgram:
    p = PGrammar()
    p.parse(s)
    return p.build_model()


class ModelTest(unittest.TestCase):

    def test_navigation(self):
        program = build_program(
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

        print_program(program, show_blanks=True, show_errors=True, show_line_numbers=True)
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

        self.assertEqual(None, program.parent)
        self.assertEqual(blank_1, program.next_descendant())
        self.assertEqual(None, program.next_following())

        self.assertEqual(program, blank_1.parent)
        self.assertEqual(None, blank_1.next_descendant())
        self.assertEqual(mark_a, blank_1.next_following())

        self.assertEqual(program, mark_a.parent)
        self.assertEqual(None, mark_a.next_descendant())
        self.assertEqual(watch_1, mark_a.next_following())

        self.assertEqual(program, watch_1.parent)
        self.assertEqual(mark_b, watch_1.next_descendant())
        self.assertEqual(mark_c, watch_1.next_following())

        self.assertEqual(watch_1, mark_b.parent)
        self.assertEqual(None, mark_b.next_descendant())
        self.assertEqual(mark_c, mark_b.next_following())

        self.assertEqual(program, mark_c.parent)
        self.assertEqual(None, mark_c.next_descendant())
        self.assertEqual(incr, mark_c.next_following())

        self.assertEqual(program, incr.parent)
        self.assertEqual(None, incr.next_descendant())
        self.assertEqual(watch_2, incr.next_following())

        self.assertEqual(program, watch_2.parent)
        self.assertEqual(mark_d, watch_2.next_descendant())
        self.assertEqual(blank_2, watch_2.next_following())

        self.assertEqual(watch_2, mark_d.parent)
        self.assertEqual(None, mark_d.next_descendant())
        self.assertEqual(blank_2, mark_d.next_following())

        self.assertEqual(program, blank_2.parent)
        self.assertEqual(None, blank_2.next_descendant())
        self.assertEqual(blank_3, blank_2.next_following())

        self.assertEqual(program, blank_3.parent)
        self.assertEqual(None, blank_3.next_descendant())
        self.assertEqual(None, blank_3.next_following())


if __name__ == "__main__":
    unittest.main()
