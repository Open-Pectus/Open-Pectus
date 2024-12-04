
import unittest

from openpectus.lang.exec.tags import TagCollection
from openpectus.lang.exec.tags_impl import ReadingTag
from openpectus.lang.exec.uod import RegexNumber, UodBuilder, UodCommand


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


class TestCommandDescriptions(unittest.TestCase):
    def test_units_filtered_by_regex(self):

        def exec_Area(cmd: UodCommand, number, number_unit):
            pass

        uod = (create_minimal_builder()
               .with_tag(ReadingTag("Area", unit="cm2"))
               .with_command_regex_arguments("Area", RegexNumber(units=["cm2", "dm2"]), exec_Area)
               ).build()

        uod.system_tags = TagCollection.create_system_tags()
        uod.validate_configuration()
        uod.build_commands()

        cmd = uod.command_descriptions["Area"]
        self.assertEqual(['cm2', "dm2"], cmd.argument_valid_units)

    def test_exec_fn_docstring(self):

        def exec_Area(cmd: UodCommand, number, number_unit):
            """ # Runs the Area command
            Area: 5 cm2
            """
            pass

        uod = (create_minimal_builder()
               .with_tag(ReadingTag("Area", unit="cm2"))
               .with_command_regex_arguments("Area", RegexNumber(units=["cm2", "dm2"]), exec_Area)
               ).build()

        uod.system_tags = TagCollection.create_system_tags()
        uod.validate_configuration()
        uod.build_commands()

        cmd = uod.command_descriptions["Area"]
        # Note removal of white space
        self.assertEqual(
"""# Runs the Area command
Area: 5 cm2""",
            cmd.docstring
        )

    def test_get_docstring_pcode(self):
        def exec_Area(cmd: UodCommand, number, number_unit):
            """ # Runs the Area command
            Area: 5 cm2
            """
            pass

        uod = (create_minimal_builder()
               .with_tag(ReadingTag("Area", unit="cm2"))
               .with_command_regex_arguments("Area", RegexNumber(units=["cm2", "dm2"]), exec_Area)
               ).build()

        uod.system_tags = TagCollection.create_system_tags()
        uod.validate_configuration()
        uod.build_commands()

        cmd = uod.command_descriptions["Area"]
        pcode = cmd.get_docstring_pcode()
        self.assertEqual("# Runs the Area command\nArea: 5 cm2", pcode)

    def test_generate_example_pcode(self):
        def exec_Area(cmd: UodCommand, number, number_unit):
            pass

        uod = (create_minimal_builder()
               .with_tag(ReadingTag("Area", unit="cm2"))
               .with_command_regex_arguments("Area", RegexNumber(units=["cm2", "dm2"]), exec_Area)
               ).build()

        uod.system_tags = TagCollection.create_system_tags()
        uod.validate_configuration()
        uod.build_commands()

        cmd = uod.command_descriptions["Area"]
        # remove comments
        pcode_examples = cmd.generate_pcode_examples()
        self.assertEqual(2, len(pcode_examples))
        self.assertEqual("Area: 0.5 cm2", pcode_examples[0])
        self.assertEqual("Area: 0.5 dm2", pcode_examples[1])
