import unittest

from openpectus.lang.grammar.pgrammar import PGrammar


def get_token_texts(code):
    p = PGrammar()
    p.parse(code)
    tokens = list(p.tokens)
    return list(t.text for t in tokens)


class LexerTest(unittest.TestCase):
    def assertPTokenCountGE(self, code: str, expected_min_count: int):

        def print(s):
            pass
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

    def test_condition_negative_value(self):
        code = "foo=-3"
        self.assertEqual(['foo', '=', '-', '3'], get_token_texts(code))

    def test_condition_unit(self):
        code = "foo > 3 ml"
        self.assertEqual(['foo', ' ', '>', ' ', '3', ' ', 'ml'], get_token_texts(code))

    def test_watch_condition(self):
        code = "watch:foo > 3 ml"
        self.assertEqual(['watch', ':', 'foo', ' ', '>', ' ', '3', ' ', 'ml'], get_token_texts(code))

    def test_pause(self):
        code = "Pause"
        self.assertEqual(['Pause'], get_token_texts(code))

    def test_pause_w_arg(self):
        code = "Pause: 2 s"
        self.assertEqual(['Pause', ':', ' ', '2', ' ', 's'], get_token_texts(code))

    def test_hold(self):
        code = "Hold"
        self.assertEqual(['Hold'], get_token_texts(code))

    def test_hold_w_arg(self):
        code = "Hold: 2 s"
        self.assertEqual(['Hold', ':', ' ', '2', ' ', 's'], get_token_texts(code))

    def test_hold_w_arg2(self):
        code = "Hold: 2.0 min"
        self.assertEqual(['Hold', ':', ' ', '2.0', ' ', 'min'], get_token_texts(code))

    def test_mark_name_percent(self):
        code = "Mark: 2%"
        self.assertEqual(['Mark', ':', ' ', '2', '%'], get_token_texts(code))

        code = "Mark: B %"
        self.assertEqual(['Mark', ':', ' ', 'B', ' ', '%'], get_token_texts(code))


if __name__ == "__main__":
    unittest.main()
