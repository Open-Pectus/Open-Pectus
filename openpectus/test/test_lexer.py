import unittest

from lang.grammar.pgrammar import PGrammar


def get_token_texts(code):
    p = PGrammar()
    p.parse(code)
    return list(t.text for t in p.tokens)


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

    def test_condition(self):
        code = "foo > 3"
        self.assertEqual(['foo', ' ', '>', ' ', '3'], get_token_texts(code))

    def test_condition_2(self):
        code = "foo=3"
        self.assertEqual(['foo', '=', '3'], get_token_texts(code))

    def test_condition_unit(self):
        code = "foo > 3 ml"
        self.assertEqual(['foo', ' ', '>', ' ', '3', ' ', 'ml'], get_token_texts(code))


if __name__ == "__main__":
    unittest.main()
