from __future__ import annotations

import logging
from typing import Any, Callable

from openpectus.engine.commands import ContextEngineCommand, CommandArgs
from openpectus.engine.hardware import HardwareLayerBase, NullHardware, Register, RegisterDirection
from openpectus.lang.exec.base_unit import BaseUnitProvider
from openpectus.lang.exec.errors import UodValidationError
from openpectus.lang.exec.readings import Reading, ReadingCollection
from openpectus.lang.exec.tags import TAG_UNITS, SystemTagName, Tag, TagCollection
from openpectus.lang.exec.tags_impl import AccumulatorBlockTag, AccumulatedColumnVolume, AccumulatorTag
from openpectus.protocol.models import PlotConfiguration

logger = logging.getLogger(__name__)


class UnitOperationDefinitionBase:
    """ Represets the Unit Operation Definition interface used by the OpenPectus engine.
    """
    def __init__(self,
                 instrument_name: str,
                 hwl: HardwareLayerBase,
                 location: str,
                 tags: TagCollection,
                 readings: ReadingCollection,
                 command_factories: dict[str, UodCommandBuilder],
                 overlapping_command_names_lists: list[list[str]],
                 plot_configuration: PlotConfiguration,
                 base_unit_provider: BaseUnitProvider
                 ) -> None:
        self.instrument = instrument_name
        self.hwl = hwl
        self.location = location
        self.tags = tags
        self.system_tags: TagCollection | None = None
        self.readings = readings
        self.command_factories = command_factories
        self.command_instances: dict[str, UodCommand] = {}
        self.overlapping_command_names_lists: list[list[str]] = overlapping_command_names_lists
        self.plot_configuration = plot_configuration
        self.base_unit_provider: BaseUnitProvider = base_unit_provider

    def define_register(self, name: str, direction: RegisterDirection, **options):
        assert isinstance(self.hwl, HardwareLayerBase)
        self.hwl.registers[name] = Register(name, direction, **options)

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
        """ Check whether the command name is defined in the Uod """
        if name.strip() == "":
            raise ValueError("Command name is None or empty")
        return name in self.command_factories.keys()

    def has_command_instance(self, name: str) -> bool:
        """ Check whether the Uod currently has an active instance of the named command """
        if name.strip() == "":
            raise ValueError("Command name is None or empty")
        return name in self.command_instances.keys()

    def has_any_command_instances(self) -> bool:
        return len(self.command_instances) > 0

    def create_command(self, name: str) -> UodCommand:
        """ Create a new command instance. Only one command instance with a given name can exist at a time. """
        if name.strip() == "":
            raise ValueError("Command name is None or empty")
        if self.has_command_instance(name):
            raise ValueError(f"Command {name} instance already exists")
        factory = self.command_factories.get(name)
        if factory is None:
            raise ValueError(f"Command {name} not found")
        instance = factory.build(self)
        self.command_instances[name] = instance
        return instance

    def dispose_command(self, cmd: UodCommand):
        """ Remove command from list of instances """
        if self.has_command_instance(cmd.name):
            self.command_instances.pop(cmd.name)

    def get_command(self, name: str) -> UodCommand | None:
        """ Get existing command instance by name """
        if name.strip() == "":
            raise ValueError("Command name is None or empty")
        if self.has_command_instance(name):
            return self.command_instances[name]
        raise ValueError(f"Command instance named '{name}' not found")

    def get_command_names(self) -> list[str]:
        return list(self.command_factories.keys())

    def validate_tag_name(self, tag_name: str) -> bool:
        return tag_name in self.tags.names

    def validate_command_name(self, command_name: str) -> bool:
        return command_name in self.get_command_names()


INIT_FN = Callable[[], None]
""" Command initialization method. """

EXEC_FN = Callable[..., None]
""" Command execution function. Must take UodCommand and **kvargs as inputs. May be invoked multiple times. """

FINAL_FN = Callable[[], None]
""" Command finalization method. """

PARSE_FN = Callable[[str | None], CommandArgs | None]
""" Command argument parse function. Parses a string into a dictionary. Returns None on invalid input. """



class UodCommand(ContextEngineCommand[UnitOperationDefinitionBase]):
    """ Represents a command that targets hardware, such as setting a valve state.

    Uod commands are specified/implemented by using the UodCommandBuilder class.
    """
    def __init__(self, context: UnitOperationDefinitionBase, name: str) -> None:
        super().__init__(context, name)
        self.init_fn: INIT_FN | None = None
        self.exec_fn: EXEC_FN | None = None
        self.finalize_fn: FINAL_FN | None = None
        self.arg_parse_fn: PARSE_FN | None = None

    @staticmethod
    def builder() -> UodCommandBuilder:
        """ Helper method that provides a command builder object that must be used to
        specify the command. """
        return UodCommandBuilder()

    def initialize(self):
        super().initialize()

        if self.init_fn is not None:
            self.init_fn()

    def execute(self, args: CommandArgs) -> None:
        if self.exec_fn is None:
            raise ValueError(f"Command '{self.name}' has no execution function defined")

        if not isinstance(args, dict):
            raise TypeError(
                f"Invalid arguments provided to command '{self.name}'. Must be a dictionary, not {type(args).__name__}")

        super().execute(args)
        self.exec_fn(args)

    def cancel(self):
        super().cancel()
        self.context.dispose_command(self)

    def finalize(self):
        super().finalize()

        if self.finalize_fn is not None:
            self.finalize_fn()

        self.context.dispose_command(self)

    def parse_args(self, args: str | None) -> CommandArgs | None:
        """ Parse argument input to concrete values. Return None to indicate invalid arguments. """
        if self.arg_parse_fn is None:
            return {}
        else:
            return self.arg_parse_fn(args)


class UodCommandBuilder():
    def __init__(self) -> None:
        self.name = ""
        self.init_fn: Callable[[UodCommand], None] | None = None
        self.exec_fn: Callable[[UodCommand, Any], None] | None = None
        self.finalize_fn: Callable[[UodCommand], None] | None = None
        self.arg_parse_fn: Callable[[str | None], CommandArgs | None] | None = None

    def with_name(self, name: str) -> UodCommandBuilder:
        """ Define the name of the command. Required. """
        self.name = name
        return self

    def with_init_fn(self, init_fn: Callable[[UodCommand], None]) -> UodCommandBuilder:
        """ Define an initialization function for the command. Optional. """
        self.init_fn = init_fn
        return self

    def with_exec_fn(self, exec_fn: Callable[..., None]) -> UodCommandBuilder:
        """ Define the command's execution function. Required.

        Example::

          def my_command_exec(cmd: UodCommand, **kvargs):
              # kvargs contains the result of the arg_parse function.
              pass

        """
        self.exec_fn = exec_fn
        return self

    def with_finalize_fn(self, finalize_fn: Callable[[UodCommand], None]) -> UodCommandBuilder:
        """ Define a finalizer function for the command. Optional. """
        self.finalize_fn = finalize_fn
        return self

    def with_arg_parse_fn(self, arg_parse_fn: Callable[[str | None], CommandArgs | None]) \
            -> UodCommandBuilder:
        """ Define an argument parser function. Optional.

        The function is given the command argument string from the method and should parse that
        and return the result as a dictionary. The result is passed to the excution function automatically.

        If not arg_parse function is defined, no arguments are provided to the execute function.

        Example::

          def my_command_parse_args(args: str | None) -> dict[str, Any] | None:
            # parse the argument string and return the values as a dictionary.
            return None # if args are invalid.
        """
        self.arg_parse_fn = arg_parse_fn
        return self

    def build(self, uod: UnitOperationDefinitionBase) -> UodCommand:

        def arg_parse(args: str | None) -> CommandArgs | None:
            if self.arg_parse_fn is None:
                return {}
            return self.arg_parse_fn(args)

        def initialize() -> None:
            if self.init_fn is not None:
                return self.init_fn(c)

        def execute(args: CommandArgs) -> None:
            if self.exec_fn is not None:
                try:
                    return self.exec_fn(c, **args)  # type: ignore
                except TypeError:
                    logger.error(
                        f"Could not call the execution function for the uod command '{self.name}'. " +
                        "Make sure the function signature is 'def exec(uod: UodCommand, **kvargs)'"
                    )
                    raise Exception(f"Execution function type error in uod command '{self.name}'")

        def finalize() -> None:
            if self.finalize_fn is not None:
                return self.finalize_fn(c)

        if self.name is None or self.name.strip() == '':
            raise ValueError("Name is not set")
        c = UodCommand(uod, self.name)
        c.init_fn = initialize
        c.exec_fn = execute
        c.finalize_fn = finalize
        c.arg_parse_fn = arg_parse
        return c


class UodBuilder():
    def __init__(self) -> None:
        self.instrument: str = ""
        self.hwl: HardwareLayerBase | None = None
        self.tags = TagCollection()
        self.commands: dict[str, UodCommandBuilder] = {}
        self.overlapping_command_names_lists: list[list[str]] = []
        self.readings = ReadingCollection()
        self.location: str = ""
        self.plot_configuration: PlotConfiguration | None = None
        self.base_unit_provider: BaseUnitProvider = BaseUnitProvider()
        self.base_unit_provider.set("s", SystemTagName.BLOCK_TIME, SystemTagName.BLOCK_TIME)
        self.base_unit_provider.set("min", SystemTagName.BLOCK_TIME, SystemTagName.BLOCK_TIME)
        self.base_unit_provider.set("h", SystemTagName.BLOCK_TIME, SystemTagName.BLOCK_TIME)

    def get_logger(self):
        return logging.getLogger(f'{__name__}.user_uod')

    def validate(self):
        if len(self.instrument.strip()) == 0:
            raise ValueError("Instrument name must be set")

        if self.hwl is None:
            raise ValueError("HardwareLayer must be set")

        return

    def with_instrument(self, instrument_name: str) -> UodBuilder:
        if len(instrument_name.strip()) == 0:
            raise ValueError("Instrument name cannot be empty")

        self.instrument = instrument_name
        return self

    def with_hardware(self, hwl: HardwareLayerBase) -> UodBuilder:
        self.hwl = hwl
        return self

    def with_location(self, location: str) -> UodBuilder:
        self.location = location
        return self

    def with_hardware_register(self, name: str, direction: RegisterDirection, **options) -> UodBuilder:
        if self.hwl is None:
            raise ValueError("HardwareLayber must be defined before defining a register")
        if name in self.hwl.registers.keys():
            raise ValueError(f"Register {name} already defined")
        self.hwl.registers[name] = Register(name, direction, **options)
        return self

    def with_no_hardware(self):
        self.hwl = NullHardware()
        return self

    def with_tag(self, tag: Tag) -> UodBuilder:
        # TODO Replace Tag as input with TagBuilder
        if self.tags.has(tag.name):
            raise ValueError(f"Duplicate tag name: {tag.name}")
        self.tags.add(tag)
        return self

    def with_accumulated_volume(self, totalizer_tag_name: str) -> UodBuilder:
        if not self.tags.has(totalizer_tag_name):
            raise ValueError(f"The specified totalizer tag name '{totalizer_tag_name}' was not found")
        totalizer = self.tags[totalizer_tag_name]
        volume_units = TAG_UNITS["volume"]
        if totalizer.unit not in volume_units:
            raise ValueError(f"The totalizer tag '{totalizer_tag_name}' must have a volume unit")
        self.with_tag(AccumulatorTag(name=SystemTagName.ACCUMULATED_VOLUME, totalizer=totalizer))
        self.with_tag(AccumulatorBlockTag(name=SystemTagName.BLOCK_VOLUME, totalizer=totalizer))
        self.with_base_unit_provider(volume_units, SystemTagName.ACCUMULATED_VOLUME, SystemTagName.BLOCK_VOLUME)
        return self

    def with_accumulated_cv(self, cv_tag_name: str, totalizer_tag_name: str) -> UodBuilder:
        if not self.tags.has(cv_tag_name):
            raise ValueError(f"The specified column volume tag name '{cv_tag_name}' was not found")
        if not self.tags.has(totalizer_tag_name):
            raise ValueError(f"The specified totalizer tag name '{totalizer_tag_name}' was not found")
        cv = self.tags[cv_tag_name]
        totalizer = self.tags[totalizer_tag_name]
        self.with_tag(AccumulatedColumnVolume(SystemTagName.ACCUMULATED_CV, cv, totalizer))
        acc_cv = self.tags[SystemTagName.ACCUMULATED_CV]
        self.with_tag(AccumulatorBlockTag(SystemTagName.BLOCK_CV, acc_cv))
        self.with_base_unit_provider(["CV"], SystemTagName.ACCUMULATED_CV, SystemTagName.BLOCK_CV)
        return self

    def with_base_unit_provider(self, units: list[str], provider_tag_name: str, provider_block_tag_name: str):
        if provider_tag_name is None or provider_tag_name.strip() == "":
            raise ValueError("provider_tag_name is required")
        if not self.tags.has(provider_tag_name):
            raise ValueError(f"The specified provider_tag_name '{provider_tag_name}' was not found ")
        if provider_block_tag_name is None or provider_block_tag_name.strip() == "":
            raise ValueError("provider_block_tag_name is required")
        if not self.tags.has(provider_block_tag_name):
            raise ValueError(f"The specified provider_block_tag_name '{provider_block_tag_name}' was not found ")

        if len(units) == 0:
            raise ValueError("At least one unit is required")
        for unit in units:
            if self.base_unit_provider.has(unit):
                logger.warning(f"The base unit provider for unit '{unit}' was \
                               overwritten with tag name '{provider_tag_name}'")
            self.base_unit_provider.set(unit, provider_tag_name, provider_block_tag_name)
        return self

    def with_command(self, cb: UodCommandBuilder) -> UodBuilder:
        # TODO improve usage by creating UodCommandBuilder and exposing it via a Context
        if cb.name in self.commands.keys():
            raise ValueError(f"Duplicate command name: {cb.name}")
        self.commands[cb.name] = cb
        return self

    def with_command_overlap(self, command_names: list[str]) -> UodBuilder:
        if len(command_names) < 2:
            raise ValueError("To define command overlap, at least two command names are required")
        self.overlapping_command_names_lists.append(command_names)
        return self

    def with_process_value(self, pv: Reading) -> UodBuilder:
        self.readings.add(pv)
        return self

    def with_plot_configuration(self, plot_configuration: PlotConfiguration):
        self.plot_configuration = plot_configuration
        return self

    def build(self) -> UnitOperationDefinitionBase:
        self.validate()

        uod = UnitOperationDefinitionBase(
            self.instrument,
            self.hwl,  # type: ignore
            self.location,
            self.tags,
            self.readings,
            self.commands,
            self.overlapping_command_names_lists,
            self.plot_configuration or PlotConfiguration.empty(),
            self.base_unit_provider
        )

        return uod
