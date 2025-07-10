from __future__ import annotations

from inspect import _ParameterKind, Parameter
import logging
import re
from typing import Any, Callable, Literal, Tuple
import sys
import time

from openpectus.engine.commands import ContextEngineCommand, CommandArgs
from openpectus.engine.hardware import HardwareLayerBase, NullHardware, Register, RegisterDirection
from openpectus.lang.exec.argument_specification import ArgSpec
from openpectus.lang.exec.base_unit import BaseUnitProvider
from openpectus.lang.exec.errors import UodValidationError
from openpectus.lang.exec.readings import (
    Reading, ReadingCollection, ReadingWithChoice, ReadingWithEntry, UodCommandDescription
)
from openpectus.lang.exec.tags import SystemTagName, Tag, TagCollection
from openpectus.lang.exec.units import get_compatible_unit_names, get_volume_units, add_unit
from openpectus.lang.exec.tags_impl import AccumulatorBlockTag, AccumulatedColumnVolume, AccumulatorTag
from openpectus.protocol.models import (
    EntryDataType, PlotConfiguration, UodDefinition, TagDefinition, CommandDefinition
)

logger = logging.getLogger(__name__)


class UnitOperationDefinitionBase:
    """ Represets the Unit Operation Definition interface used by the OpenPectus engine.
    """
    def __init__(self,
                 instrument_name: str,
                 hwl: HardwareLayerBase,
                 author_name: str,
                 author_email: str,
                 filename: str,
                 location: str,
                 tags: TagCollection,
                 readings: ReadingCollection,
                 command_factories: dict[str, UodCommandBuilder],
                 command_descriptions: dict[str, UodCommandDescription],
                 overlapping_command_names_lists: list[list[str]],
                 plot_configuration: PlotConfiguration,
                 required_roles: set[str],
                 data_log_interval_seconds: float,
                 base_unit_provider: BaseUnitProvider
                 ) -> None:
        self.instrument = instrument_name
        self.hwl = hwl
        self.author_name = author_name
        self.author_email = author_email
        self.filename = filename
        self.location = location
        self.tags = tags
        self.system_tags: TagCollection | None = None
        self.readings = readings
        self.command_factories = command_factories
        self.command_descriptions = command_descriptions
        self.command_instances: dict[str, UodCommand] = {}
        self.overlapping_command_names_lists: list[list[str]] = overlapping_command_names_lists
        self.plot_configuration = plot_configuration
        self.required_roles = required_roles
        self.data_log_interval_seconds = data_log_interval_seconds
        self.base_unit_provider: BaseUnitProvider = base_unit_provider

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(instrument={self.instrument}, location={self.location}, hwl={self.hwl})'

    @property
    def options(self) -> dict[str, str]:
        return {
            'uod_name': self.instrument,
            'uod_author_name': self.author_name,
            'uod_author_email': self.author_email,
            'uod_filename': self.filename,
            'location': self.location
        }

    def build_commands(self):  # noqa C901
        """ Complete configuration of a validated uod. This builds the commands.
        """
        for r in self.readings:
            r.build_commands_list()

        # build command descriptions/examples documentation
        for cmd_name, cmd_builder in self.command_factories.items():
            valid_units: list[str] = []
            exclusive_options: list[str] = []
            additive_options: list[str] = []
            argument_type: Literal["float", "unknown", "none"] = "unknown"

            # Determine whether command is used for reading entry. If so, we can use the related tag's unit
            # as source of valid_units
            cmd_reading = next((r for r in self.readings if cmd_name in [c.name for c in r.commands]), None)
            if cmd_reading is not None:  # command is paired with this reading
                tag = cmd_reading.tag
                assert tag is not None
                if tag.unit is not None:
                    valid_units = get_compatible_unit_names(tag.unit)
                    if isinstance(tag.value, float):
                        argument_type = "float"

            # use the configured argument parser to determine argument and units
            regex_parser = RegexNamedArgumentParser.get_instance(cmd_builder.arg_parse_fn)
            if regex_parser is not None:
                named_groups = sorted(regex_parser.get_named_groups())
                if "number" in named_groups:  # always True for this regex
                    argument_type = "float"
                if "number_unit" in named_groups:
                    valid_units = regex_parser.get_units()

                    if cmd_reading is not None:
                        # propagate regex unit constraints back to reading's valid entry units
                        logger.debug(f"Applying regex unit constraints, {cmd_reading.valid_value_units} -> {valid_units} " +
                                     f"command {cmd_name}")
                        cmd_reading.valid_value_units = valid_units
                if "option" in named_groups:
                    exclusive_options = regex_parser.get_exclusive_options()
                    additive_options = regex_parser.get_additive_options()
            elif cmd_builder.arg_parse_fn is None:
                # no argument parser, this means no argument and units at all
                # argument_type = "none"
                valid_units = []

            desc = UodCommandDescription(name=cmd_name)
            desc.argument_type = argument_type
            desc.argument_valid_units = valid_units
            desc.argument_exclusive_options = exclusive_options
            desc.argument_additive_options = additive_options
            desc.set_docstring(cmd_builder.exec_fn.__doc__)

            self.command_descriptions[cmd_name] = desc

    def validate_configuration(self):  # noqa C901
        """ Validates these areas:
        - Each Reading matches a defined tag
        - Each Reading Command is verified
            - Must have an exec function with an appropriate signature
            - If the command uses a regular expression as parser function, it is verified that
              the exec function arguments match the regular expression.
        - Each process value is verified
            - Checks that entry process values have matching tag value type and
              process value entry_data_type.
        - Plot configuration
            - Process value names exist
            - Process values of a single axis share unit
        """
        fatal = False

        def log_fatal(msg: str):
            nonlocal fatal
            if not fatal:
                logger.fatal("An error occured while validating the Unit Operation Definition. " +
                             "Pectus Engine cannot start. " +
                             "Apply -v flag to validate UOD with more verbose error descriptions.")
            fatal = True
            logger.fatal(msg)

        if self.instrument is None or self.instrument.strip() == "":
            log_fatal("Instrument is not configured")
        if self.hwl is None:
            log_fatal("Hardware Layer is not configured")

        self.validate_read_registers()

        if self.system_tags is None:
            log_fatal("System tags have not been set")
        else:
            tags = self.tags.merge_with(self.system_tags)
            for r in self.readings:
                try:
                    r.match_with_tags(tags)
                except UodValidationError as vex:
                    log_fatal(str(vex))

                try:
                    r.resolve_entry_type()
                except ValueError as ex:
                    log_fatal(str(ex))

            # temporary check until we can support multiple readings per tag
            tags_with_reading = []
            for r in self.readings:
                if r.tag_name in tags_with_reading:
                    log_fatal(f"Tag '{r.tag_name}' is used by multiple readings. This is not currently supported.")
                else:
                    tags_with_reading.append(r.tag_name)
        try:
            self.validate_command_signatures()
        except UodValidationError as vex:
            log_fatal("Error in command definition. " + str(vex))

        try:
            self.validate_plot_configuration()
        except UodValidationError as vex:
            log_fatal("Error in plot configuration. " + str(vex))

        if fatal:
            sys.exit(1)

    def validate_command_signatures(self):  # noqa C901
        """ Validate the signatures of command exec functions"""
        import inspect

        for key, builder in self.command_factories.items():
            # builder.exec_fn is the function we are validating
            if builder.exec_fn is None:
                raise UodValidationError(f"Command '{key}' must have an execution function")

            signature = inspect.signature(builder.exec_fn)

            # 'cmd' is part of the framework and is always required
            if 'cmd' not in signature.parameters.keys():
                raise UodValidationError(f"Execution function for command '{key}' is missing a 'cmd' argument")

            regex_parser = RegexNamedArgumentParser.get_instance(builder.arg_parse_fn)
            if regex_parser is not None:
                # The command is using RegexNamedArgumentParser as argument parser. In this case we can validate the exec
                # function thoroughly by checking that its argument names match the named groups in the regular expression.

                # Given a regex with named groups ['foo', 'bar'], the expected signature is:
                #   def some_name(cmd: UodCommand, foo, bar) or
                #   def some_name(cmd: UodCommand, **kvargs)
                # However, it can also be a more intricate variation where default values are used
                # for arguments that may or may not be available depending on the regex...
                # Like this:
                #   some_name(cmd: UodCommand, foo, whynot=None, nevertheless=True, bar) or
                #   some_name(cmd: UodCommand, foo, whynot=None, **myargs)
                # which are also both valid.
                try:
                    named_groups = sorted(regex_parser.get_named_groups())
                except Exception as ex:
                    raise UodValidationError(
                        f"Error in command '{key}'. Failed to find named groups in regex: '{regex_parser.regex}'. Ex: {ex}")

                # Account for each signature parameter and each named group in the regex:
                parameter_unmatched = False
                named_groups_unmatched = set(named_groups)
                # A parameter has to either:
                for name, p in signature.parameters.items():
                    # 0) be named "cmd" which is part of the framework
                    if name == "cmd":
                        continue
                    # 1) be matched by a named group in the regex
                    if name in named_groups:
                        named_groups_unmatched.discard(name)
                        continue
                    # 2) have a default value
                    if p.default is not Parameter.empty:
                        named_groups_unmatched.discard(name)
                        continue
                    # 3) be a kvargs parameter
                    if p.kind == _ParameterKind.VAR_KEYWORD:
                        named_groups_unmatched.clear()
                        continue

                    parameter_unmatched = True

                if len(named_groups_unmatched) > 0 or parameter_unmatched:
                    # Parameter not accounted for. This means we can't provide a value for it when invoking exec_fn
                    # so we fail the validation
                    raise UodValidationError(f"""Command '{key}' has an error.
The parameters for the execution function do not match those defined in the regular expression
{regex_parser.regex} .
The expected execution function signature is:
    def some_name(cmd: UodCommand, {', '.join(named_groups)})""")

            elif builder.arg_parse_fn == defaultArgumentParser:
                # Default argument parser. Require a "value" parameter or a **kvargs parameter:
                param_count = len(signature.parameters)
                last_param_name = list(signature.parameters.keys())[param_count - 1]
                last_param = signature.parameters[last_param_name]
                if param_count == 1:
                    raise UodValidationError(f"""Command '{key}' has an error.
The execution function is using the default argument parser and requires
either a 'value' argument or a '**kvargs' argument""")
                if param_count == 2:
                    if last_param.kind != _ParameterKind.VAR_KEYWORD and last_param_name != "value":
                        raise UodValidationError(f"""Command '{key}' has an error.
The execution function is using the default argument parser and requires
either a 'value' argument or a '**kvargs' argument""")

            else:
                # Custom arg parsing. we can only verify that a **kvargs parameter is present
                # if only one positional arg is present.
                param_count = len(signature.parameters)
                last_param_name = list(signature.parameters.keys())[param_count - 1]
                last_param = signature.parameters[last_param_name]
                if param_count == 2 and last_param.kind != _ParameterKind.VAR_KEYWORD:
                    raise UodValidationError(f"""Command '{key}' has an error.
The execution function is missing named arguments or a '**kvargs' argument""")

    def validate_plot_configuration(self):
        """ Validate plot configuration """
        # Create complete list of tags
        assert self.system_tags
        tags = self.tags.merge_with(self.system_tags)
        # The following tags are added manually here because they are not
        # present in the self.system_tags list. They will be created by the engine
        # once it starts.
        tags.add(Tag(name=SystemTagName.MARK))
        tags.add(Tag(name=SystemTagName.BLOCK_TIME, unit="s"))
        tags.add(Tag(name=SystemTagName.SCOPE_TIME, unit="s"))

        # Check that process value names (tags) exist
        for sub_plot in self.plot_configuration.sub_plots:
            for plot_axis in sub_plot.axes:
                for process_value_name in plot_axis.process_value_names:
                    if not tags.has(process_value_name):
                        raise UodValidationError(f"Tag '{process_value_name}' referenced in sub_plot of plot configuration does not exist.")

        for process_value_name in self.plot_configuration.x_axis_process_value_names:
            if not tags.has(process_value_name):
                raise UodValidationError(f"Tag '{process_value_name}' referenced in x_axis_process_value_names of plot configuration does not exist.")

        for process_value_name in self.plot_configuration.process_value_names_to_annotate:
            if not tags.has(process_value_name):
                raise UodValidationError(f"Tag '{process_value_name}' referenced in process_value_names_to_annotate of plot configuration does not exist.")

        for color_region in self.plot_configuration.color_regions:
            if not tags.has(color_region.process_value_name):
                raise UodValidationError(f"Tag '{color_region.process_value_name}' referenced in color_regions of plot configuration does not exist.")

        # Check that units of process values of a single axis are homogenous
        # It might be annoying if it causes validation to fail so it only warns
        for sub_plot in self.plot_configuration.sub_plots:
            for plot_axis in sub_plot.axes:
                plot_axis_tags = [tags.get(process_value_name) for process_value_name in plot_axis.process_value_names]
                if not all(tag.unit == plot_axis_tags[0].unit for tag in plot_axis_tags):
                    tag_name_unit = ", ".join(f"{tag.name} [{tag.unit}]" for tag in plot_axis_tags)
                    logger.warning(f"""Process values sharing a plot axis should all have the same unit of measurement.
The process values of PlotAxis '{plot_axis.label}' have the following units: {tag_name_unit}.""")

    def validate_read_registers(self):
        """ Verify that all read registers have a matching tag. """
        read_registers = [r for r in self.hwl.registers.values() if RegisterDirection.Read in r.direction]
        for r in read_registers:
            if not self.tags.has(r.name):
                raise UodValidationError(
                    f"Register '{r.name}' has read direction but no matching tag")

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

    def generate_pcode_examples(self) -> list[Tuple[str, str]]:
        """ Generate example code as tuples of (description, example_pcode). """
        examples: list[Tuple[str, str]] = []
        for description in self.command_descriptions.values():
            # Generate example from command docstring
            docstring_pcode_example = description.get_docstring_pcode()
            if not docstring_pcode_example.strip():
                logger.warning(f"{description} has no pcode example")
            else:
                examples.append((str(description), docstring_pcode_example))

            # Generate examples from arg_parse_regex if RegexCategorical
            # or RegexNumber.
            for regex_example in description.generate_pcode_examples():
                examples.append((str(description), regex_example))

        # Generate examples from readings with command_options
        for reading in self.readings:
            if reading.command_options:
                for command_option in reading.command_options.values():
                    examples.append((str(reading), command_option))

        return examples

    def create_lsp_definition(self) -> UodDefinition:
        tags = []
        for t in self.tags:
            tags.append(TagDefinition(name=t.name, unit=t.unit))
        for t in self.system_tags or []:
            tags.append(TagDefinition(name=t.name, unit=t.unit))
        cmds: list[CommandDefinition] = []
        for name, builder in self.command_factories.items():
            parser = RegexNamedArgumentParser.get_instance(builder.arg_parse_fn)
            if parser is not None:
                cmds.append(CommandDefinition(
                    name=name,
                    validator=parser.serialize(),
                    docstring=self.command_descriptions.get(name, UodCommandDescription(name)).docstring
                ))
        for name, desc in self.command_descriptions.items():
            if name not in [c.name for c in cmds]:
                logger.warning(f"Adding command '{name}' which has no command factory/buidler")
                cmds.append(CommandDefinition(name=name, validator=None, docstring=desc.docstring))
        return UodDefinition(
            commands=cmds,
            system_commands=[],
            tags=tags
        )


INIT_FN = Callable[[], None]
""" Command initialization method. """

EXEC_FN = Callable[..., None]
""" Command execution function. Must take UodCommand and **kvargs as inputs. May be invoked multiple times.

NOTE: The type system does not seem to support describing the real signature (which should be something like
Callable[[UodCommand, Unpack[CommandArgs]], None]).

For this reason we validate the exec function dynamically during uod validation. This validation check must be
updated if EXEC_FN changes. It is implemented in UnitOperationDefinitionBase.verify_command_signatures().
"""

FINAL_FN = Callable[[], None]
""" Command finalization method. """

PARSE_FN = Callable[[str], CommandArgs | None]
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
        self._performance_warned = False
        self.cmd_state: dict[str, Any] = dict()

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
            raise ValueError(f"Command {self} has no execution function defined")

        if not isinstance(args, dict):
            raise TypeError(
                f"Invalid arguments provided to command {self}. Must be a dictionary, not {type(args).__name__}")

        super().execute(args)
        t0 = time.perf_counter()
        self.exec_fn(args)
        t1 = time.perf_counter()
        dt = t1-t0
        if not self._performance_warned and dt > 0.1:
            logger.warning(f"exec_fn {self.exec_fn} for {self} is slow. Execution time: {dt:0.1f} s. " +
                           "This warning is only issued once.")
            self._performance_warned = True

    def cancel(self):
        super().cancel()

    def finalize(self):
        super().finalize()

        if self.finalize_fn is not None:
            self.finalize_fn()

        self.context.dispose_command(self)

    def parse_args(self, args: str) -> CommandArgs | None:
        """ Parse argument input to concrete values. Return None to indicate invalid arguments. """
        if self.arg_parse_fn is None:
            return {}
        else:
            return self.arg_parse_fn(args)


class UodCommandBuilder:
    """ Used to builds command specifications and as factory to instantiate commands from the specifications. """
    def __init__(self) -> None:
        self.name = ""
        self.init_fn: Callable[[UodCommand], None] | None = None
        self.exec_fn: Callable[..., None] | None = None
        self.finalize_fn: Callable[[UodCommand], None] | None = None
        self.arg_parse_fn: Callable[[str], CommandArgs | None] | None = None

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(name={self.name})'

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

    def with_arg_parse_fn(self, arg_parse_fn: Callable[[str], CommandArgs | None]) -> UodCommandBuilder:
        """ Define an argument parser function. Optional.

        The function is given the command argument string from the method and should parse that
        and return the result as a dictionary. The result is passed to the excution function automatically.

        If not arg_parse function is defined, no arguments are provided to the execute function.

        Example::

          def my_command_parse_args(args: str) -> dict[str, Any] | None:
            # parse the argument string and return the values as a dictionary.
            return None # if args are invalid.
        """
        self.arg_parse_fn = arg_parse_fn
        return self

    def build(self, uod: UnitOperationDefinitionBase) -> UodCommand:  # noqa C901
        """ Construct the command """

        def arg_parse(args: str) -> CommandArgs | None:
            if self.arg_parse_fn is None:
                return {}
            return self.arg_parse_fn(args)

        def initialize() -> None:
            if self.init_fn is not None:
                return self.init_fn(c)

        def execute(args: CommandArgs) -> None:
            if self.exec_fn is not None:
                try:
                    return self.exec_fn(c, **args)
                except TypeError as te:
                    raise Exception(f"Execution function type error in uod command '{self.name}' with **args '{args}'")\
                        from te

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


class UodBuilder:
    """ Provides a builder api to define a Unit Operation Definition """
    def __init__(self) -> None:
        self.instrument: str = ""
        self.hwl: HardwareLayerBase | None = None
        self.tags = TagCollection()
        self.command_factories: dict[str, UodCommandBuilder] = {}
        self.command_descriptions: dict[str, UodCommandDescription] = {}
        self.overlapping_command_names_lists: list[list[str]] = []
        self.readings = ReadingCollection()
        self.author_name: str = ""
        self.author_email: str = ""
        self.filename: str = ""
        self.location: str = ""
        self.plot_configuration: PlotConfiguration = PlotConfiguration.empty()
        self.required_roles: set[str] = set()
        self.data_log_interval_seconds = 5
        self.base_unit_provider: BaseUnitProvider = BaseUnitProvider()
        self.base_unit_provider.set("s", SystemTagName.SCOPE_TIME, SystemTagName.BLOCK_TIME)
        self.base_unit_provider.set("min", SystemTagName.SCOPE_TIME, SystemTagName.BLOCK_TIME)
        self.base_unit_provider.set("h", SystemTagName.SCOPE_TIME, SystemTagName.BLOCK_TIME)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'

    def get_logger(self):
        return logging.getLogger(f'{__name__}.user_uod')

    def validate(self):
        if len(self.instrument.strip()) == 0:
            raise ValueError("Instrument name must be set")

        if len(self.author_name.strip()) == 0 or len(self.author_email.strip()) == 0:
            raise ValueError("Author must be set")

        if len(self.filename.strip()) == 0:
            raise ValueError("Filename must be set")

        if self.hwl is None:
            raise ValueError("HardwareLayer must be set")

        return

    def with_instrument(self, instrument_name: str) -> UodBuilder:
        if len(instrument_name.strip()) == 0:
            raise ValueError("Instrument name cannot be empty")

        self.instrument = instrument_name
        return self

    def with_hardware_none(self) -> UodBuilder:
        """ Use no hardware. Mainly used for testing. """
        return self.with_hardware(NullHardware())

    def with_hardware_opcua(self, host: str) -> UodBuilder:
        """ Use OPCUA hardware """
        from openpectus.engine.opcua_hardware import OPCUA_Hardware
        hwl = OPCUA_Hardware(host)
        return self.with_hardware(hwl)

    def with_hardware_labjack(self, serial_number: str | None = None) -> UodBuilder:
        """ Use LabJack hardware """
        from openpectus.engine.labjack_hardware import Labjack_Hardware
        hwl = Labjack_Hardware(serial_number)
        return self.with_hardware(hwl)

    def with_hardware(self, hwl: HardwareLayerBase) -> UodBuilder:
        self.hwl = hwl
        return self

    def with_author(self, name: str, email: str) -> UodBuilder:
        self.author_name = name
        self.author_email = email
        return self

    def with_filename(self, filename: str) -> UodBuilder:
        self.filename = filename
        return self

    def with_location(self, location: str) -> UodBuilder:
        self.location = location
        return self

    def with_hardware_register(self, name: str, direction: RegisterDirection = RegisterDirection.Read, **options)\
            -> UodBuilder:
        """ Define a hardware register.

        Parameters:
            name (str):
                The register name. Used to match the register to a tag.
            direction:
                Specify whether the register is read, written or both
            options:
                Specify additional named options. Specific hardwares may require certain options,
                e.g. the opcua hardware requires a 'path' option.

                Two special options are callbacks named 'to_tag' and 'from_tag'. If specified, these callbacks
                convert between hardware values and tag values.
        """
        register = Register(name, direction, **options)
        if self.hwl is None:
            raise ValueError("HardwareLayber must be defined before defining a register")
        if register.name is None or register.name == "":
            raise ValueError("Register name must be non-empty")
        if register.name in self.hwl.registers.keys():
            raise ValueError(f"Register {register.name} is already defined")
        self.hwl.registers[register.name] = register
        return self

    def with_tag(self, tag: Tag) -> UodBuilder:
        # TODO Replace Tag as input with specific named variations
        # eg. with_tag_choice, with_tag_reading, with_tag
        return self._with_tag(tag)

    def _with_tag(self, tag: Tag) -> UodBuilder:
        if self.tags.has(tag.name):
            raise ValueError(f"Duplicate tag name: {tag.name}")
        self.tags.add(tag)
        return self

    def with_accumulated_volume(self, totalizer_tag_name: str) -> UodBuilder:
        if not self.tags.has(totalizer_tag_name):
            raise ValueError(f"The specified totalizer tag name '{totalizer_tag_name}' was not found")
        totalizer = self.tags[totalizer_tag_name]
        volume_units = get_volume_units()
        if totalizer.unit not in volume_units:
            raise ValueError(f"The totalizer tag '{totalizer_tag_name}' must have a volume unit")
        self._with_tag(AccumulatorTag(name=SystemTagName.ACCUMULATED_VOLUME, totalizer=totalizer))
        self._with_tag(AccumulatorBlockTag(name=SystemTagName.BLOCK_VOLUME, totalizer=totalizer))
        self.with_base_unit_provider(volume_units, SystemTagName.ACCUMULATED_VOLUME, SystemTagName.BLOCK_VOLUME)
        return self

    def with_accumulated_cv(self, cv_tag_name: str, totalizer_tag_name: str) -> UodBuilder:
        if not self.tags.has(cv_tag_name):
            raise ValueError(f"The specified column volume tag name '{cv_tag_name}' was not found")
        if not self.tags.has(totalizer_tag_name):
            raise ValueError(f"The specified totalizer tag name '{totalizer_tag_name}' was not found")
        cv = self.tags[cv_tag_name]
        totalizer = self.tags[totalizer_tag_name]
        self._with_tag(AccumulatedColumnVolume(SystemTagName.ACCUMULATED_CV, cv, totalizer))
        acc_cv = self.tags[SystemTagName.ACCUMULATED_CV]
        self._with_tag(AccumulatorBlockTag(SystemTagName.BLOCK_CV, acc_cv))
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

    def with_command(
            self,
            name: str,
            exec_fn: Callable[..., None],
            init_fn: Callable[[UodCommand], None] | None = None,
            finalize_fn: Callable[[UodCommand], None] | None = None,
            arg_parse_fn: Callable[[str], CommandArgs | None] | Literal["default"] | None = "default"
            ) -> UodBuilder:
        """ Define a custom unit operation command that can be executed from pcode.

        Parameters:
            name (str):
                The command name. Used in pcode to refer to the command
            exec_fn:
                The function to execute when the command is run. The function will be called
                once in each engine tick until it is completed. To signal completion, use
                `cmd.set_complete()`.
            init_fn, optional:
                An optional initialization function that is invoked once before the command runs
            finalize_fn, optional:
                An optional function that is run once when the command is completed
            arg_parse_fn, optional:
                An optional function that is used to parse the command argument in pcode to
                **kvargs that are given as named arguments to the exec function.
                A number of cases are possible:
                The default parsing function (`arg_parse_fn="default"`) passes the argument from the pcode line
                verbatim to the exec function using the argument name 'value'.
                If no parse function is set (`arg_parse_fn=None`), no arguments are passed to the exec function.
                To use a regular expression as argument parser, use the method `with_command_regex_arguments()`
                instead.
        """
        cb = UodCommandBuilder().with_name(name).with_exec_fn(exec_fn)
        if init_fn is not None:
            cb.with_init_fn(init_fn)
        if finalize_fn is not None:
            cb.with_finalize_fn(finalize_fn)
        if arg_parse_fn == "default":
            cb.with_arg_parse_fn(defaultArgumentParser)
        elif arg_parse_fn is not None:
            cb.with_arg_parse_fn(arg_parse_fn)
        elif arg_parse_fn is None:
            cb.with_arg_parse_fn(RegexNamedArgumentParser(ArgSpec.NoArgsInstance.regex).parse)
        if cb.name in self.command_factories.keys():
            raise ValueError(f"Duplicate command name: {cb.name}")
        self.command_factories[cb.name] = cb
        return self

    def with_command_regex_arguments(
            self,
            name: str,
            arg_parse_regex: str,
            exec_fn: Callable[..., None],
            init_fn: Callable[[UodCommand], None] | None = None,
            finalize_fn: Callable[[UodCommand], None] | None = None,
            ) -> UodBuilder:
        """ Define a custom unit operation command with a regular expression as argument parser.

        Parameters:
            name (str):
                The command name. Used in pcode to refer to the command
            arg_parse_regex (str):
                The regular expression to use for parsing. The expression must use named groups
                to specify the argument names and values.
            exec_fn:
                The function to execute when the command is run. The function will be called
                once in each engine tick until it is completed. To signal completion, use
                `cmd.set_complete()`.
            init_fn, optional:
                An optional initialization function that is invoked once before the command runs
            finalize_fn, optional:
                An optional function that is run once when the command is completed
        """
        cb = UodCommandBuilder().with_name(name).with_exec_fn(exec_fn).with_arg_parse_fn(
            RegexNamedArgumentParser(arg_parse_regex).parse)
        if init_fn is not None:
            cb.with_init_fn(init_fn)
        if finalize_fn is not None:
            cb.with_finalize_fn(finalize_fn)
        self.command_factories[cb.name] = cb
        return self

    def with_command_overlap(self, command_names: list[str]) -> UodBuilder:
        """ Specify that the given commands names overlap, i.e. at most one can run at a time. """
        if len(command_names) < 2:
            raise ValueError("To define command overlap, at least two command names are required")
        self.overlapping_command_names_lists.append(command_names)
        return self

    def with_process_value(self, tag_name: str) -> UodBuilder:
        """ Add process value that displays the given tag in the UI. """
        reading = Reading(tag_name=tag_name)
        return self._with_process_value(reading)

    def with_process_value_entry(
            self,
            tag_name: str,
            entry_data_type: EntryDataType = "auto",
            execute_command_name: str | None = None
            ) -> UodBuilder:
        """ Add process value for the given tag and enable setting its value by typing in a value in the UI.

        Parameters:
            tag_name: str
                The tag to display
            entry_data_type: "str" | "int" | "float" | "auto", optional, default="auto"
                The data type to display and validate in the UI. Default is "auto" which uses the type of the tag's
                value. The "auto" value requires that the tag has a default value with the correct type.
            execute_command_name: str: optional
                The command to execute to 'set the process value'. In principle, this can be any pcode command that takes a
                single argument as given by the user. However, the intension is that the command 'sets the process value',
                probably by writing the value to the register backing the tag.

                If not specified, it defaults to the tag name, assuming that there is a command with the same name as
                the tag that takes a single argument.
        """
        reading = ReadingWithEntry(
            tag_name=tag_name,
            entry_data_type=entry_data_type,
            execute_command_name=execute_command_name)
        return self._with_process_value(reading)

    def with_process_value_choice(self, tag_name: str, command_options: dict[str, str]) -> UodBuilder:
        """ Add process value for the given tag and enable command choices.

        Parameters:
            tag_name: str
                The tag to display. The tag's choices are also used as commands, unless
                command_options are specified.
            command_options: optional
                Dictionary that maps command names to their pcode implementation.
        """
        if not self.tags.has(tag_name):
            raise ValueError(f"Cannot add process value choice for tag name {tag_name}. The tag name was not found")
        if not command_options:
            raise ValueError(f"Cannot add process value choice without any command_options. Use 'with_process_value' instead.")
        if command_options is not None:
            reading = ReadingWithChoice(tag_name, command_options)
        return self._with_process_value(reading)

    def _with_process_value(self, reading: Reading) -> UodBuilder:
        self.readings.add(reading)
        return self

    def with_plot_configuration(self, plot_configuration: PlotConfiguration):
        self.plot_configuration = plot_configuration
        return self

    def with_required_roles(self, required_roles: set[str]) -> UodBuilder:
        self.required_roles = required_roles
        return self

    def with_data_log_interval_seconds(self, data_log_interval_seconds: float) -> UodBuilder:
        self.data_log_interval_seconds = data_log_interval_seconds
        return self

    def with_measurement_unit(self,
                              unit: str,
                              unit_relation: None | str = None,
                              quantity_relation: None | dict[str, str] = None,
                              quantity: None | str = None) -> UodBuilder:
        add_unit(unit=unit, unit_relation=unit_relation, quantity_relation=quantity_relation, quantity=quantity)
        return self

    def build(self) -> UnitOperationDefinitionBase:
        self.validate()

        uod = UnitOperationDefinitionBase(
            self.instrument,
            self.hwl,  # type: ignore
            self.author_name,
            self.author_email,
            self.filename,
            self.location,
            self.tags,
            self.readings,
            self.command_factories,
            self.command_descriptions,
            self.overlapping_command_names_lists,
            self.plot_configuration,
            self.required_roles,
            self.data_log_interval_seconds,
            self.base_unit_provider
        )

        return uod


def defaultArgumentParser(args: str) -> CommandArgs:
    """ The default command argument parser.

    Passes the string argument verbatim to the command exec function as a single argument
    named `value`.

    E.g. for the command pcode `MyCommand: 87`, `value` will have the value '87'.

    When using this argument parser, the exec function looks like this::

      def exec(cmd: UodCommand, value: str):
        # implementation here
        cmd.set_complete()
    """
    return {'value': args}


def unescape(re_escaped_string: str) -> str:
    """
    re.escape is used to escape options supplied to
    RegexCategorical. This function can reverses operation.

    assert unescape(re.escape('A B')) == 'A B'
    assert unescape(re.escape('A/B')) == 'A/B'
    """
    # Source: https://stackoverflow.com/questions/43662474/reversing-pythons-re-escape
    return re.sub(r'\\(.)', r'\1', re_escaped_string)


class RegexNamedArgumentParser:
    def __init__(self, regex: str, name: str | None = None) -> None:
        self.regex = regex
        self.name = name

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(named_groups={self.get_named_groups()})'

    def parse(self, args: str) -> dict[str, Any] | None:
        match = re.search(self.regex, args)
        if not match:
            return None
        return match.groupdict()

    def validate(self, args: str) -> bool:
        match = re.search(self.regex, args)
        return match is not None

    def get_named_groups(self) -> list[str]:
        # ex: r"(?P<value>[0-9]+[.][0-9]*?|[.][0-9]+|[0-9]+) ?(?P<unit>m2)"
        # ex2: ' ?(?P<number_unit>kg)'
        # eg3: '^\\s*(?P<number>-?[0-9]+[.][0-9]*?|-?[.][0-9]+|-?[0-9]+)\\s* ?(?P<number_unit>kg|g)\\s*$'
        result = []
        p = re.compile(r"\<(?P<name>([a-zA-Z]|_)+)\>")
        for match in p.finditer(self.regex):
            result.append(match.group("name"))
        return result

    def get_units(self) -> list[str]:
        if "number_unit" not in self.get_named_groups():
            return []
        start = self.regex.index("<number_unit>") + len("<number_unit>")
        end = self.regex.index(")", start)
        result = unescape(self.regex[start: end]).split("|")
        return result

    def get_exclusive_options(self) -> list[str]:
        if "option" not in self.get_named_groups():
            return []
        start = self.regex.index("<option>") + len("<option>(")
        end = self.regex.index("|(")
        result = unescape(self.regex[start: end]).split("|")
        if "" in result:
            result.remove("")
        return result

    def get_additive_options(self) -> list[str]:
        if "option" not in self.get_named_groups():
            return []
        start = self.regex.index("|(") + len("|(")
        end = self.regex.index(r"|\+)+)(?<!\+))\s*")
        result = unescape(self.regex[start: end]).split("|")
        if "" in result:
            result.remove("")
        return result

    @staticmethod
    def get_instance(parse_func) -> RegexNamedArgumentParser | None:
        """ Gets the RegexNamedArgumentParser associated with parse_func or None
        if parse_func is not a regex validator
        """
        try:
            instance = getattr(parse_func, "__self__", None)
            if instance is not None and isinstance(instance, RegexNamedArgumentParser):
                return instance
        except Exception:
            return None

    def serialize(self) -> str:
        return f"RNAP-v1-{self.regex}"

    @staticmethod
    def deserialize(serialized: str, name: str | None = None) -> RegexNamedArgumentParser | None:
        if serialized.startswith("RNAP-v1-"):
            return RegexNamedArgumentParser(serialized[8:], name)
        return None
