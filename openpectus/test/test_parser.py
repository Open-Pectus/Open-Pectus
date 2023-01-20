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

        # We do not support comma in timeexp for now
        test("7,89 foo: bar", "foo", "bar")

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
