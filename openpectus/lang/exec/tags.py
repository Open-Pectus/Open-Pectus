from __future__ import annotations
from enum import StrEnum, auto
from typing import Any, Dict, Iterable, List, Set

import pint
from pint import UnitRegistry, Quantity
from pint.facets.plain import PlainQuantity

ureg = UnitRegistry(cache_folder="./pint-cache")
Q_ = Quantity

QuantityType = pint.Quantity | PlainQuantity[Any]

# Represents tag API towards interpreter

class SystemTagName(StrEnum):
    BASE = "Base"
    RUN_COUNTER = "Run Counter"
    BLOCK_TIME = "Block Time"
    PROCESS_TIME = "Process Time"
    RUN_TIME = "Run Time"
    CLOCK = "Clock"
    SYSTEM_STATE = "System State"
    METHOD_STATUS = "Method Status"


# Define the dimensions and units we want to use and the conversions we want to provide.
# Pint has way too many built in to be usable for this and it is simpler than customizing it
TAG_UNITS = {
    'length': ['m', 'cm'],
    'mass': ['kg', 'g'],
    '[time]': ['s', 'm', 'h', 'ms'],
    'flow': ['L/h', 'L/min', 'L/d'],  # Pint parses L/m as liter/meter
}

TAG_UNIT_DIMS = {
    'liter / hour': 'flow'
}


def _get_compatible_unit_names(tag: Tag):
    # TODO define the difference between None and [""]
    if tag.unit is None:
        return [""]

    pu = tag.get_pint_unit()
    if pu is None:
        return [""]
    elif pu.dimensionless:
        return [""]
    else:
        dims = pu.dimensionality
        if len(dims) == 1:
            unit_names = TAG_UNITS.get(str(dims))
            if unit_names is None:
                raise NotImplementedError(f"Unit {pu} with dimensionality {dims} has no defined compatible units")
            else:
                return unit_names
        else:
            dim_name = TAG_UNIT_DIMS.get(str(pu))
            if dim_name is None:
                raise NotImplementedError(f"Unit {pu} has no defined compatible units")
            unit_names = TAG_UNITS.get(dim_name)
            if unit_names is None:
                raise NotImplementedError(f"Unit {pu} has no defined compatible units for dimension {dim_name}")
            return unit_names


TagValueType = int | float | str | None


class ChangeListener():
    """ Collects named changes """
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
    """ Inherit to support change notification """
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


class Tag(ChangeSubject):
    def __init__(
            self,
            name: str,
            value: TagValueType = None,
            unit: str | None = None,
            direction: TagDirection = TagDirection.NA,
            safe_value: TagValueType = None) -> None:

        super().__init__()

        if unit is not None and not isinstance(unit, str):
            raise ValueError("unit must be None or a string")

        self.name: str = name
        self.value: TagValueType = value  # Do we need default also? sometimes it is used as safe but are the other uses?
        self.unit: str | None = unit
        self.choices: List[str] | None = None
        self.direction: TagDirection = direction
        self.safe_value: TagValueType = safe_value

    def as_readonly(self) -> TagValue:
        return TagValue(self.name, self.value, self.unit)

    def set_value(self, val: TagValueType) -> None:
        if val != self.value:
            self.value = val
            self.notify_listeners(self.name)

    def get_value(self):
        return self.value

    def get_pint_unit(self) -> pint.Unit | None:
        if self.unit is None:
            return None
        return pint.Unit(self.unit)

    def get_compatible_units(self):
        return _get_compatible_unit_names(self)

    def as_quantity(self) -> pint.Quantity:
        return pint.Quantity(self.value, self.unit)  # type: ignore

    def as_number(self) -> int | float:
        if not isinstance(self.value, (int, float)):
            raise ValueError(f"Value is not numerical: '{self.value}'")
        return self.value

    def set_quantity(self, q: QuantityType):
        self.unit = None if q.dimensionless else str(q.units)
        self.set_value(q.magnitude)

    def clone(self) -> Tag:
        return Tag(self.name, self.value, self.unit)


class ReadingTag(Tag):
    def __init__(self, name: str, unit: str | None = None) -> None:
        super().__init__(name, value=0.0, unit=unit, direction=TagDirection.INPUT)


class SelectTag(Tag):
    def __init__(self, name: str, value, unit: str | None ,
                 choices: List[str], direction: TagDirection = TagDirection.NA) -> None:
        super().__init__(name, value, unit, direction)
        if choices is None or len(choices) == 0:
            raise ValueError("choices must be non-empty")
        self.choices = choices

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
    """ Represents a  name/tag dictionary. """

    def __init__(self) -> None:
        super().__init__()
        self.tags: Dict[str, Tag] = {}

    def as_readonly(self) -> TagValueCollection:
        return TagValueCollection([t.as_readonly() for t in self.tags.values()])

    # propagate tag changes to collection changes
    def notify_change(self, elm: str):
        self.notify_listeners(elm)

    @property
    def names(self) -> List[str]:
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

    def clone(self) -> TagCollection:
        """ Returns a deep clone of the collection. """
        tags = TagCollection()
        for tag in self.tags.values():
            tags.add(tag.clone())
        return tags

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
        tags = TagCollection()
        defaults = [
            (SystemTagName.BASE, "min", None),  # TODO this should not be wrapped in pint quantity
            (SystemTagName.RUN_COUNTER, 0, None),
            (SystemTagName.BLOCK_TIME, 0.0, "s"),
            (SystemTagName.PROCESS_TIME, 0.0, "s"),
            (SystemTagName.RUN_TIME, 0.0, "s"),
            (SystemTagName.CLOCK, 0.0, "s"),
            (SystemTagName.SYSTEM_STATE, "Stopped", None),
            (SystemTagName.METHOD_STATUS, "OK", None),
        ]
        for name, value, unit in defaults:
            tag = Tag(name, value, unit, TagDirection.NA)
            tags.add(tag)
        return tags


class TagValue():
    """ Read-only and immutable representation of a tag value. """
    def __init__(
            self,
            name: str,
            value: TagValueType = None,
            unit: str | None = None
    ):
        if name is None or name.strip() == '':
            raise ValueError("name is None or empty")

        self.name = name
        self.value = value
        self.unit = unit


class TagValueCollection(Iterable[TagValue]):
    """ Represents a read-only and immutable dictionary of tag values. """

    def __init__(self, values: Iterable[TagValue]) -> None:
        super().__init__()
        self._tag_values: Dict[str, TagValue] = {}
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
