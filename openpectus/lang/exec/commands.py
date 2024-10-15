from __future__ import annotations
from enum import StrEnum
from typing import Any, Callable, Dict, List
from uuid import UUID


class InterpreterCommandEnum(StrEnum):
    """ Commands (instructions of type PCommand) that are executed by the interpreter """
    BASE = "Base"
    INCREMENT_RUN_COUNTER = "Increment run counter"
    RUN_COUNTER = "Run counter"

    @staticmethod
    def has_value(value: str):
        """ Determine if enum has this string value defined. Case sensitive. """
        return value in InterpreterCommandEnum.__members__.values()


# Represents part of Engine API


class CommandRequest():
    """ Represents a command request for engine to execute. """
    def __init__(self, name: str, source: str, exec_id: UUID | None = None, kvargs: dict[str, Any] = {}) -> None:
        self.name: str = name
        self.unparsed_args: str | None = None
        self.kvargs: dict[str, Any] | None = kvargs
        self.exec_id: UUID | None = exec_id
        self.source: str = source

        # allows tracking individual commands
        self.command_exec_id: UUID | None = None

    @staticmethod
    def from_user(name: str, unparsed_args: str | None = None) -> CommandRequest:
        cmd_req = CommandRequest(name=name, source='user')
        cmd_req.unparsed_args = unparsed_args
        return cmd_req

    @staticmethod
    def from_interpreter(name: str, exec_id: UUID | None, **kvargs) -> CommandRequest:
        if "unparsed_args" in kvargs.keys():
            cmd_req = CommandRequest(name=name, source="@interpreter", exec_id=exec_id)
            cmd_req.unparsed_args = kvargs["unparsed_args"]
            return cmd_req
        else:
            return CommandRequest(name=name, source="@interpreter", exec_id=exec_id, kvargs=kvargs)

    def __str__(self) -> str:
        return f"EngineCommand {self.name} | kvargs: {str(self.kvargs)} | unparsed_args: {self.unparsed_args}"

    def get_args(self) -> dict[str, Any]:
        if self.kvargs is None or (self.kvargs == {} and self.unparsed_args is not None):
            return {"unparsed_args": self.unparsed_args}
        else:
            return self.kvargs


# Represents command API towards interpreter
# Used by analyzers


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
        """ Returns a new CommandCollection with the combined commands of both collections.

        In case of duplicate commands names, tags from other collection are used.
        """
        cmds = CommandCollection()
        for cmd in self.commands.values():
            cmds.add(cmd)
        for cmd in other.commands.values():
            cmds.add(cmd)
        return cmds
