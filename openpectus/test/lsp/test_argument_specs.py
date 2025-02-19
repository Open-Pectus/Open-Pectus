
import re
import unittest

from openpectus.engine.engine import Engine
from openpectus.engine.internal_commands import InternalEngineCommand
from openpectus.lang.exec.uod import RegexNumber, RegexNumberOptional, UodBuilder
from openpectus.lang.exec.argument_specification import command_argument, ArgSpec


def create_minimal_builder() -> UodBuilder:
    builder = (
        UodBuilder()
        .with_instrument("TestUod")
        .with_author("Test Author", "test@openpectus.org")
        .with_filename(__file__)
        .with_hardware_none()
        .with_location("Test location")
    )
    return builder


class TestArgumentSpecification(unittest.TestCase):

    def test_can_annotate_with_NoArgs(self):

        @command_argument(validation_spec=ArgSpec.NoArgs())
        class TestCommand(InternalEngineCommand):
            ...

        self.assertEqual(ArgSpec.NoArgsInstance, TestCommand.argument_validation_spec)
        self.assertEqual(True, TestCommand.argument_validation_spec.validate(""))
        self.assertEqual(False, TestCommand.argument_validation_spec.validate(" "))
        self.assertEqual(False, TestCommand.argument_validation_spec.validate(" something "))

    def test_can_annotate_with_NoCheck(self):

        @command_argument(ArgSpec.NoCheck())
        class TestCommand(InternalEngineCommand):
            ...

        self.assertEqual(ArgSpec.NoCheckInstance, TestCommand.argument_validation_spec)
        self.assertEqual(True, TestCommand.argument_validation_spec.validate(" "))
        self.assertEqual(True, TestCommand.argument_validation_spec.validate(" something  "))


    def test_can_annotate_and_validate_with_empty_regex(self):

        test_regex = ""

        @command_argument(ArgSpec.Regex(regex=test_regex))
        class TestCommand(InternalEngineCommand):
            ...

        assert isinstance(TestCommand.argument_validation_spec, ArgSpec)
        self.assertEqual(test_regex, TestCommand.argument_validation_spec.regex)

        self.assertEqual(True, TestCommand.argument_validation_spec.validate(""))
        self.assertEqual(True, TestCommand.argument_validation_spec.validate("foo bar"))  # empty regex matches everything

    def test_can_annotate_with_and_validate_with_RegexNumber(self):

        test_regex = RegexNumber(units=None)

        @command_argument(ArgSpec.Regex(regex=test_regex))
        class TestCommand(InternalEngineCommand):
            ...

        assert isinstance(TestCommand.argument_validation_spec, ArgSpec)
        self.assertEqual(test_regex, TestCommand.argument_validation_spec.regex)

        self.assertEqual(True, TestCommand.argument_validation_spec.validate("56"))
        self.assertEqual(True, TestCommand.argument_validation_spec.validate("56.7"))
        self.assertEqual(False, TestCommand.argument_validation_spec.validate("foo"))
        self.assertEqual(False, TestCommand.argument_validation_spec.validate("56,7"))

    def test_can_get_command_args_specs(self):
        engine = Engine(create_minimal_builder().build())

        command_definitions = engine.get_command_definitions()
        self.assertIsNotNone(command_definitions)
        self.assertTrue("Wait" in [c.name for c in command_definitions])
        self.assertTrue("Start" in [c.name for c in command_definitions])
        self.assertTrue("Unhold" in [c.name for c in command_definitions])

        wait_cmd = next(c for c in command_definitions if c.name == "Wait")
        self.assertIsNotNone(wait_cmd.validator)

        engine.cleanup()

    def test_regex_no_args(self):
        regex = re.compile("^$")

        def assert_is_match(arg: str, match: bool = False):
            with self.subTest(arg + str(match)):
                if match:
                    self.assertIsNotNone(regex.match(arg))
                else:
                    self.assertIsNone(regex.match(arg))

        assert_is_match("", True)
        assert_is_match(" ")
        assert_is_match(" foo")
        assert_is_match("bar ")

    def test_regex_number_w_required_unit(self):
        regex = re.compile(RegexNumber(units=['s', 'min', 'h']))

        def assert_is_match(arg: str, match: bool = False):
            with self.subTest(arg + str(match)):
                if match:
                    self.assertIsNotNone(regex.match(arg))
                else:
                    self.assertIsNone(regex.match(arg))

        assert_is_match("5s", True)
        assert_is_match("5.89 s", True)
        assert_is_match("5")
        assert_is_match("5 f")

    def test_regex_optional_number_w_unit(self):
        regex = re.compile(RegexNumberOptional(units=['s', 'min', 'h']))

        def assert_is_match(arg: str, match: bool = False):
            with self.subTest(arg + " " + str(match)):
                if match:
                    self.assertIsNotNone(regex.match(arg))
                else:
                    self.assertIsNone(regex.match(arg))

        assert_is_match("", True)
        assert_is_match("5s", True)
        assert_is_match("5.89 s", True)
        assert_is_match("5")
        assert_is_match("5 f")
        assert_is_match("s")
