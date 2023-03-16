from __future__ import annotations
from typing import Dict, List

DEFAULT_TAG_BASE = "BASE"
DEFAULT_TAG_RUN_COUNTER = "RUN COUNTER"
DEFAULT_TAG_BLOCK_TIME = "BLOCK TIME"


# TODO refactor to support pint units. Consider whether to hide pint or expose it.
# TODO add support for 'safe' values, ie. to allow specifying a value that is automatically
# set when interpretation state is one or more of stopped/paused/on hold

class Tag:
    def __init__(self, name: str = "", value: str = "") -> None:
        self.name: str = name
        self.value: str = value

    def set_value(self, val: str) -> None:
        self.value = val

    def get_value(self) -> str:
        return self.value

    def clone(self) -> Tag:
        return Tag(self.name, self.value)


# TODO probably add keys in upper case for case insensitive lookup
# TODO consider support for frozen tags, e.g. such that UOD is not allowed to mutate standard tags

class TagCollection():
    """ Represents a case insensitive name/tag dictionary. """

    def __init__(self) -> None:
        self.tags: Dict[str, Tag] = {}

    @property
    def names(self) -> List[str]:
        """ Return the tag names in upper case. """
        return list(self.tags.keys())

    def __getitem__(self, tag_name: str):
        return self.tags[tag_name.upper()]

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
    def create_default() -> TagCollection:
        tags = TagCollection()
        defaults = [
            (DEFAULT_TAG_BASE, "min"),
            (DEFAULT_TAG_RUN_COUNTER, "0"),
            (DEFAULT_TAG_BLOCK_TIME, "0"),
        ]
        for k, v in defaults:
            tags.add(Tag(k, v))
        return tags
