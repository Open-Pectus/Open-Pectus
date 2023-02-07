
from typing import Dict


class Tag:
    def __init__(self, name: str = "", value: str = "") -> None:
        self.name: str = name
        self.value: str = value

    def set_value(self, val: str) -> None:
        self.value = val

    def get_value(self) -> str:
        return self.value


class TagCollection(Dict[str, Tag]):
    pass
