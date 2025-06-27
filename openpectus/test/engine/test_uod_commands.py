
import unittest

from openpectus.lang.exec.regex import RegexCategorical, RegexNumber
from openpectus.lang.exec.tags import Tag, create_system_tags
from openpectus.lang.exec.tags_impl import ReadingTag
from openpectus.lang.exec.uod import UodBuilder, UodCommand

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

        uod.system_tags = create_system_tags()
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

        uod.system_tags = create_system_tags()
        uod.validate_configuration()
        uod.build_commands()

        cmd = uod.command_descriptions["Area"]
        # Note removal of white space
        self.assertEqual(
            """# Runs the Area command\nArea: 5 cm2""",
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

        uod.system_tags = create_system_tags()
        uod.validate_configuration()
        uod.build_commands()

        cmd = uod.command_descriptions["Area"]
        pcode = cmd.get_docstring_pcode()
        self.assertEqual("# Runs the Area command\nArea: 5 cm2", pcode)

    def test_generate_example_pcode_number_with_unit(self):
        def exec_Area(cmd: UodCommand, number, number_unit):
            pass

        uod = (create_minimal_builder()
               .with_tag(ReadingTag("Area", unit="cm2"))
               .with_command_regex_arguments("Area", RegexNumber(units=["cm2", "dm2"]), exec_Area)
               ).build()

        uod.system_tags = create_system_tags()
        uod.validate_configuration()
        uod.build_commands()

        cmd = uod.command_descriptions["Area"]
        # remove comments
        pcode_examples = cmd.generate_pcode_examples()
        self.assertEqual(2, len(pcode_examples))
        self.assertEqual("Area: 0.5 cm2", pcode_examples[0])
        self.assertEqual("Area: 0.5 dm2", pcode_examples[1])

    def test_generate_example_pcode_w_unit(self):
        def exec_Vel(cmd: UodCommand, number, number_unit):
            pass

        uod = (create_minimal_builder()
               .with_tag(ReadingTag("Flow", unit="L/min"))
               .with_command_regex_arguments("Flow", RegexNumber(units=["L/h", "L/min"]), exec_Vel)
               ).build()

        uod.system_tags = create_system_tags()
        uod.validate_configuration()
        uod.build_commands()

        cmd = uod.command_descriptions["Flow"]
        pcode_examples = cmd.generate_pcode_examples()
        self.assertEqual(2, len(pcode_examples))
        self.assertEqual("Flow: 0.5 L/h", pcode_examples[0])
        self.assertEqual("Flow: 0.5 L/min", pcode_examples[1])

    def test_options_filtered_by_regex(self):

        def exec_Categorical(cmd: UodCommand, option: str):
            pass

        uod = (create_minimal_builder()
               .with_tag(Tag("Category", value=""))
               .with_command_regex_arguments("Categorical",
                                             RegexCategorical(exclusive_options=["A", "B"],
                                                              additive_options=["1", "2", "3"]),
                                             exec_Categorical)
               ).build()

        uod.system_tags = create_system_tags()
        uod.validate_configuration()
        uod.build_commands()

        cmd = uod.command_descriptions["Categorical"]
        self.assertEqual(["A", "B"], cmd.argument_exclusive_options)
        self.assertEqual(["1", "2", "3"], cmd.argument_additive_options)

    def test_generate_example_pcode_categorical(self):

        def exec_Categorical(cmd: UodCommand, option: str):
            pass

        uod = (create_minimal_builder()
               .with_tag(Tag("Category", value=""))
               .with_command_regex_arguments("Categorical",
                                             RegexCategorical(exclusive_options=["A", "B"],
                                                              additive_options=["1", "2", "3"]),
                                             exec_Categorical)
               ).build()

        uod.system_tags = create_system_tags()
        uod.validate_configuration()
        uod.build_commands()

        cmd = uod.command_descriptions["Categorical"]
        pcode_examples = cmd.generate_pcode_examples()
        self.assertEqual(9, len(pcode_examples))
        self.assertEqual("Categorical: A", pcode_examples[0])
        self.assertEqual("Categorical: B", pcode_examples[1])
        self.assertEqual("Categorical: 1", pcode_examples[2])
        self.assertEqual("Categorical: 2", pcode_examples[3])
        self.assertEqual("Categorical: 3", pcode_examples[4])
        self.assertEqual("Categorical: 1+2", pcode_examples[5])
        self.assertEqual("Categorical: 1+3", pcode_examples[6])
        self.assertEqual("Categorical: 2+3", pcode_examples[7])
        self.assertEqual("Categorical: 1+2+3", pcode_examples[8])

    def test_create_lsp_definition_w_regex_command(self):
        def exec_Vel(cmd: UodCommand, number, number_unit):
            pass

        uod = (create_minimal_builder()
               .with_tag(ReadingTag("Flow", unit="L/min"))
               .with_command_regex_arguments("Flow", RegexNumber(units=["L/h", "L/min"]), exec_Vel)
               ).build()

        uod.system_tags = create_system_tags()
        uod.validate_configuration()
        uod.build_commands()

        lsp_def = uod.create_lsp_definition()
        cmd_def = next((c for c in lsp_def.commands), None)
        assert cmd_def is not None
        self.assertEqual("Flow", cmd_def.name)
