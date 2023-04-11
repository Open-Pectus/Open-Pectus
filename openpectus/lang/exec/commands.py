from __future__ import annotations
from typing import Callable, Dict, List

# Represents command API towards interpreter


class Command:
    """ Represents a named command. """
    def __init__(self, name: str, validatorFn: Callable[[str], bool] | None = None) -> None:
        self.name: str = name
        self.validatorFn = validatorFn

    def is_complete(self) -> bool:
        return True

    def validate_args(self, args: str) -> bool:
        valid = True
        if self.validatorFn is not None:
            valid = self.validatorFn(args)
        return valid

    def clone(self) -> Command:
        return Command(self.name)


class CommandCollection():
    """ Represents a case insensitive name/command dictionary. """

    def __init__(self) -> None:
        self.commands: Dict[str, Command] = {}

    @property
    def names(self) -> List[str]:
        """ Return the tag names in upper case. """
        return list(self.commands.keys())

    def __getitem__(self, tag_name: str):
        return self.commands[tag_name.upper()]

    def get(self, cmd_name: str) -> Command:
        if cmd_name is None or cmd_name.strip() == '':
            raise ValueError("cmd_name is None or empty")
        if not cmd_name.upper() in self.commands.keys():
            raise ValueError(f"Command name {cmd_name} not found")
        return self[cmd_name]

    def add(self, cmd: Command, exist_ok: bool = True):
        """ Add command to collection. If command name already exists and exist_ok is False, a ValueError is raised. """
        if cmd is None:
            raise ValueError("cmd is None")
        if cmd.name is None or cmd.name.strip() == '':
            raise ValueError("cmd name is None or empty")
        if cmd.name in self.commands.keys() and not exist_ok:
            raise ValueError(f"A command named {cmd.name} already exists")

        self.commands[cmd.name.upper()] = cmd

    def with_cmd(self, cmd: Command):
        self.add(cmd)
        return self

    def has(self, cmd_name: str) -> bool:
        if cmd_name is None or cmd_name.strip() == '':
            raise ValueError("cmd_name is None or empty")
        return cmd_name.upper() in self.commands.keys()

    def clone(self) -> CommandCollection:
        """ Returns a deep clone of the collection. """
        cmds = CommandCollection()
        for cmd in self.commands.values():
            cmds.add(cmd.clone())
        return cmds

    def merge_with(self, other: CommandCollection) -> CommandCollection:
        """ Returns a new CommandCollection with the combined commands
        of both collections.

        In case of duplicate commands names, tags from other collection
        are used.
        """
        cmds = CommandCollection()
        for cmd in self.commands.values():
            cmds.add(cmd)
        for cmd in other.commands.values():
            cmds.add(cmd)
        return cmds
