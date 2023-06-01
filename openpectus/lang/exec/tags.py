from __future__ import annotations
from enum import StrEnum, auto
from typing import Dict, Iterable, List, Set

import pint
from pint import UnitRegistry, Quantity

ureg = UnitRegistry()
Q_ = Quantity

# Represents tag API towards interpreter

DEFAULT_TAG_BASE = "BASE"
DEFAULT_TAG_RUN_COUNTER = "RUN COUNTER"
DEFAULT_TAG_BLOCK_TIME = "BLOCK TIME"
DEFAULT_TAG_RUN_TIME = "RUN TIME"
DEFAULT_TAG_CLOCK = "CLOCK"


class ChangeListener():
    def __init__(self) -> None:
        self._changes: Set[str] = set()

    def notify_change(self, elm: str):
        self._changes.add(elm)

    def clear_changes(self):
        self._changes.clear()

    @property
    def changes(self) -> List[str]:
        return list(self._changes)


class ChangeSubject():
    def __init__(self) -> None:
        super().__init__()

        self._listeners: List[ChangeListener] = []

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
    INPUT = auto(),
    """ Tag is read from hardware, e.g. a sensor """
    OUTPUT = auto(),
    """ Tag is written to hardware, e.g. an actuator """
    NA = auto()
    """ Tag is calculated/derived and neither read from or written to hw. """
    UNSPECIFIED = auto()


# TODO add support for 'safe' values, ie. to allow specifying a value that is automatically
# written when run state is one or more of stopped/paused/on hold

class Tag(ChangeSubject):
    def __init__(
            self,
            name: str,
            value=None,
            unit: str | None = None) -> None:

        super().__init__()

        if unit is not None and not isinstance(unit, str):
            raise ValueError("unit must be None or a string")

        self.name: str = name
        self.value = value  # Do we need default also? sometimes it is used as safe but are the other uses?
        self.unit = unit
        self.choices: List[str] | None = None
        self.direction: TagDirection = TagDirection.UNSPECIFIED
        self.safe_value = None

    def set_value(self, val) -> None:
        if val != self.value:
            self.value = val
            self.notify_listeners(self.name)

    def get_value(self):
        return self.value

    def get_pint_unit(self):
        if self.unit is None:
            return None
        return pint.Unit(self.unit)

    def as_quantity(self) -> pint.Quantity:
        return pint.Quantity(self.value, self.unit)

    def as_number(self) -> int | float:
        if not isinstance(self.value, (int, float)):
            raise ValueError(f"Value is not numerical: '{self.value}'")
        return self.value

    def set_quantity(self, q: pint.Quantity):
        self.unit = None if q.dimensionless else q.units
        self.set_value(q.magnitude)

    def clone(self) -> Tag:
        return Tag(self.name, self.value, self.unit)


class Reading(Tag):
    def __init__(self, name: str, unit: str | None = None) -> None:
        super().__init__(name, value=0.0, unit=unit)
        self.direction = TagDirection.INPUT


class Select(Tag):
    def __init__(self, name: str, value, unit: str | None ,
                 choices: List[str], direction: TagDirection = TagDirection.NA) -> None:
        super().__init__(name, value, unit)
        if choices is None or len(choices) == 0:
            raise ValueError("choices must be non-empty")
        self.choices = choices
        self.direction = direction

# TODO consider builder pattern for Tag - may replace so many tags - or at least make ctor args managable

# class Select_old(Tag):
#     '''Implements a tag that can hold discrete values.'''
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.states = kwargs.pop('choices')
#         self.direction = kwargs.pop('direction', Direction.NA)
#         self.default = kwargs.pop('default', None)
#         if self.direction == Direction.OUTPUT:
#             self.state = None
#         else:
#             self.state = self.default
#         self.archive = self.read
#         self.hw_value = self.read
#     def read(self):
#         return self.state
#     def write(self, request):
#         if isinstance(request, int):
#             if request < len(self.states):
#                 request = self.states[request]
#         if request in self.states:
#             if self.state is not request:
#                 self.state = request
#                 self.notify()
#     def reset(self):
#         self.write(self.default)
#         self.notify()
#     def safe(self):
#         self.write(self.default)


class TagCollection(ChangeSubject, ChangeListener, Iterable[Tag]):
    """ Represents a case insensitive name/tag dictionary. """

    def __init__(self) -> None:
        super().__init__()
        self.tags: Dict[str, Tag] = {}

    # propagate tag changes to collection changes
    def notify_change(self, elm: str):
        self.notify_listeners(elm)

    @property
    def names(self) -> List[str]:
        """ Return the tag names in upper case. """
        return list(self.tags.keys())

    def __iter__(self):
        yield from self.tags.values()

    def __getitem__(self, tag_name: str):
        return self.tags[tag_name.upper()]

    def __len__(self) -> int:
        return len(self.tags)

    def get(self, tag_name: str) -> Tag:
        if tag_name is None or tag_name.strip() == '':
            raise ValueError("tag_name is None or empty")
        if not tag_name.upper() in self.tags.keys():
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

        self.tags[tag.name.upper()] = tag
        tag.add_listener(self)

    def with_tag(self, tag: Tag):
        self.add(tag)
        return self

    def has(self, tag_name: str) -> bool:
        if tag_name is None or tag_name.strip() == '':
            raise ValueError("tag_name is None or empty")
        return tag_name.upper() in self.tags.keys()

    def get_value_or_default(self, tag_name) -> str | None:
        if not self.has(tag_name):
            return None
        return self.tags[tag_name].get_value()

    def clone(self) -> TagCollection:
        """ Returns a deep clone of the collection. """
        tags = TagCollection()
        for tag in self.tags.values():
            tags.add(tag.clone())
        return tags

    def merge_with(self, other: TagCollection) -> TagCollection:
        """ Returns a new TagCollection with the combined tags of both collections.

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
        tags = TagCollection()
        defaults = [
            (DEFAULT_TAG_BASE, "min", None),  # TODO this should not be wrapped in pint quantity
            (DEFAULT_TAG_RUN_COUNTER, 0, None),
            (DEFAULT_TAG_BLOCK_TIME, 0.0, "s"),
            (DEFAULT_TAG_RUN_TIME, 0.0, "s"),
            (DEFAULT_TAG_CLOCK, 0.0, "s"),
        ]
        for name, value, unit in defaults:
            tags.add(Tag(name, value, unit))
        return tags
