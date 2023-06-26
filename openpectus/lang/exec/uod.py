from __future__ import annotations
from typing import Any, Callable, Dict, List

from openpectus.lang.exec.tags import Tag, TagCollection
from openpectus.engine.hardware import HardwareLayerBase, Register, RegisterDirection


class UnitOperationDefinitionBase:
    # TODO split into two classes: definition for interpreter and execution for engine
    """ Represets the Unit Operation Definition interface used by the Pectus engine and intepreter.

    It consists of two parts - the machine definition part (interpreter) and the execution part (engine).

    The interface specifies:
        Process values (tags)
        Custom tags
        Custom commands
        Mapping of process value tags to physical I/O
    """
    def __init__(self) -> None:
        self.instrument = ""
        self.hwl: HardwareLayerBase | None = None
        self.tags = TagCollection()
        self.commands: Dict[str, UodCommand] = {}
        self.io_map: Dict[str, Dict] = {}

    def define_instrument(self, instrument: str):
        self.instrument = instrument

    def define_hardware_layer(self, hwl: HardwareLayerBase):
        self.hwl = hwl

    def define_io(self, name: str, data: dict):
        self.io_map[name] = data

    def define_tag(self, t: Tag):
        self.tags.add(t)

    def define_register(self, name: str, direction: RegisterDirection, **options):
        assert isinstance(self.hwl, HardwareLayerBase)
        self.hwl.registers[name] = Register(name, direction, **options)

    def define_command(self, c: UodCommand):
        if c.name is None or c.name.strip() == "":
            raise ValueError("Command name is None or empty")
        if c.name.lower() in self.commands.keys():
            raise ValueError(f"Command name {c.name} is already defined")
        self.commands[c.name.lower()] = c

    def define(self):
        raise NotImplementedError()

    def validate_configuration(self):
        if self.instrument is None or self.instrument.strip() == "":
            raise ValueError("instrument is not configured")
        if self.hwl is None:
            raise ValueError("hwl is not configured")

    def get_command(self, name: str) -> UodCommand | None:
        if name is None or name.strip() == "":
            raise ValueError("Command name is None or empty")
        return self.commands.get(name.lower(), None)

    def get_command_names(self, as_lower=True) -> List[str]:
        def to_case(name: str):
            if as_lower:
                return name.lower()
            return name
        return list([to_case(c_name) for c_name in self.commands.keys()])

    def validate_tag_name(self, tag_name: str) -> bool:
        return tag_name.upper() in self.tags.names

    def validate_command_name(self, command_name: str) -> bool:
        return command_name.lower() in self.get_command_names(as_lower=True)

    def validate_command_args(self, command_name: str, command_args: str | None) -> bool:
        if not self.validate_command_name(command_name):
            return True
        cmd = self.get_command(command_name)
        assert cmd is not None
        return cmd.parse_args(command_args, self) is not None

    def execute_command(self, command_name: str, command_args: str | None) -> None:
        cmd = self.get_command(command_name)
        if cmd is not None:
            parsed_args = cmd.parse_args(command_args, self)
            if parsed_args is None:
                raise ValueError(f"Invalid arguments '{command_args}' provided for command '{cmd.name}'")
            else:
                cmd.execute(parsed_args, self)

                if cmd.is_complete:
                    # TODO reset the command - possibly a reset() method
                    cmd.iterations = 0
                else:
                    cmd.iterations += 1
                    pass


class UodCommand():
    """ Represents a command that targets hardware, such as setting a valve state. """
    def __init__(self) -> None:
        self.name: str = ""

        # TODO consider generalizing to use a UodCommandContext object
        self.exec_fn: Callable[[List[Any], UnitOperationDefinitionBase], None] | None = None
        self.arg_parse_fn: Callable[[str | None, UnitOperationDefinitionBase], None] | None = None
        # TODO progress, "i", ...
        # TODO does it make sence for command
        # - return a value?
        # - not have exec function?
        self.is_complete: bool = True
        self.iterations: int = 0

    @staticmethod
    def builder() -> UodCommandBuilder:
        return UodCommandBuilder()

    def execute(self, args: List[Any], uod: UnitOperationDefinitionBase) -> None:
        if self.exec_fn is None:
            raise ValueError(f"Command '{self.name}' has no execution function defined")
        else:
            return self.exec_fn(args, uod)
        
    # TODO initialize(), finalize(), completed(), cancelled()

    def parse_args(self, args: str | None, uod: UnitOperationDefinitionBase) -> List[Any] | None:
        """ Parse argument input to concrete values. Return None to indicate invalid arguments. """
        if self.arg_parse_fn is None:
            return []
        else:
            return self.arg_parse_fn(args, uod)


class UodCommandBuilder():
    def __init__(self) -> None:
        self.name = ""
        self.exec_fn: Callable[[List[Any], UnitOperationDefinitionBase], None] | None = None
        self.arg_parse_fn: Callable[[str | None, UnitOperationDefinitionBase], None] | None = None

    def with_name(self, name: str) -> UodCommandBuilder:
        self.name = name
        return self

    def with_exec_fn(self, exec_fn: Callable[[List[Any], UnitOperationDefinitionBase], None]) -> UodCommandBuilder:
        self.exec_fn = exec_fn
        return self

    def with_arg_parse_fn(self, arg_parse_fn: Callable[[str | None, UnitOperationDefinitionBase], None])\
            -> UodCommandBuilder:
        self.arg_parse_fn = arg_parse_fn
        return self

    def build(self) -> UodCommand:
        c = UodCommand()
        if self.name is None or self.name.strip() == '':
            raise ValueError("Name is not set")
        c.name = self.name
        if self.exec_fn is not None:
            c.exec_fn = self.exec_fn
        return c
