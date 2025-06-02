import openpectus.aggregator.models as Mdl
import openpectus.aggregator.routers.dto as Dto
import openpectus.protocol.aggregator_messages as AM


def parse_as_message(cmd: Dto.ExecutableCommand, readings: list[Mdl.ReadingInfo]) -> AM.AggregatorMessage:
    if cmd.command is None or cmd.command.strip() == "":
        raise ValueError("Command is empty")

    lines = cmd.command.splitlines(keepends=False)
    line_count = len(lines)
    if line_count < 1:
        raise ValueError("Command is empty")

    if cmd.source == Dto.CommandSource.UNIT_BUTTON:
        if line_count > 1:
            raise ValueError("Unit Button command must be a single line command")
        code = lines[0]
        if not code.istitle():
            raise ValueError("Unit Button commands must be title cased")
        return AM.InvokeCommandMsg(name=code)

    return _parse_advanced_command(cmd, readings)


def _parse_advanced_command(cmd: Dto.ExecutableCommand, readings: list[Mdl.ReadingInfo]) -> AM.AggregatorMessage:
    if cmd.value is None:
        return AM.InjectCodeMsg(pcode=cmd.command)

    if isinstance(cmd.value, Dto.ProcessValueCommandNumberValue):
        unit_str = ""
        if cmd.value.value_unit is not None and cmd.value.value_unit.strip() != "":
            unit_str = " " + cmd.value.value_unit.strip()
        return AM.InjectCodeMsg(pcode=f"{cmd.command}: {cmd.value.value}{unit_str}")

    elif isinstance(cmd.value, Dto.ProcessValueCommandFreeTextValue):
        return AM.InjectCodeMsg(pcode=f"{cmd.command}: {cmd.value.value}")

    elif isinstance(cmd.value, Dto.ProcessValueCommandChoiceValue):
        if cmd.command_id is None or cmd.command_id.strip() == "":
            raise ValueError("Invalid command. command_id empty")
        cmd_reading = next((r for r in readings if r.has_command_id(cmd.command_id)), None)
        if cmd_reading is None:
            raise ValueError(f"Invalid command. command_id '{cmd.command_id}' does not match a reading command")

        if cmd_reading.command_options is None:
            raise ValueError("Invalid command. Matching reading has no command_options")
        command = cmd_reading.command_options.get(cmd.value.value)
        if command is None:
            raise ValueError(f"Invalid command. Matching reading has no command_option with name {cmd.value.value}")

        return AM.InjectCodeMsg(pcode=command)

    raise ValueError(f"Command not supported: '{cmd}'")


def create_reading_commands(tag: Mdl.TagValue, reading: Mdl.ReadingInfo) -> list[Dto.ProcessValueCommand]:
    commands: list[Dto.ProcessValueCommand] = []
    for reading_cmd in reading.commands:
        if reading.discriminator == "reading_with_entry":
            command = Dto.ProcessValueCommand(
                command_id=reading_cmd.command_id,
                name=reading_cmd.name,
                command=reading_cmd.command,
                disabled=None,
                value=None
            )
            if reading.entry_data_type is None or reading.entry_data_type == "auto":
                raise ValueError(
                    f"Error in uod. Failed to build commands for ReadingWithEntry, tag: '{reading.tag_name}'." +
                    f"entry_data_type is {reading.entry_data_type}. Expected str/int/float")
            elif reading.entry_data_type == "str":
                command.value = Dto.ProcessValueCommandFreeTextValue(
                    value="",
                    value_type=Dto.ProcessValueType.STRING
                )
            elif reading.entry_data_type == "float":
                command.value = Dto.ProcessValueCommandNumberValue(
                    value=tag.value if isinstance(tag.value, (float, int)) else 0,
                    value_type=Dto.ProcessValueType.FLOAT,
                    value_unit=tag.value_unit,
                    valid_value_units=reading.valid_value_units
                )
            elif reading.entry_data_type == "int":
                command.value = Dto.ProcessValueCommandNumberValue(
                    value=int(tag.value) if isinstance(tag.value, (float, int)) else 0,
                    value_type=Dto.ProcessValueType.INT,
                    value_unit=tag.value_unit,
                    valid_value_units=reading.valid_value_units
                )
            commands.append(command)

        elif reading.discriminator == "reading_with_choice":
            if reading_cmd.choice_names is None or len(reading_cmd.choice_names) == 0:
                raise ValueError(
                    f"Error in uod. Failed to build commands for ReadingWithChoice, tag: '{reading.tag_name}'. " +
                    "Reading choice_names is empty")
            current_value = str(tag.value)
            command = Dto.ProcessValueCommand(
                command_id=reading_cmd.command_id,
                name=reading_cmd.name,
                command=reading_cmd.command,
                disabled=None,
                value=Dto.ProcessValueCommandChoiceValue(
                    value=current_value,
                    value_type=Dto.ProcessValueType.CHOICE,
                    options=[choice for choice in reading_cmd.choice_names]
                )
            )
            commands.append(command)

        else:
            raise ValueError(
                f"Error in uod. Failed to build commands for reading, tag: '{reading.tag_name}'. " +
                f"Unknown discriminator: {reading.discriminator}")

    return commands


def create_command_examples(commands: list[Mdl.CommandInfo]) -> list[Dto.CommandExample]:
    # TODO We probably need a headline and spacer elements
    examples: list[Dto.CommandExample] = []
    for cmd in commands:
        example = "# No command information available"
        if cmd.docstring is not None and cmd.docstring != "":
            example = cmd.docstring
        examples.append(Dto.CommandExample(name=cmd.name, example=example))
    return examples
