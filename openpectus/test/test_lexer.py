import unittest

from lang.grammar.pgrammar import PGrammar


class LexerTest(unittest.TestCase):
    def assertPTokenCountGE(self, code: str, expected_min_count: int):
        print(f"\nCode: '{code}'")
        print("Tokens:")
        p = PGrammar()
        p.parse(code)
        tokens = p.tokens
        for t in tokens:
            print(t)
        self.assertGreaterEqual(len(tokens), expected_min_count)

    def test_block(self):
        code = "block:foo"
        self.assertPTokenCountGE(code, 1)

        code = "block: foo "
        self.assertPTokenCountGE(code, 1)

        code = "\nblock:foo#cmt\n"
        self.assertPTokenCountGE(code, 1)

    def test_command(self):
        code = "foo #no comment"
        self.assertPTokenCountGE(code, 1)

    # def test_comment(self):
    # p = parse("foo #foo")
    # c = p.parser.comment()
    # self.assertGreaterEqual(len(p.tokens), 1)


if __name__ == "__main__":
    unittest.main()
