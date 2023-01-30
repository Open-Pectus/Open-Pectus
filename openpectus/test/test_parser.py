import unittest

from lang.grammar.pgrammar import PGrammar
from lang.grammar.codegen.pcodeParser import ParserRuleContext, pcodeParser


def parse(s):
    p = PGrammar()
    p.parse(s)
    return p


class ParserTest(unittest.TestCase):
    def test_block(self):
        p = parse("block: foo")
        c = p.parser.block()  # type: ignore
        self.assertIsNotNone(c)
        p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.BlockContext)

        p = parse("block: foo")
        c = p.parser.program()  # type: ignore
        self.assertIsNotNone(c)
        self.assertIsInstance(c, pcodeParser.ProgramContext)

    def test_end_block(self):
        p = parse("end block")
        c = p.parser.end_block()  # type: ignore
        self.assertIsNotNone(c)
        p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.End_blockContext)

    def test_end_blocks(self):
        p = parse("end blocks")
        c = p.parser.end_blocks()  # type: ignore
        self.assertIsNotNone(c)
        p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.End_blocksContext)

    def test_watch(self):
        p = parse("watch")
        c = p.parser.watch()  # type: ignore
        self.assertIsNotNone(c)
        p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.WatchContext)

    def test_condition(self):
        p = parse("X > 10 ml")
        c = p.parser.condition()  # type: ignore
        self.assertIsNotNone(c)
        p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.ConditionContext)

    def assertIsWatchWithCondition(self, c: ParserRuleContext, condition: str):
        self.assertIsNotNone(c)
        self.assertIsInstance(c, pcodeParser.WatchContext)
        _args = None
        if c.children is not None:
            for x in c.children:
                if isinstance(x, pcodeParser.ConditionContext):
                    _args = x.getText()
        self.assertEqual(_args, condition)

    def test_watch_with_condition(self):
        p = parse("watch: X > 10 ml")
        c = p.parser.watch()  # type: ignore
        self.assertIsNotNone(c)
        p.printSyntaxTree(c)
        self.assertIsWatchWithCondition(c, "X > 10 ml")

    def assertIsAlarmWithCondition(self, c: ParserRuleContext, condition: str):
        self.assertIsNotNone(c)
        self.assertIsInstance(c, pcodeParser.AlarmContext)
        _args = None
        if c.children is not None:
            for x in c.children:
                if isinstance(x, pcodeParser.ConditionContext):
                    _args = x.getText()
        self.assertEqual(_args, condition)

    def test_alarm(self):
        p = parse("alarm")
        c = p.parser.alarm()  # type: ignore
        self.assertIsNotNone(c)
        p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.AlarmContext)

    def test_alarm_with_condition(self):
        p = parse("alarm: X > 10 ml")
        c = p.parser.alarm()  # type: ignore
        self.assertIsNotNone(c)
        p.printSyntaxTree(c)
        self.assertIsAlarmWithCondition(c, "X > 10 ml")

    def test_increment_rc(self):
        p = parse("Increment run counter")
        c = p.parser.increment_rc()  # type: ignore
        self.assertIsNotNone(c)
        p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.Increment_rcContext)

    def test_stop(self):
        p = parse("sTop")
        c = p.parser.stop()  # type: ignore
        self.assertIsNotNone(c)
        p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.StopContext)

    def test_pause(self):
        p = parse("PAuSe")
        c = p.parser.pause()  # type: ignore
        self.assertIsNotNone(c)
        p.printSyntaxTree(c)
        self.assertIsInstance(c, pcodeParser.PauseContext)

    def assertIsPCommandWithNameArgs(self, c: ParserRuleContext, name: str, args: str):
        self.assertIsNotNone(c)
        self.assertIsInstance(c, pcodeParser.CommandContext)

        _name = None
        _args = None

        if c.children is not None:
            for x in c.children:
                if isinstance(x, pcodeParser.Command_nameContext):
                    _name = x.getText()
                elif isinstance(x, pcodeParser.Command_argsContext):
                    _args = x.getText()

        self.assertEqual(_name, name)
        self.assertEqual(_args, args)

    def test_command_name(self):
        self.assertEqual(parse("foo").parser.command_name().getText(), "foo")  # type: ignore

    def test_command_args(self):
        def test(code, expected_args):
            with self.subTest(code):
                print(f"\nCode: '{code}'")
                p = parse(code)
                c = p.parser.command_args()  # type: ignore
                print("Tree:")
                p.printSyntaxTree(c)
                self.assertEqual(c.getText(), expected_args)

        test("bar", "bar")
        test("bar baz", "bar baz")
        test("bar=baz", "bar=baz")
        test("bar,baz", "bar,baz")
        # TODO test("bar,baz #comment", "bar,baz")

    def test_command(self):
        def test(code):
            with self.subTest(code):
                c = parse(code).parser.command()  # type: ignore
                self.assertIsNotNone(c)
                self.assertIsInstance(c, pcodeParser.CommandContext)

        test("foo")
        test(" foo")
        test("   foo")
        test("1 foo")
        test("1.1 foo")
        test("1.02 foo")
        test("  1.3 foo")
        test("   1.02 foo")

        test("foo:")
        test(" foo:a:3")
        test(" foo: a:3")
        test("   foo:a=3")
        test("1 foo:3,4 ")
        test("1.1 foo: 3=4,5:6")
        test("2.95 Zero UV")

    def test_command_name_args_simple(self):
        def test(code, expected_name, expected_args):
            with self.subTest(code):
                print(f"\nCode: '{code}'")
                p = parse(code)
                c = p.parser.command()  # type: ignore
                print("Tree:")
                p.printSyntaxTree(c)
                self.assertIsPCommandWithNameArgs(c, expected_name, expected_args)

        test("foo", "foo", None)
        test("foo: bar", "foo", "bar")
        test("1 foo: bar", "foo", "bar")
        test("7.89 foo: bar", "foo", "bar")
        test("7,89 foo: bar", "foo", "bar")
        test("2.95 Zero UV", "Zero UV", None)

    def test_command_name_args(self):
        def test(code, expected_name, expected_args):
            with self.subTest(code):
                print(f"\nCode: '{code}'")
                p = parse(code)
                c = p.parser.command()  # type: ignore
                print("Tree:")
                p.printSyntaxTree(c)
                self.assertIsPCommandWithNameArgs(c, expected_name, expected_args)

        test("1.23 foo bar", "foo bar", None)
        test("foo: bar,baz", "foo", "bar,baz")
        test("1.23 foo: bar baz", "foo", "bar baz")
        test("foo: 3,5", "foo", "3,5")
        test("foo: 3=5", "foo", "3=5")

        test("Inlet PU01: VA01", "Inlet PU01", "VA01")
        test("PU01: 77.64 %", "PU01", "77.64 %")


if __name__ == "__main__":
    unittest.main()
