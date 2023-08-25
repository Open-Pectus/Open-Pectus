from __future__ import annotations
from typing import Any, Callable, Dict, List
import logging
from openpectus.lang.exec.errors import UodValidationError
from openpectus.lang.exec.readings import Reading, ReadingCollection
from openpectus.lang.exec.tags import Tag, TagCollection
from openpectus.engine.hardware import HardwareLayerBase, Register, RegisterDirection
from openpectus.engine.commands import EngineCommand

logger = logging.getLogger(__name__)


class UnitOperationDefinitionBase:
    # TODO decide on casing behavior for names of tags, registers and commands
    # TODO Define a builder for constructing the Uod. This is only needed by tests and entry point to set it up,
    # and not by all other references.
    # This will remove the clutter from the uod interface and also make it immutable
    #   (only its structure, commands and tags - not its values)
    """ Represets the Unit Operation Definition interface used by the Pectus engine and intepreter.

    It consists of two parts - the machine definition part (interpreter) and the execution part (engine).

    The interface specifies:
        Custom tags
        Custom commands
        Mapping of process value tags to physical I/O
        Process values (which tags as displayed and possibly a command to modify them)
    """
    def __init__(self,
                 instrument_name: str,
                 hwl: HardwareLayerBase,
                 tags: TagCollection,
                 system_tags: TagCollection,
                 readings: ReadingCollection,
                 command_factories: Dict[str, UodCommandBuilder]) -> None:
        self.instrument = instrument_name
        self.hwl = hwl
        self.tags = tags
        self.system_tags = system_tags
        self.readings = readings
        self.command_factories = command_factories
        self.command_instances: Dict[str, UodCommand] = {}

    def define_register(self, name: str, direction: RegisterDirection, **options):
        assert isinstance(self.hwl, HardwareLayerBase)
        self.hwl.registers[name] = Register(name, direction, **options)

    def define_command(self, cb: UodCommandBuilder):
        if cb.name is None or cb.name.strip() == "":
            raise ValueError("Command name is None or empty")
        if cb.name.lower() in self.command_factories.keys():
            raise ValueError(f"Command name {cb.name} is already defined")
        self.command_factories[cb.name.lower()] = cb

    def validate_configuration(self):
        fatal = False

        def log_fatal(msg: str):
            nonlocal fatal
            if not fatal:
                logger.fatal("An error occured while validating the Unit Operation Definition. Pectus Engine cannot start.")
            fatal = True
            logger.fatal(msg)

        if self.instrument is None or self.instrument.strip() == "":
            log_fatal("Instrument is not configured")
        if self.hwl is None:
            log_fatal("Hardware Layer is not configured")

        if self.system_tags is None:
            log_fatal("System tags have not been set")
        else:
            tags = self.tags.merge_with(self.system_tags)
            for r in self.readings:
                try:
                    r.match_with_tags(tags)
                except UodValidationError as vex:
                    logging.error(vex.args[0])

        if fatal:
            exit(1)

    def has_command_name(self, name: str) -> bool:
        if name.strip() == "":
            raise ValueError("Command name is None or empty")
        return name in self.command_factories.keys()

    def has_command_instance(self, name: str) -> bool:
        if name.strip() == "":
            raise ValueError("Command name is None or empty")
        return name in self.command_instances.keys()

    def create_command(self, name: str) -> UodCommand:
        if name.strip() == "":
            raise ValueError("Command name is None or empty")
        if self.has_command_instance(name):
            raise ValueError(f"Command {name} instance already exists")
        factory = self.command_factories.get(name)
        if factory is None:
            raise ValueError(f"Command {name} not found")
        return factory.build(self)

    def get_command(self, name: str) -> UodCommand | None:
        if name.strip() == "":
            raise ValueError("Command name is None or empty")
        if self.has_command_instance(name):
            return self.get_command(name)
        return None

    def get_or_create_command(self, name: str) -> UodCommand:
        if name.strip() == "":
            raise ValueError("Command name is None or empty")

        if self.has_command_instance(name):
            return self.get_command(name)  # type: ignore
        else:
            return self.create_command(name)

    def get_command_names(self, as_lower=True) -> List[str]:
        def to_case(name: str):
            if as_lower:
                return name.lower()
            return name
        return list([to_case(c_name) for c_name in self.command_factories.keys()])

    def validate_tag_name(self, tag_name: str) -> bool:
        return tag_name.upper() in self.tags.names

    def validate_command_name(self, command_name: str) -> bool:
        return command_name.lower() in self.get_command_names(as_lower=True)

    def validate_command_args(self, command_name: str, command_args: str | None) -> bool:
        raise NotImplementedError("TODO Requires command instance - ")  # TODO fix this somehow for interpreter
        if not self.validate_command_name(command_name):
            return True
        cmd = self.get_command(command_name)
        assert cmd is not None
        return cmd.parse_args(command_args, self) is not None


class UodCommand(EngineCommand[UnitOperationDefinitionBase]):
    """ Represents a command that targets hardware, such as setting a valve state.

    Uod commands are specified/implemented by using the UodCommandBuilder class.
    """
    def __init__(self, context: UnitOperationDefinitionBase) -> None:
        super().__init__(context)
        self.name: str = ""
        self.init_fn: Callable[[], None] | None = None
        self.exec_fn: Callable[[List[Any]], None] | None = None
        self.finalize_fn: Callable[[], None] | None = None
        self.arg_parse_fn: Callable[[str | None], None] | None = None

    @staticmethod
    def builder() -> UodCommandBuilder:
        """ Helper method that provides a command builder object that must be used to
        specify the command. """
        return UodCommandBuilder()

    def initialize(self):
        super().initialize()

        if self.init_fn is not None:
            self.init_fn()

    def execute(self, args: List[Any]) -> None:
        if self.exec_fn is None:
            raise ValueError(f"Command '{self.name}' has no execution function defined")

        super().execute(args)
        self.exec_fn(args)

    def finalize(self):
        super().finalize()

        if self.finalize_fn is not None:
            self.finalize_fn()

    def parse_args(self, args: str | None, uod: UnitOperationDefinitionBase) -> List[Any] | None:
        """ Parse argument input to concrete values. Return None to indicate invalid arguments. """
        if self.arg_parse_fn is None:
            return []
        else:
            return self.arg_parse_fn(args)


class UodCommandBuilder():
    def __init__(self) -> None:
        self.name = ""
        self.init_fn: Callable[[UodCommand], None] | None = None
        self.exec_fn: Callable[[UodCommand, List[Any]], None] | None = None
        self.finalize_fn: Callable[[UodCommand], None] | None = None
        self.arg_parse_fn: Callable[[str | None], None] | None = None

    def with_name(self, name: str) -> UodCommandBuilder:
        self.name = name
        return self

    def with_init_fn(self, init_fn: Callable[[UodCommand], None]) \
            -> UodCommandBuilder:
        self.init_fn = init_fn
        return self

    def with_exec_fn(self, exec_fn: Callable[[UodCommand, List[Any]], None]) \
            -> UodCommandBuilder:
        self.exec_fn = exec_fn
        return self

    def with_finalize_fn(self, finalize_fn: Callable[[UodCommand], None]) \
            -> UodCommandBuilder:
        self.finalize_fn = finalize_fn
        return self

    # TODO consider removing None as argument. Does  not seem to make sence
    def with_arg_parse_fn(self, arg_parse_fn: Callable[[str | None], None]) \
            -> UodCommandBuilder:
        self.arg_parse_fn = arg_parse_fn
        return self

    def build(self, uod: UnitOperationDefinitionBase) -> UodCommand:

        def initialize() -> None:
            if self.init_fn is not None:
                return self.init_fn(c)

        def execute(args: List[Any]) -> None:
            if self.exec_fn is not None:
                return self.exec_fn(c, args)

        def finalize() -> None:
            if self.finalize_fn is not None:
                return self.finalize_fn(c)

        c = UodCommand(uod)
        if self.name is None or self.name.strip() == '':
            raise ValueError("Name is not set")
        c.name = self.name
        c.init_fn = initialize
        c.exec_fn = execute
        c.finalize_fn = finalize
        return c


class UodBuilder():
    def __init__(self) -> None:
        self.instrument: str = ""
        self.hwl: HardwareLayerBase | None = None
        self.tags = TagCollection()
        self.system_tags: TagCollection | None = None
        self.commands: Dict[str, UodCommandBuilder] = {}
        self.readings = ReadingCollection()

    def validate(self):
        if len(self.instrument.strip()) == 0:
            raise ValueError("Instrument name must be set")

        if self.hwl is None:
            raise ValueError("HardwareLayer must be set")

        if self.system_tags is None:
            raise ValueError("system_tags must be set")

        return

    def with_instrument(self, instrument_name: str) -> UodBuilder:
        if len(instrument_name.strip()) == 0:
            raise ValueError("Instrument name cannot be empty")

        self.instrument = instrument_name
        return self

    def with_hardware(self, hwl: HardwareLayerBase) -> UodBuilder:
        self.hwl = hwl
        return self

    def with_hardware_register(self, name: str, direction: RegisterDirection, **options) -> UodBuilder:
        if self.hwl is None:
            raise ValueError("HardwareLayber must be defined before defining a register")
        if name in self.hwl.registers.keys():
            raise ValueError(f"Register {name} already defined")
        self.hwl.registers[name] = Register(name, direction, **options)
        return self

    def with_tag(self, tag: Tag) -> UodBuilder:
        # TODO Replace Tag as input with TagBuilder
        if self.tags.has(tag.name):
            raise ValueError(f"Duplicate tag name: {tag.name}")
        self.tags.add(tag)
        return self

    def with_system_tags(self, system_tags: TagCollection) -> UodBuilder:
        self.system_tags = system_tags
        return self

    def with_new_system_tags(self) -> UodBuilder:
        return self.with_system_tags(TagCollection.create_system_tags())

    def with_command(self, cb: UodCommandBuilder) -> UodBuilder:
        if cb.name in self.commands.keys():
            raise ValueError(f"Duplicate command name: {cb.name}")
        self.commands[cb.name] = cb
        return self

    def with_process_value(self, pv: Reading) -> UodBuilder:
        self.readings.add(pv)
        return self

    def build(self) -> UnitOperationDefinitionBase:
        self.validate()

        uod = UnitOperationDefinitionBase(
            self.instrument,
            self.hwl,  # type: ignore
            self.tags,
            self.system_tags,  # type: ignore
            self.readings,
            self.commands)

        return uod
