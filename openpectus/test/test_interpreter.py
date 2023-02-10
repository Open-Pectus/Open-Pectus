
import unittest

from lang.grammar.pprogramformatter import print_program
from lang.grammar.pgrammar import PGrammar
from lang.model.pprogram import (
    PProgram,
)

from lang.exec.pinterpreter import PInterpreter
from lang.exec.uod import UnitOperationDefinitionBase
from lang.exec.tags import Tag


def build_program(s) -> PProgram:
    p = PGrammar()
    p.parse(s)
    return p.build_model()


def print_log(i: PInterpreter):
    print('\n'.join(str(x['time']) + '\t' + str(x['unit_time']) + '\t' + x['message'] for x in i.logs))


class InterpreterTest(unittest.TestCase):

    def test_command_incr_counter(self):
        program = build_program("""
mark: a
incr counter
""")
        print()
        print("Initial program")
        print_program(program)

        uod = TestUod()
        i = PInterpreter(program, uod)
        i.validate_commands()

        print("Validated program")
        print_program(program, show_errors=True)

        self.assertEqual("0", uod.tags["counter"].get_value())

        i.start()

        self.assertEqual("1", uod.tags["counter"].get_value())
        self.assertEqual("a", i.get_marks()[0])

    def test_watch_can_evaluate_tag(self):
        program = build_program("""
mark: a
watch: counter > 0
    mark: b
mark: c
incr counter
watch: counter > 0
    mark: d
""")
        uod = TestUod()
        i = PInterpreter(program, uod)
        i.validate_commands()
        print_program(program, show_errors=True, show_line_numbers=True, show_blanks=True)
        i.start()
        self.assertEqual(["a", "c", "d"], i.get_marks())


if __name__ == "__main__":
    unittest.main()


class TestUod(UnitOperationDefinitionBase):
    def __init__(self) -> None:
        super().__init__()
        self.tags["counter"] = Tag("counter", "0")

        self.command_names.append("incr counter")

    # def add_tag(self, tag: Tag):

    def execute_command(self, command_name: str, command_args: str | None = None) -> None:
        cmd = command_name.replace(" ", "_")
        # if hasattr(self, cmd):
        #     method = getattr(self, cmd)
        #     method(command_args)  # type: ignore
        if cmd == "incr_counter":
            self.incr_counter()
        else:
            raise ValueError("Unknown command: " + cmd)

    def incr_counter(self):
        counter = self.tags["counter"]
        count = int(counter.get_value())
        count += 1
        counter.set_value(str(count))
