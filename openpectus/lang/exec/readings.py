from typing import Dict, Iterable, List
from openpectus.lang.exec.tags import Tag, TagCollection
from openpectus.lang.exec.errors import UodValidationError


class ReadingCommand():
    def __init__(self, name: str, command: str) -> None:
        self.name: str = name
        self.command: str = command


class Reading():
    """ Defines a reading that is displayed to the frontend user as a Process Value.

    It is typically defined by matching it with a tag to display that tag's value and with one or
    more commands to allow the user to invoke these commands. """

    def __init__(self, tag_name: str, commands: List[ReadingCommand] = []) -> None:
        if tag_name == "":
            raise ValueError("tag_name in Reading must not be empty")
        self.tag_name = tag_name
        self.commands = commands  # might need both name and argument
        self.tag: Tag | None = None
        self.valid_value_units: List[str] | None = None

    def match_with_tags(self, tags: TagCollection):
        """ Match the reading with the provided tags. Raises UodValidationError or error. """

        if not tags.has(self.tag_name):
            raise UodValidationError(f"Reading with tag name: {self.tag_name} has no matching tag defined")

        self.tag = tags[self.tag_name]
        self.valid_value_units = self.tag.get_compatible_units()


class ReadingWithEntry(Reading):
    pass

    # TODO verify that tags have proper direction for write? Or is it just ok if there is a command?


class ReadingWithChoice(Reading):
    def match_with_tags(self, tags: TagCollection):
        super().match_with_tags(tags)

        assert self.tag is not None
        if self.tag.choices is None or len(self.tag.choices) == 0:
            raise UodValidationError(
                f"ReadingWithChoice can only be applied to tags with choices, Reading Tag: {self.tag_name}")


class ReadingCollection(Iterable[Reading]):
    def __init__(self) -> None:
        super().__init__()
        self.readings: Dict[str, Reading] = {}

    def add(self, reading: Reading):
        self.readings[reading.tag_name] = reading

    def __iter__(self):
        yield from self.readings.values()

    def __getitem__(self, tag_name: str) -> Reading:
        return self.readings[tag_name]

    def __len__(self) -> int:
        return len(self.readings)
