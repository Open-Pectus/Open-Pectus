
import unittest

from lang.grammar.pprogramformatter import print_program
from lang.grammar.pgrammar import PGrammar
from lang.model.pprogram import (
    PProgram,
)
from lang.exec.pinterpreter import (
    PInterpreter,
)
from lang.exec.uod import UnitOperationDefinitionBase
from lang.exec.tags import (
    Tag,
    DEFAULT_TAG_BASE
)


def build_program(s) -> PProgram:
    p = PGrammar()
    p.parse(s)
    return p.build_model()


def print_log(i: PInterpreter):
    print('\n'.join(str(x['time']) + '\t' + str(x['unit_time']) + '\t' + x['message'] for x in i.logs))


class InterpreterTest(unittest.TestCase):

    def test_sequential_marks(self):
        program = build_program("""
mark: a
mark: b
mark: c
""")
        uod = TestUod()
        i = PInterpreter(program, uod)

        i.run(10)
        # for _ in i.interpret():
        #     pass

        self.assertEqual(["a", "b", "c"], i.get_marks())
        print_log(i)

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

        self.assertEqual(0, uod.tags["counter"].as_number())

        i.run()

        self.assertEqual(1, uod.tags["counter"].as_number())
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
        i.run(15)

        print_log(i)
        self.assertEqual(["a", "c", "b", "d"], i.get_marks())
        # Note that first watch is also activated and its body executed 
        # even though it is not activated when first run. This represents the
        # interrupt nature of watches and alarms. So the behavior is not like this:
        # self.assertEqual(["a", "c", "d"], i.get_marks())

    def test_watch_nested(self):
        program = build_program("""
mark: a
watch: counter > 0
    mark: b
    watch: counter > 1
        mark: e
mark: c
incr counter
incr counter
watch: counter > 0
    mark: d
""")
        uod = TestUod()
        i = PInterpreter(program, uod)
        i.run(15)

        print_log(i)
        self.assertEqual(["a", "c", "b", "e", "d"], i.get_marks())

    def test_block(self):
        program = build_program("""
Block: A
    Mark: A1
    End block
    Mark: A2
Mark: A3
""")
        uod = TestUod()
        i = PInterpreter(program, uod)
        i.tags[DEFAULT_TAG_BASE].set_value("sec")

        i.run()

        print_log(i)

        self.assertEqual(["A1", "A3"], i.get_marks())

    def test_block_nested(self):
        program = build_program("""
Block: A
    Mark: A1
    Block: B
        Mark: B1
        End block
        Mark: B2
    End block
    Mark: A2
Mark: A3
""")
        uod = TestUod()
        i = PInterpreter(program, uod)

        i.run()

        self.assertEqual(["A1", "B1", "A3"], i.get_marks())

    def test_block_unterminated(self):
        program = build_program("""
Block: A
    Mark: A1
    Mark: A2
Mark: A3
""")
        uod = TestUod()
        i = PInterpreter(program, uod)

        i.run(max_ticks=5)

        self.assertEqual(["A1", "A2"], i.get_marks())

    def test_block_time_watch(self):
        program = build_program("""
Block: A
    Mark: A1
    Watch: Block time > 1 sec
        End block
    Mark: A2
Mark: A3
""")
        uod = TestUod()
        i = PInterpreter(program, uod)

        i.run(max_ticks=30)

        self.assertEqual(["A1", "A2", "A3"], i.get_marks())

    @unittest.skip("TODO")
    def test_(self):
        raise NotImplementedError()
        program = build_program("""
""")
        i = PInterpreter(program, TestUod())
        i.tags[DEFAULT_TAG_BASE].set_value("sec")
        i.validate_commands()
        print_program(program, show_errors=True, show_line_numbers=True, show_blanks=True)
        i.run()

    @unittest.skip("TODO")
    def test_command_long_running(self):
        raise NotImplementedError()
        program = build_program("""
""")
        i = PInterpreter(program, TestUod())
        i.tags[DEFAULT_TAG_BASE].set_value("sec")
        i.validate_commands()
        print_program(program, show_errors=True, show_line_numbers=True, show_blanks=True)
        i.run()

    @unittest.skip("TODO")
    def test_change_base_in_program(self):
        # base is also available in scope
        raise NotImplementedError()

    @unittest.skip("TODO")
    def test_change_base_in_scope(self):
        # base is global, a change should remain in place after scope completes
        raise NotImplementedError()


if __name__ == "__main__":
    unittest.main()


class TestUod(UnitOperationDefinitionBase):
    def __init__(self) -> None:
        super().__init__()
        self.tags.add(Tag("counter", 0))

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
        count = counter.as_number()
        count = count + 1  # type: ignore
        counter.set_value(count)
