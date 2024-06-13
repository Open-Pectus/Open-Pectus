from typing import Iterable
import uuid

from openpectus.engine.models import EntryDataType
from openpectus.lang.exec.tags import Tag, TagCollection
from openpectus.lang.exec.errors import UodValidationError
import openpectus.protocol.models as Mdl

class ReadingCommand():
    """ Defines commands that are available in the frontend for a given reading/process value. """
    def __init__(self, name: str, command: str) -> None:
        self.command_id: str = str(uuid.uuid4())
        self.name: str = name
        self.command: str = command
        self.choice_names: list[str] = []


class Reading():
    """ Defines a reading that is displayed to the frontend user as a Process Value.

    It is typically defined by matching it with a tag to display that tag's value and with one or
    more commands to allow the user to invoke these commands.

    execute_command_name is the name of the command to execute when the command is posted from the
    frontend. It defaults to tag_name which is usually fine. It can be set to something else if so
    desired.
    """

    def __init__(self, tag_name: str, execute_command_name: str | None = None) -> None:
        if tag_name is None or tag_name == "":
            raise ValueError("tag_name in Reading must not be empty")
        self.discriminator = "reading"
        self.tag_name = tag_name
        self.execute_command_name = execute_command_name or tag_name
        self.commands : list[ReadingCommand] = []
        self.tag: Tag | None = None
        self.valid_value_units: list[str] | None = None
        self.entry_data_type: EntryDataType | None = None
        self.command_options: dict[str, str] | None = None

    def match_with_tags(self, tags: TagCollection):
        """ Match the reading with the provided tags. Raises UodValidationError or error. """

        if not tags.has(self.tag_name):
            raise UodValidationError(f"Reading with tag name: {self.tag_name} has no matching tag defined")

        self.tag = tags[self.tag_name]
        self.valid_value_units = self.tag.get_compatible_units()

    def build_commands_list(self):
        """ Override to specify the commands available in the UI for this process value.

        Is invoked during validataion after match_with_tags so `tag` and `valid_value_units` have been set.
        """
        pass

    def as_reading_info(self) -> Mdl.ReadingInfo:
        return Mdl.ReadingInfo(
            discriminator=self.discriminator,
            tag_name=self.tag_name,
            valid_value_units=self.valid_value_units,
            entry_data_type=self.entry_data_type,
            command_options=self.command_options,
            commands=[Mdl.ReadingCommand(
                command_id=c.command_id,
                name=c.name,
                command=c.command,
                choice_names=c.choice_names,
            ) for c in self.commands]
        )

class ReadingWithEntry(Reading):
    def __init__(
            self,
            tag_name: str,
            entry_data_type: EntryDataType = "auto",
            execute_command_name: str | None = None) -> None:
        """ Create a reading with a command that takes an input value from the user.

        Parameters:

            tag_name:
                The tag to get the value from
            entry_data_type: optional, default="auto"
                The data type to display in the UI. Default is auto which uses the type of the tag's value.
            execute_command_name: optional
                The command name. Defaults to the name of the tag.
        """
        super().__init__(tag_name, execute_command_name)
        self.discriminator = "reading_with_entry"
        self.entry_data_type = entry_data_type

    def match_with_tags(self, tags: TagCollection):
        super().match_with_tags(tags)

    def build_commands_list(self):
        self.commands.append(ReadingCommand(self.tag_name, self.execute_command_name))

class ReadingWithChoice(Reading):
    """ A reading that is displayed with a list of possible commands. """

    def __init__(self, tag_name: str, command_options: dict[str, str] | None = None) -> None:
        """ Create a reading with command choices.

        Parameters:

            tag_name: str
                The tag to get value from. The tag's choices are also used as commands, unless
                command_options are specified.
            command_options: optional
                Dictionary that maps command names to their pcode implementation.
                If not specified, the tag's choices are used as both names and
                pcode implementation. If specified, the tag's choices are not used and the
                tag does not need to have choices defined.
        """
        super().__init__(tag_name)
        self.discriminator = "reading_with_choice"
        self.command_options = command_options

    def match_with_tags(self, tags: TagCollection):
        """ Internal, used in validation."""
        super().match_with_tags(tags)

        assert self.tag is not None
        if self.tag.choices is None or len(self.tag.choices) == 0:
            if self.command_options is None or len(self.command_options) == 0:
                raise UodValidationError(
                    "ReadingWithChoice requires either a tag with choices or non-empty command_options, " +
                    f"Reading Tag: {self.tag_name}")

        if self.command_options is None or len(self.command_options.keys()) == 0:
            self.command_options = {}
            assert self.tag.choices is not None
            for choice in self.tag.choices:
                self.command_options[choice] = choice

    def build_commands_list(self):
        """ Internal, used during validation. """
        assert self.command_options is not None
        choices = list(self.command_options.keys())
        command = ReadingCommand(self.tag_name, "(empty)")
        command.choice_names = choices
        self.commands.append(command)


class ReadingCollection(Iterable[Reading]):
    def __init__(self) -> None:
        super().__init__()
        self.readings: dict[str, Reading] = {}

    def add(self, reading: Reading):
        self.readings[reading.tag_name] = reading

    def __iter__(self):
        yield from self.readings.values()

    def __getitem__(self, tag_name: str) -> Reading:
        return self.readings[tag_name]

    def __len__(self) -> int:
        return len(self.readings)
