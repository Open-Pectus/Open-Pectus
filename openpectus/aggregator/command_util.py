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


def create_commands(tag: Mdl.TagValue, reading: Mdl.ReadingInfo) -> list[Dto.ProcessValueCommand]:
    commands: list[Dto.ProcessValueCommand] = []
    for cmd in reading.commands:
        if reading.discriminator == "reading_with_entry":
            is_string = is_int = is_float = False
            assert reading.entry_data_type is not None
            if reading.entry_data_type == "auto":
                is_string = isinstance(tag.value, str)
                is_int = isinstance(tag.value, int)
                is_float = isinstance(tag.value, float)
                if not (is_string | is_int | is_float):
                    raise ValueError(
                        f"Error in uod. Failed to build commands for ReadingWithEntry, tag: '{tag.name}'." +
                        "Entry_data_type=auto cannot be used because the tag's current value has en incorrect type.")
            elif reading.entry_data_type == "float":
                is_float = True
            elif reading.entry_data_type == "int":
                is_int = True
            elif reading.entry_data_type == "str":
                is_string = True

            cmd = reading.commands[0]
            command = Dto.ProcessValueCommand(
                command_id=cmd.command_id,
                name=cmd.name,
                command=cmd.command,
                disabled=None,
                value=None
            )

            if is_string:
                assert isinstance(tag.value, str)
                command.value = Dto.ProcessValueCommandFreeTextValue(
                    value=tag.value,
                    value_type=Dto.ProcessValueType.STRING
                )
            elif is_float:
                assert isinstance(tag.value, float)
                command.value = Dto.ProcessValueCommandNumberValue(
                    value=tag.value,
                    value_type=Dto.ProcessValueType.FLOAT,
                    value_unit=tag.value_unit,
                    valid_value_units=reading.valid_value_units
                )
            elif is_int:
                assert isinstance(tag.value, int)
                command.value = Dto.ProcessValueCommandNumberValue(
                    value=tag.value,
                    value_type=Dto.ProcessValueType.INT,
                    value_unit=tag.value_unit,
                    valid_value_units=reading.valid_value_units
                )
            else:
                raise ValueError("Internal error. Failed to determine entry_data_type")

        elif reading.discriminator == "reading_with_choice":
            current_value = str(tag.value)
            command = Dto.ProcessValueCommand(
                command_id=cmd.command_id,
                name=cmd.name,
                command=cmd.command,
                disabled=None,
                value=Dto.ProcessValueCommandChoiceValue(
                    value=current_value,
                    value_type=Dto.ProcessValueType.CHOICE,
                    options=[choice for choice in cmd.choice_names]
                )
            )

        else:
            raise NotImplementedError("Reading discriminator not implemented: " + reading.discriminator)

        commands.append(command)

    return commands
