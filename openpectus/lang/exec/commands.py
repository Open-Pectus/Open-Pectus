from __future__ import annotations
from enum import StrEnum
from typing import Callable, Dict, Iterable, List
from uuid import UUID

from openpectus.lang.exec.uod import RegexNamedArgumentParser

class InterpreterCommandEnum(StrEnum):
    """ Commands (instructions of type PCommand) that are executed by the interpreter """
    BASE = "Base"
    INCREMENT_RUN_COUNTER = "Increment run counter"
    RUN_COUNTER = "Run counter"
    WAIT = "Wait"

    @staticmethod
    def has_value(value: str):
        """ Determine if enum has this string value defined. Case sensitive. """
        return value in InterpreterCommandEnum.__members__.values()


# Represents part of Engine API


class CommandRequest:
    """ Represents a command request for engine to execute. """
    def __init__(self, name: str, arguments: str, source: str, exec_id: UUID | None = None) -> None:
        self.name: str = name
        self.arguments: str = arguments
        self.exec_id: UUID | None = exec_id
        self.source: str = source

        # allows tracking individual commands
        self.command_exec_id: UUID | None = None

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(name="{self.name}", arguments={self.arguments}, ' +
                f'source="{self.source}", exec_id={self.exec_id}, command_exec_id={self.command_exec_id})')

    @staticmethod
    def from_user(name: str, arguments: str = "") -> CommandRequest:
        return CommandRequest(name=name, arguments=arguments, source='user')

    @staticmethod
    def from_interpreter(name: str, arguments: str, exec_id: UUID | None) -> CommandRequest:
        return CommandRequest(name=name, arguments=arguments, source="@interpreter", exec_id=exec_id)


# Represents command API towards interpreter
# Used by analyzers


class Command:
    """ Represents a named command. """
    def __init__(self, name: str, validatorFn: Callable[[str], bool] | None = None,
                 docstring: str | None = None, arg_parser: RegexNamedArgumentParser | None = None) -> None:
        self.name: str = name
        self.validatorFn = validatorFn
        self.docstring = docstring
        self.arg_parser = arg_parser

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(name="{self.name}")'

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
    """ Represents a name/command dictionary. """

    def __init__(self, commands: Iterable[Command] | None = None) -> None:
        self.commands: Dict[str, Command] = {}
        if commands is not None:
            for cmd in commands:
                self.add(cmd, False)

    def __str__(self) -> str:
        commands = [str(command) for command in self.commands]
        return f'{self.__class__.__name__}(commands={commands})'

    @property
    def names(self) -> List[str]:
        """ Return the command names """
        return list(self.commands.keys())

    def __getitem__(self, tag_name: str):
        return self.commands[tag_name]

    def get(self, cmd_name: str) -> Command:
        if cmd_name is None or cmd_name.strip() == '':
            raise ValueError("cmd_name is None or empty")
        if cmd_name not in self.commands.keys():
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

        self.commands[cmd.name] = cmd

    def with_cmd(self, cmd: Command):
        self.add(cmd)
        return self

    def has(self, cmd_name: str) -> bool:
        if cmd_name is None or cmd_name.strip() == '':
            raise ValueError("cmd_name is None or empty")
        return cmd_name in self.commands.keys()

    def clone(self) -> CommandCollection:
        """ Returns a deep clone of the collection. """
        cmds = CommandCollection()
        for cmd in self.commands.values():
            cmds.add(cmd.clone())
        return cmds

    def to_list(self):
        return list(self.commands.values())

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
