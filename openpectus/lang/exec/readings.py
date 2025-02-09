from typing import Iterable, Literal
import uuid
from inspect import cleandoc
from itertools import combinations

from openpectus.engine.models import EntryDataType
from openpectus.lang.exec.tags import Tag, TagCollection
from openpectus.lang.exec.units import get_compatible_unit_names
from openpectus.lang.exec.errors import UodValidationError
import openpectus.protocol.models as Mdl

class ReadingCommand:
    """ Defines commands that are available in the frontend for a given reading/process value. """
    def __init__(self, name: str, command: str) -> None:
        self.command_id: str = str(uuid.uuid4())
        self.name: str = name
        self.command: str = command
        self.choice_names: list[str] = []

    def __str__(self) -> str:
        if len(self.choice_names):
            return (f'{self.__class__.__name__}(command_id="{self.command_id}", name="{self.name}", ' +
                    f'command="{self.command}", choice_names={self.choice_names})')
        else:
            return (f'{self.__class__.__name__}(command_id="{self.command_id}", name="{self.name}", ' +
                    f'command="{self.command}")')


class Reading:
    """ Defines a reading that is displayed to the frontend user as a Process Value.

    It is typically defined by matching it with a tag to display that tag's value and with one or
    more commands to allow the user to invoke these commands. The cases where commands are added are
    handled by Reading subclasses.

    execute_command_name is the name of the command to execute when the command is posted from the
    frontend. It defaults to tag_name which is usually fine. It can be set to something else if so
    desired.
    """

    def __init__(self, tag_name: str) -> None:
        if tag_name is None or tag_name == "":
            raise ValueError("tag_name in Reading must not be empty")
        self.discriminator = "reading"
        self.tag_name = tag_name
        self.commands : list[ReadingCommand] = []
        self.tag: Tag | None = None
        self.valid_value_units: list[str] | None = None
        self.entry_data_type: EntryDataType | None = None
        self.command_options: dict[str, str] | None = None

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(tag_name={self.tag_name})'

    def match_with_tags(self, tags: TagCollection):
        """ Match the reading with the provided tags. Raises UodValidationError or error. """

        if not tags.has(self.tag_name):
            raise UodValidationError(f"Reading with tag name: {self.tag_name} has no matching tag defined")

        self.tag = tags[self.tag_name]
        self.valid_value_units = get_compatible_unit_names(self.tag.unit)

    def build_commands_list(self):
        """ Override to specify the commands available in the UI for this process value.

        Is invoked after validation and match_with_tags so `tag` and `valid_value_units` have been set.
        """
        pass

    def resolve_entry_type(self):
        """ If entry_data_type is 'auto', resolve its type using the tag's current value.

        If resolved, mutate reading to use the resolved type as entry_data_type.
        """
        if self.entry_data_type == "auto":  # try to resolve the "auto" entry type
            assert self.tag is not None
            value = self.tag.get_value()
            if value is None:
                # Cannot resolve auto type when the tag has no value.
                raise ValueError(f"Cannot resolve entry type 'auto' for tag '{self.tag_name}' because the tag " +
                                 "value is None. Avoid this by setting a tag default value.")
            elif isinstance(value, str):
                self.entry_data_type = "str"
            elif isinstance(value, float):
                self.entry_data_type = "float"
            elif isinstance(value, int):
                self.entry_data_type = "int"

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
                The tag to display
            entry_data_type: optional, default="auto"
                The data type to display in the UI. Default is auto which uses the type of the tag's value.
            execute_command_name: optional
                The command name. Defaults to the name of the tag.
        """
        super().__init__(tag_name)
        self.execute_command_name = execute_command_name or tag_name
        self.discriminator = "reading_with_entry"
        self.entry_data_type = entry_data_type

    def match_with_tags(self, tags: TagCollection):
        super().match_with_tags(tags)
        assert isinstance(self.tag, Tag)

        if self.entry_data_type == "int":
            if not isinstance(self.tag.value, int):
                raise UodValidationError(
                    f"The process value for tag '{self.tag_name}' specifies the entry_data_type: {self.entry_data_type}. " +
                    f"This conflicts with the tag's current value '{self.tag.value}' which is of type {type(self.tag.value)}"
                )
        elif self.entry_data_type == "float":
            if not isinstance(self.tag.value, float):
                raise UodValidationError(
                    f"The process value for tag '{self.tag_name}' specifies the entry_data_type: {self.entry_data_type}. " +
                    f"This conflicts with the tag's current value '{self.tag.value}' which is of type {type(self.tag.value)}"
                )

    def build_commands_list(self):
        self.commands.append(ReadingCommand(self.tag_name, self.execute_command_name))

class ReadingWithChoice(Reading):
    """ A reading that is displayed with a list of possible commands. """

    def __init__(self, tag_name: str, command_options: dict[str, str] | None = None) -> None:
        """ Create a reading with command choices.

        Parameters:
            tag_name: str
                The tag to display. The tag's choices are used as commands, unless
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
        self._readings: list[Reading] = []

    def add(self, reading: Reading):
        self._readings.append(reading)

    def __iter__(self):
        yield from self._readings

    def __len__(self) -> int:
        return len(self._readings)


class UodCommandDescription:
    """ Describes a command and its usage. """
    def __init__(self, name: str) -> None:
        self.name: str = name
        """ Name of the command as used in pcode. """
        self.docstring: str = ""
        """ Description of the command's purpose, provided by uod author as docstring
        on the exec function. """
        self.argument_type: Literal["float", "unknown", "none"] = "unknown"
        """ the type of the argument in case the commands takes a single argument """
        self.argument_valid_units: list[str] = []
        """ Valid argument units if applicable. """
        self.argument_exclusive_options: list[str] = []
        """ Exclusive options if applicable. """
        self.argument_additive_options: list[str] = []
        """ Additive options if applicable. """

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(name="{self.name}")'

    def as_command_info(self) -> Mdl.CommandInfo:
        return Mdl.CommandInfo(
            name=self.name,
            docstring=self.docstring,
        )

    def set_docstring(self, docstring: str | None):
        self.docstring = cleandoc(docstring) if docstring is not None else ""

    def get_docstring_pcode(self) -> str:
        return self.docstring

    def generate_pcode_examples(self) -> list[str]:
        """ For commands with regex arg parser, generate pcode examples to test the command
        using combinations of argument values and units.
        """
        examples: list[str] = []
        if self.argument_type == "float":
            args = [0.5, 10, 32.6]
            if len(self.argument_valid_units) == 0:
                for arg in args:
                    examples.append(f"{self.name}: {arg}")
            else:
                for unit in self.argument_valid_units:
                    examples.append(f"{self.name}: {args[0]} {unit}")
        else:
            # Create examples for all exclusive options
            # If there are no exclusive options then the list is ['']
            # which we do not want to test.
            for arg in self.argument_exclusive_options:
                if arg:
                    examples.append(f"{self.name}: {arg}")
            # Create examples of all combinations of all possible lengths of additive options
            # If there are no additive options then the list is ['']
            # which we do not want to test.
            if len(self.argument_additive_options):
                for r in range(1, len(self.argument_additive_options)+1):
                    for args in combinations(self.argument_additive_options, r):
                        arg = "+".join(args)
                        if arg:
                            examples.append(f"{self.name}: {arg}")
        return examples
