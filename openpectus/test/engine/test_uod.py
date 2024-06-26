import re
import unittest

from openpectus.lang.exec.uod import RegexCategorical, RegexNamedArgumentParser, RegexNumberWithUnit, RegexText

class TestRegexs_(unittest.TestCase):

    def test_named_groups_RegexNumberWithUnit(self):
        parser = RegexNamedArgumentParser(RegexNumberWithUnit(units=None))
        self.assertEqual(['number'], parser.get_named_groups())

        #TODO test signature in validation...

        parser = RegexNamedArgumentParser(RegexNumberWithUnit(units=['kg']))
        self.assertEqual(['number', 'number_unit'], parser.get_named_groups())

    def test_named_groups_RegexText(self):
        parser = RegexNamedArgumentParser(RegexText())
        self.assertEqual(['text'], parser.get_named_groups())

    def test_named_groups_RegexCategorical(self):
        # exclusive
        regex = RegexCategorical(exclusive_options=["Open", "Closed"])
        parser = RegexNamedArgumentParser(regex)
        self.assertEqual(['option'], parser.get_named_groups())

        # exclusive + additive
        regex = RegexCategorical(exclusive_options=['Closed'], additive_options=['VA01', 'VA02', 'VA03'])
        parser = RegexNamedArgumentParser(regex)
        self.assertEqual(['option'], parser.get_named_groups())

class TestRegexs(unittest.TestCase):
    def test_regex_number_with_unit(self):
        regex = RegexNumberWithUnit(units=["mS/cm", "L/h", "bar"])

        self.assertEqual(
            re.search(regex, "12 L/h").groupdict(),  # type: ignore
            dict(number="12", number_unit="L/h"))

        self.assertEqual(
            re.search(regex, "12.1 L/h").groupdict(),  # type: ignore
            dict(number="12.1", number_unit="L/h"))

        self.assertEqual(
            re.search(regex, ".5 L/h").groupdict(),  # type: ignore
            dict(number=".5", number_unit="L/h"))

        self.assertEqual(
            re.search(regex, "0.921 bar").groupdict(),  # type: ignore
            dict(number="0.921", number_unit="bar"))

        self.assertEqual(
            re.search(regex, "-1 bar").groupdict(),  # type: ignore
            dict(number="-1", number_unit="bar"))

        self.assertEqual(
            re.search(regex, "-12.1 bar").groupdict(),  # type: ignore
            dict(number="-12.1", number_unit="bar"))

        self.assertEqual(
            re.search(regex, "-.1 bar").groupdict(),  # type: ignore
            dict(number="-.1", number_unit="bar"))

        self.assertEqual(
            re.search(regex, "0.14 foo"),
            None)

    def test_regex_number_ws(self):
        regex = RegexNumberWithUnit(units=["mS/cm", "L/h", "bar"])
        self.assertEqual(
            re.search(regex, " 12  L/h   ").groupdict(),  # type: ignore
            dict(number="12", number_unit="L/h"))

        regex = RegexNumberWithUnit(units=None)
        self.assertEqual(
            re.search(regex, " 12  ").groupdict(),  # type: ignore
            dict(number="12"))


    def test_regex_number_with_unit_non_negative(self):
        regex = RegexNumberWithUnit(units=['mS/cm', 'L/h', 'bar'], non_negative=True)

        self.assertEqual(
            re.search(regex, "12 L/h").groupdict(),  # type: ignore
            dict(number="12", number_unit="L/h"))

        self.assertEqual(
            re.search(regex, "12.1 L/h").groupdict(),  # type: ignore
            dict(number="12.1", number_unit="L/h"))

        self.assertEqual(
            re.search(regex, ".5 L/h").groupdict(),  # type: ignore
            dict(number=".5", number_unit="L/h"))

        self.assertEqual(
            re.search(regex, "0.921 bar").groupdict(),  # type: ignore
            dict(number="0.921", number_unit="bar"))

        self.assertEqual(
            re.search(regex, "-12 L/h"),
            None)

        self.assertEqual(
            re.search(regex, "0.14 foo"),
            None)

    def test_regex_number_without_unit(self):
        regex = RegexNumberWithUnit(units=None)

        self.assertEqual(
            re.search(regex, "12").groupdict(),  # type: ignore
            dict(number="12"))

        self.assertEqual(
            re.search(regex, "12.1").groupdict(),  # type: ignore
            dict(number="12.1"))

        self.assertEqual(
            re.search(regex, ".5").groupdict(),  # type: ignore
            dict(number=".5"))

        self.assertEqual(
            re.search(regex, "-1").groupdict(),  # type: ignore
            dict(number="-1"))

        self.assertEqual(
            re.search(regex, "-12.1").groupdict(),  # type: ignore
            dict(number="-12.1"))

        self.assertEqual(
            re.search(regex, "-.1").groupdict(),  # type: ignore
            dict(number="-.1"))

        self.assertEqual(
            re.search(regex, "0.14 foo"),
            None)


    def test_regex_categorical_exclusive(self):
        regex = RegexCategorical(exclusive_options=["Open", "Closed"])
        self.assertEqual(
            re.search(regex, "Closed").groupdict(),  # type: ignore
            dict(option="Closed"))

        self.assertEqual(
            re.search(regex, "VA01"),
            None)

        self.assertEqual(
            re.search(regex, "Open").groupdict(),  # type: ignore
            dict(option="Open"))

        self.assertEqual(
            re.search(regex, "Open+Closed"),
            None)


    def test_regex_categorical_exclusive_and_additive(self):
        regex = RegexCategorical(exclusive_options=['Closed'], additive_options=['VA01', 'VA02', 'VA03'])

        self.assertEqual(
            re.search(regex, "Closed").groupdict(),  # type: ignore
            dict(option="Closed"))

        self.assertEqual(
            re.search(regex, "Closed+VA01"),
            None)

        self.assertEqual(
            re.search(regex, "VA01").groupdict(),  # type: ignore
            dict(option="VA01"))

        self.assertEqual(
            re.search(regex, "VA01+VA02").groupdict(),  # type: ignore
            dict(option="VA01+VA02"))

        self.assertEqual(
            re.search(regex, "Open+Closed"),
            None)


    def test_regex_string(self):
        regex = RegexText()

        self.assertEqual(
            re.search(regex, "Test string").groupdict(),  # type: ignore
            dict(text="Test string"))

        self.assertEqual(
            re.search(regex, "Test").groupdict(),  # type: ignore
            dict(text="Test"))

        self.assertEqual(
            re.search(regex, ""),
            None)

    def test_regex_string_allowing_empty(self):
        regex = RegexText(allow_empty=True)

        self.assertEqual(
            re.search(regex, "Test string").groupdict(),  # type: ignore
            dict(text="Test string"))

        self.assertEqual(
            re.search(regex, "Test").groupdict(),  # type: ignore
            dict(text="Test"))

        self.assertEqual(
            re.search(regex, "").groupdict(),  # type: ignore
            dict(text=""))


if __name__ == "__main__":
    unittest.main()
