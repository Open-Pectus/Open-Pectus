
class BaseUnitProvider:
    """ Manages a mapping between units that can be used in the Base instruction and
    the tags that provides the value in non-block and block scopes. """
    def __init__(self) -> None:
        self.map: dict[str, tuple[str, str]] = {}

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(units={self.get_units()})'

    def has(self, unit: str) -> bool:
        return unit in self.map.keys()

    def set(self, unit: str, main_tag_name: str, block_tag_name: str):
        self.map[unit] = (main_tag_name, block_tag_name)

    def get_units(self) -> list[str]:
        return list(self.map.keys())

    def get_tags(self, unit: str) -> tuple[str, str]:
        if unit not in self.map.keys():
            raise ValueError(f"Unit '{unit}' is not registered")
        return self.map[unit]
