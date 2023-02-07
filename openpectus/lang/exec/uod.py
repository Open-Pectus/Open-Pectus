
from typing import List

from lang.exec.tags import TagCollection


class UnitOperationDefinitionBase:
    """ Represets the Unit Operation Definition interface used by the Pectus intepreter.

    The interface specifies:
        Process values (tags)
        Custom tags
        Custom commands
        Mapping of process value tags to physical I/O
    """
    def __init__(self) -> None:
        self.tags = TagCollection()
        self.command_names: List[str] = []

    def get_command_names(self) -> List[str]:
        return self.command_names

    def validate_command_name(self, command_name: str) -> bool:
        return command_name in self.command_names

    def validate_command_args(self, command_name: str, command_args: str | None = None) -> bool:
        return True

    def execute_command(self, command_name: str, command_args: str | None = None) -> None:
        pass
