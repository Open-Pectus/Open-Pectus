from __future__ import annotations

from enum import StrEnum, auto
import time
from typing import Any, Callable, Iterable, Set

from openpectus.lang.exec.tag_lifetime import TagLifetime
from openpectus.lang.exec.units import convert_value_to_unit, is_supported_unit


# Represents tag API towards interpreter

class SystemTagName(StrEnum):
    BASE = "Base"
    RUN_COUNTER = "Run Counter"
    BLOCK = "Block"
    BLOCK_TIME = "Block Time"
    PROCESS_TIME = "Process Time"
    RUN_TIME = "Run Time"
    CLOCK = "Clock"
    SYSTEM_STATE = "System State"
    METHOD_STATUS = "Method Status"
    CONNECTION_STATUS = "Connection Status"
    RUN_ID = "Run Id"

    # these tags are only present if defined in uod.
    BLOCK_VOLUME = "Block Volume"
    ACCUMULATED_VOLUME = "Accumulated Volume"
    BLOCK_CV = "Block CV"
    ACCUMULATED_CV = "Accumulated CV"


    @staticmethod
    def has_value(value: str):
        """ Determine if enum has this string value defined. Case sensitive. """
        return value in SystemTagName.__members__.values()


TagValueType = int | float | str | None
""" Represents the types of tag values """

TagFormatFunction = Callable[[Any], str]
""" Represents a function that is used to format tag values for display """


def format_time_as_clock(value: float) -> str:
    import datetime
    date = datetime.datetime.fromtimestamp(value, datetime.UTC)
    tm = date.time()
    return f"{tm.hour:02}:{tm.minute:02}:{tm.second:02}"


class ChangeListener():
    """ Collects named changes. Used by engine to track tag changes """

    def __init__(self) -> None:
        self._changes: Set[str] = set()

    def notify_change(self, elm: str):
        self._changes.add(elm)

    def clear_changes(self):
        self._changes.clear()

    @property
    def changes(self) -> list[str]:
        return list(self._changes)


class ChangeSubject():
    """ Inherit to support change notification. Used by engine to track tag changes """

    def __init__(self) -> None:
        super().__init__()

        self._listeners: list[ChangeListener] = []

    def add_listener(self, listener: ChangeListener):
        self._listeners.append(listener)

    def notify_listeners(self, elm: str):
        for listener in self._listeners:
            listener.notify_change(elm)

    def clear_listeners(self):
        # for listener in self._listeners:
        #     listener.clear_changes()
        self._listeners.clear()


# seems only relevant in hw interface
class TagDirection(StrEnum):
    """ Specifies whether a tag is read from or written to hardware and whether is can be changed in UI.

    Direction of the tag is in relation to the physical IO. Sensors are regarded as inputs and
    actuators as outputs. Derived values are regarded as NA.
    """
    Input = auto()
    """ Tag is read from hardware, e.g. a sensor """
    Output = auto()
    """ Tag is written to hardware, e.g. an actuator """
    NA = auto()
    """ Tag is calculated/derived and neither read from or written to hw. """
    Unspecified = auto()


class Unset():
    """ Used to specify that a value has not been set.

    Used for nullable values to distinguish between being set to None and not being set.
    """
    pass


class Tag(ChangeSubject, TagLifetime):
    """ Base class for tags. Most tags do not need their own class but can just use this class.

    Supports change tracking which is used by engine to detect changes between reads of hardware values.

    Supports lifetime notification events that are automatically invoked by the engine.
    """
    def __init__(
            self,
            name: str,
            tick_time: float | None = None,
            value: TagValueType = None,
            unit: str | None = None,
            direction: TagDirection = TagDirection.NA,
            safe_value: TagValueType | Unset = Unset(),
            format_fn: TagFormatFunction | None = None
            ) -> None:

        super().__init__()

        assert name is not None
        assert name != ""
        assert isinstance(name, str)  # this includes StrEnum which is useful

        if unit is not None:
            if not isinstance(unit, str):
                raise ValueError("unit must be None or a string")
            elif not is_supported_unit(unit):
                raise ValueError(f"Invalid unit '{unit}'")

        self.name: str = name
        self.tick_time = tick_time or time.time()
        self.value: TagValueType = value  # Do we need default also? sometimes it is used as safe but are the other uses?
        self.unit: str | None = unit
        self.choices: list[str] | None = None
        self.direction: TagDirection = direction
        self.safe_value: TagValueType | Unset = safe_value
        self.format_fn = format_fn

    def as_readonly(self) -> TagValue:
        """ Convert the value to a readonly and immutable TagValue instance """
        value_formatted = None if self.format_fn is None else self.format_fn(self.get_value())
        return TagValue(self.name, self.tick_time, self.value, value_formatted, self.unit, self.direction)

    def set_value(self, val: TagValueType, tick_time: float) -> None:
        if val != self.value:
            self.value = val
            self.tick_time = tick_time
            self.notify_listeners(self.name)

    def set_value_and_unit(self, val: TagValueType, unit: str, tick_time: float) -> None:
        """ Set a new value by converting the provided value and unit into the the unit of the tag. """
        if not isinstance(val, (int, float)):
            raise ValueError(f"Cannot set unit for a non-numeric value {val} of type {type(val).__name__}")
        if self.unit is None:
            raise ValueError("Cannot change unit on a tag with no unit")
        val = convert_value_to_unit(val, unit, self.unit)
        self.set_value(val, tick_time)

    def get_value(self):
        return self.value

    def as_number(self) -> int | float:
        if not isinstance(self.value, (int, float)):
            raise ValueError(
                f"Value is not numerical: '{self.value}' has type '{type(self. value).__name__}' tag: '{self.name}'")
        return self.value

    def as_float(self) -> float:
        if not isinstance(self.value, (float)):
            raise ValueError(
                f"Value is not a float: '{self.value}' has type '{type(self. value).__name__}' tag: '{self.name}'")
        return self.value

    def archive(self) -> str | None:
        """ The value to write to archive or None to skip that tag from archival """
        if self.value is None:
            return ""
        elif isinstance(self.value, float):
            return f"{self.as_float():0.5f}"
        else:
            return str(self.value)


class TagCollection(ChangeSubject, ChangeListener, Iterable[Tag]):
    """ Represents a  name/tag dictionary. """
    def __init__(self, tags: Iterable[Tag] | None = None) -> None:
        super().__init__()
        self.tags: dict[str, Tag] = {}
        if tags is not None:
            for tag in tags:
                self.add(tag, exist_ok=False)

    def as_readonly(self) -> TagValueCollection:
        return TagValueCollection([t.as_readonly() for t in self.tags.values()])

    # propagate tag changes to collection changes
    def notify_change(self, elm: str):
        self.notify_listeners(elm)

    @property
    def names(self) -> list[str]:
        """ Return the tag names """
        return list(self.tags.keys())

    def __iter__(self):
        yield from self.tags.values()

    def __getitem__(self, tag_name: str) -> Tag:
        return self.tags[tag_name]

    def __len__(self) -> int:
        return len(self.tags)

    def get(self, tag_name: str) -> Tag:
        if tag_name is None or tag_name.strip() == '':
            raise ValueError("tag_name is None or empty")
        if tag_name not in self.tags.keys():
            raise ValueError(f"Tag name {tag_name} not found")
        return self[tag_name]

    def add(self, tag: Tag, exist_ok: bool = True):
        """ Add tag to collection. If tag name already exists and exist_ok is False, a ValueError is raised. """
        if tag is None:
            raise ValueError("tag is None")
        if tag.name is None or tag.name.strip() == '':
            raise ValueError("tag name is None or empty")
        if tag.name in self.tags.keys() and not exist_ok:
            raise ValueError(f"A tag named {tag.name} already exists")

        self.tags[tag.name] = tag
        tag.add_listener(self)

    def with_tag(self, tag: Tag):
        self.add(tag)
        return self

    def has(self, tag_name: str) -> bool:
        if tag_name is None or tag_name.strip() == '':
            raise ValueError("tag_name is None or empty")
        return tag_name in self.tags.keys()

    def get_value_or_default(self, tag_name) -> TagValueType:
        if not self.has(tag_name):
            return None
        return self.tags[tag_name].get_value()

    def merge_with(self, other: TagCollection) -> TagCollection:
        """ Returns a new TagCollection with the combined tags of both collections.

        Tag instances are kept so tag values are shared between the three collections.

        In case of duplicate tag names, tags from other collection are used.
        """
        tags = TagCollection()
        for tag in self.tags.values():
            tags.add(tag)
        for tag in other.tags.values():
            tags.add(tag)
        return tags

    @staticmethod
    def create_system_tags() -> TagCollection:
        tags = TagCollection([
            Tag(SystemTagName.BASE, value="min"),  # note special value "min" and no unit
            Tag(SystemTagName.RUN_COUNTER, value=0),
            Tag(SystemTagName.BLOCK, value=None),
            Tag(SystemTagName.BLOCK_TIME, value=0.0, unit="s", format_fn=format_time_as_clock),
            Tag(SystemTagName.PROCESS_TIME, value=0.0, unit="s", format_fn=format_time_as_clock),
            Tag(SystemTagName.RUN_TIME, value=0.0, unit="s", format_fn=format_time_as_clock),
            Tag(SystemTagName.CLOCK, value=0.0, unit="s", format_fn=format_time_as_clock),
            Tag(SystemTagName.SYSTEM_STATE, value="Stopped"),
            Tag(SystemTagName.METHOD_STATUS, value="OK"),
            Tag(SystemTagName.CONNECTION_STATUS, value="Disconnected"),
            Tag(SystemTagName.RUN_ID, value=None),
        ])
        return tags


class TagValue():
    """ Read-only and immutable representation of a tag value. """
    def __init__(
            self,
            name: str,
            tick_time: float = 0.0,
            value: TagValueType = None,
            value_formatted: str | None = None,
            unit: str | None = None,
            direction: TagDirection = TagDirection.Unspecified,
    ):
        if name is None or name.strip() == '':
            raise ValueError("name is None or empty")

        self.name = name
        self.tick_time = tick_time
        self.value = value
        self.value_formatted = value_formatted
        self.unit = unit
        self.direction = direction


class TagValueCollection(Iterable[TagValue]):
    """ Represents a read-only and immutable dictionary of tag values. """

    def __init__(self, values: Iterable[TagValue]) -> None:
        super().__init__()
        self._tag_values: dict[str, TagValue] = {}
        for v in values:
            self._add(v)

    @staticmethod
    def empty() -> TagValueCollection:
        return TagValueCollection([])

    def get(self, tag_name: str) -> TagValue:
        if tag_name is None or tag_name.strip() == '':
            raise ValueError("tag_name is None or empty")
        if tag_name not in self._tag_values.keys():
            raise ValueError(f"Tag name {tag_name} not found")
        return self[tag_name]

    def has(self, tag_name: str) -> bool:
        if tag_name is None or tag_name.strip() == '':
            raise ValueError("tag_name is None or empty")
        return tag_name in self._tag_values.keys()

    def _add(self, tag_value: TagValue):
        self._tag_values[tag_value.name] = tag_value

    def __iter__(self):
        yield from self._tag_values.values()

    def __getitem__(self, tag_name: str) -> TagValue:
        return self._tag_values[tag_name]

    def __len__(self) -> int:
        return len(self._tag_values)

    def to_list(self) -> list[TagValue]:
        return [v for v in self._tag_values.values()]
