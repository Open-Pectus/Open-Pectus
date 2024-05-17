from __future__ import annotations

from inspect import _ParameterKind, Parameter
import logging
import re
from typing import Any, Callable, Literal

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

    def __str__(self) -> str:
        return f"UnitOperationDefinition({self.instrument=},{self.location=},hwl={str(self.hwl)})"

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

                # now that tag validation was completed, the command list can be built
                r.build_commands_list()
        try:
            self.validate_command_signatures()
        except UodValidationError as vex:
            log_fatal("Error in command definition. " + str(vex))

        if fatal:
            exit(1)

    def validate_command_signatures(self):
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
                # function thoroughly by checking that its parameters matches the named groups in the regular expression.

                # Given a regex with named groups ['foo', 'bar'], the expected signature is:
                #   def some_name(cmd: UodCommand, foo, bar) or
                #   def some_name(cmd: UodCommand, **kvargs)
                # However, it can also be a more intricate variation where default values are used
                # for arguments that may or may not be available depending on the regex...
                # Like this:
                #   some_name(cmd: UodCommand, foo, whynot=None, nevertheless=True, bar) or
                #   some_name(cmd: UodCommand, foo, whynot=None, **myargs)
                # which are also  both valid.
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
                    # Parameter not accounted for. This means we cant provide a value for it when invoking exec_fn
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

    def parse_args(self, args: str) -> CommandArgs | None:
        """ Parse argument input to concrete values. Return None to indicate invalid arguments. """
        if self.arg_parse_fn is None:
            return {}
        else:
            return self.arg_parse_fn(args)


class UodCommandBuilder():
    """ Used to builds command specifications and as factory to instantiate commands from the specifications. """
    def __init__(self) -> None:
        self.name = ""
        self.init_fn: Callable[[UodCommand], None] | None = None
        self.exec_fn: Callable[..., None] | None = None
        self.finalize_fn: Callable[[UodCommand], None] | None = None
        self.arg_parse_fn: Callable[[str], CommandArgs | None] | None = None

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

    def build(self, uod: UnitOperationDefinitionBase) -> UodCommand:
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
                The default parsing function passes the pcode argument verbatim with the argument
                name 'value'. If no parse function is set, no arguments are passed to exec.
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
        if cb.name in self.commands.keys():
            raise ValueError(f"Duplicate command name: {cb.name}")
        self.commands[cb.name] = cb
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


class RegexNamedArgumentParser():
    def __init__(self, regex: str) -> None:
        self.regex = regex

    def parse(self, args: str) -> dict[str, Any] | None:
        match = re.search(self.regex, args)
        if not match:
            return None
        return match.groupdict()

    def get_named_groups(self) -> list[str]:
        # ex: r"(?P<value>[0-9]+[.][0-9]*?|[.][0-9]+|[0-9]+) ?(?P<unit>m2)"
        # ex2: ' ?(?P<number_unit>kg)'
        result = []
        p = re.compile(r"\<(?P<name>([a-zA-Z]|_)+)\>")
        for match in p.finditer(self.regex):
            result.append(match.group("name"))
        return result

    @staticmethod
    def get_instance(parse_func) -> RegexNamedArgumentParser | None:
        try:
            instance = getattr(parse_func, "__self__", None)
            if instance is not None and isinstance(instance, RegexNamedArgumentParser):
                return instance
        except Exception:
            return None


# Common regular expressions for use with RegexNamedArgumentParser

def RegexNumberWithUnit(units: list[str] | None, non_negative: bool = False) -> str:
    """ Parses a number with a unit to arguments `number` and `number_unit`. """
    sign_part = "" if non_negative else "-?"
    unit_part = " ?(?P<number_unit>" + "|".join(re.escape(unit).replace(r"/", r"\/") for unit in units) + ")" \
        if units else ""
    return rf"^\s*(?P<number>{sign_part}[0-9]+[.][0-9]*?|{sign_part}[.][0-9]+|{sign_part}[0-9]+)\s*{unit_part}\s*$"


def RegexCategorical(exclusive_options: list[str] | None = None, additive_options: list[str] | None = None) -> str:
    """ Parses categorical text into an argument named `option`.

    Examples - exclusive::

        regex = RegexCategorical(exclusive_options=["Open", "Closed"])

        self.assertEqual(re.search(regex, "Closed").groupdict(), dict(option="Closed"))

        self.assertEqual(re.search(regex, "VA01"), None)

        self.assertEqual(re.search(regex, "Open").groupdict(), dict(option="Open"))

        self.assertEqual(re.search(regex, "Open+Closed"), None)


    Examples - exclusive and additive::

        regex = RegexCategorical(exclusive_options=['Closed'], additive_options=['VA01', 'VA02', 'VA03'])

        self.assertEqual(re.search(regex, "Closed").groupdict(), dict(option="Closed"))

        self.assertEqual(re.search(regex, "Closed+VA01"), None)

        self.assertEqual(re.search(regex, "VA01").groupdict(), dict(option="VA01"))

        self.assertEqual(re.search(regex, "VA01+VA02").groupdict(), dict(option="VA01+VA02"))

        self.assertEqual(re.search(regex, "Open+Closed"), None)
    """
    if exclusive_options is None and additive_options is None:
        raise TypeError("RegexCategorical() missing argument 'exclusive_options' or 'additive_options'.")
    exclusive_option_part = "|".join(re.escape(option) for option in exclusive_options) if exclusive_options else ""
    additive_option_part = "|".join(re.escape(option) for option in additive_options) if additive_options else ""
    return rf"^(?P<option>({exclusive_option_part}|({additive_option_part}|\+)+))\s*$"

def RegexText(allow_empty: bool = False):
    """ Parses text into an argument named `text`."""
    allow_empty_part = "*" if allow_empty else "+"
    return rf"^(?P<text>.{allow_empty_part})$"
