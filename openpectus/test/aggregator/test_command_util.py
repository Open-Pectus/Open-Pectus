import unittest

import openpectus.aggregator.models as Mdl
import openpectus.aggregator.routers.dto as Dto
from openpectus.lang.exec.readings import Reading, ReadingWithEntry, ReadingWithChoice
import openpectus.protocol.aggregator_messages as AM

from openpectus.aggregator import command_util as cu


def create_ReadingInfo(reading: Reading) -> Mdl.ReadingInfo:
    reading.build_commands_list()
    return reading.as_reading_info()


class CommantUtilTest(unittest.TestCase):

    def test_unit_button_parse(self):

        def test(command, name, expectSuccess=True, expectedResultType: type | None = None):
            with self.subTest(command + "_" + name):
                cmd = Dto.ExecutableCommand(
                    command_id=None,
                    command=command,
                    source=Dto.CommandSource.UNIT_BUTTON,
                    name=name,
                    value=None)

                if expectSuccess:
                    msg = cu.parse_as_message(cmd, [])
                    if expectedResultType is not None:
                        self.assertIsInstance(msg, expectedResultType)
                else:
                    with self.assertRaises(ValueError, msg="Expected parse error"):
                        cu.parse_as_message(cmd, [])

        test("Start", "", True, AM.InvokeCommandMsg)
        test("Stop", "", True, AM.InvokeCommandMsg)

        test("", "", False)
        test("stop", "", False)
        test("Stop\nStart", "", False)


    def test_cmd_without_value_parse_as_injected_with_command_as_pcode(self):
        cmd = Dto.ExecutableCommand(
            command_id=None,
            command="foo",
            source=Dto.CommandSource.PROCESS_VALUE,
            name=None,
            value=None)

        msg = cu.parse_as_message(cmd, [])
        assert isinstance(msg, AM.InjectCodeMsg)
        self.assertEqual("foo", msg.pcode)


    def test_cmd_with_value_Number_float_no_unit(self):
        reading = create_ReadingInfo(ReadingWithEntry(tag_name="foo", entry_data_type="float"))

        cmd = Dto.ExecutableCommand(
            command_id=reading.commands[0].command_id,
            command="foo",
            source=Dto.CommandSource.PROCESS_VALUE,
            name=None,
            value=Dto.ProcessValueCommandNumberValue(
                value=13.5,
                value_unit="",
                valid_value_units=[],
                value_type=Dto.ProcessValueType.FLOAT
            )
        )

        msg = cu.parse_as_message(cmd, [reading])

        assert isinstance(msg, AM.InjectCodeMsg)
        self.assertEqual("foo: 13.5", msg.pcode)

    def test_cmd_with_value_Number_int_unit(self):
        reading = create_ReadingInfo(ReadingWithEntry(tag_name="bar", entry_data_type="int"))

        cmd = Dto.ExecutableCommand(
            command_id=reading.commands[0].command_id,
            command="bar",
            source=Dto.CommandSource.PROCESS_VALUE,
            name=None,
            value=Dto.ProcessValueCommandNumberValue(
                value=87,
                value_unit="kg",
                valid_value_units=["g", "kg"],
                value_type=Dto.ProcessValueType.INT
            )
        )

        msg = cu.parse_as_message(cmd, [reading])

        assert isinstance(msg, AM.InjectCodeMsg)
        self.assertEqual("bar: 87 kg", msg.pcode)

    def test_cmd_with_value_FreeText_(self):
        reading = create_ReadingInfo(ReadingWithEntry(tag_name="bar", entry_data_type="str"))

        cmd = Dto.ExecutableCommand(
            command_id=reading.commands[0].command_id,
            command="bar",
            source=Dto.CommandSource.PROCESS_VALUE,
            name=None,
            value=Dto.ProcessValueCommandFreeTextValue(
                value="freetext VaLuE",
                value_type=Dto.ProcessValueType.STRING
            )
        )

        msg = cu.parse_as_message(cmd, [reading])

        assert isinstance(msg, AM.InjectCodeMsg)
        self.assertEqual("bar: freetext VaLuE", msg.pcode)

    def test_cmd_with_value_Choice_(self):
        reading = create_ReadingInfo(ReadingWithChoice(tag_name="foo", command_options={'A': 'Foo: A', 'B': 'Foo: B'}))

        cmd = Dto.ExecutableCommand(
            command_id=reading.commands[0].command_id,
            command="foo",
            source=Dto.CommandSource.PROCESS_VALUE,
            name=None,
            value=Dto.ProcessValueCommandChoiceValue(
                value="B",  # <- name of selected choice is provided here
                value_type=Dto.ProcessValueType.CHOICE,
                options=['A', 'B']
            ))

        msg = cu.parse_as_message(cmd, [reading])

        assert isinstance(msg, AM.InjectCodeMsg)
        self.assertEqual("Foo: B", msg.pcode)
