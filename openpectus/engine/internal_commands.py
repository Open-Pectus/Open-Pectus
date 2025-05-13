from __future__ import annotations
import importlib
import logging
from typing import Any, Callable, Generator
from openpectus.engine.commands import EngineCommand
from openpectus.engine.models import EngineCommandEnum
from openpectus.lang.exec.argument_specification import ArgSpec
from openpectus.lang.exec.commands import InterpreterCommandEnum
import openpectus.lang.exec.regex as regex
from openpectus.lang.exec.uod import RegexNamedArgumentParser
from openpectus.protocol.models import CommandDefinition
from openpectus.aggregator.command_examples import examples


logger = logging.getLogger(__name__)


class InternalCommandsRegistry:
    def __init__(self, engine):
        self.engine = engine
        self._command_map: dict[str, Callable[[], InternalEngineCommand]] = {}
        self._command_spec: dict[str, ArgSpec] = {
            InterpreterCommandEnum.BASE: ArgSpec.Regex(regex.REGEX_BASE_ARG),
            InterpreterCommandEnum.INCREMENT_RUN_COUNTER: ArgSpec.NoArgs(),
            InterpreterCommandEnum.RUN_COUNTER: ArgSpec.Regex(regex.REGEX_INT),
            InterpreterCommandEnum.WAIT: ArgSpec.Regex(regex.REGEX_DURATION),
            "End block": ArgSpec.NoArgs(),
            "End blocks": ArgSpec.NoArgs(),
            "Stop": ArgSpec.NoArgs(),
            "Restart": ArgSpec.NoArgs(),
        }
        # system cmds that are implemented in interpreter and have no command class
        others = [
            "Watch",
            "Alarm",
            "Block",
            "Mark",
            "Macro",
            "Call macro",
            "Batch",
        ]
        for other_cmd in others:
            self._command_spec[other_cmd] = ArgSpec.NoCheck()

        self._command_instances: dict[str, InternalEngineCommand] = {}

    def __str__(self) -> str:
        _command_instances = [str(command_instance) for command_instance in self._command_instances]
        return f'{self.__class__.__name__}(engine={self.engine}, _command_instances={_command_instances})'

    def __enter__(self):
        self._register_commands(self.engine)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        logger.debug("Disposing registry")
        self._command_map.clear()
        for cmd in self._command_instances.values():
            try:
                cmd.cancel()
            except Exception as ex:
                logger.warning(f"Error during cancel/finalize while disposing command: {cmd.name}: {str(ex)}")
        self._finalize_instances()

    def _register_commands(self, engine):
        if len(self._command_map) > 0:
            raise ValueError("Register may only run once per engine lifetime. " +
                             "Engine was probably not cleaned up with .cleanup()")

        def register(command_name: str, cls):
            self._command_map[command_name] = lambda : cls(engine, self)
            logger.debug(f"Registered command '{command_name}' with factory '{str(cls)}'")

        # use dynamic import for introspection to avoid static import cycle error
        command_impl_module = importlib.import_module("openpectus.engine.internal_commands_impl")

        # use introspection to auto-register classes in command_impl_module
        registered_classes = []
        for command_name in EngineCommandEnum:
            for cls_name in dir(command_impl_module):
                if cls_name == f"{command_name}EngineCommand":
                    cls = getattr(command_impl_module, cls_name, None)
                    if cls is not None:
                        # register constructor via a function here to obtain the right closure
                        register(command_name, cls)
                        registered_classes.append(cls_name)
                        # register the argument specification
                        self._command_spec[command_name] = cls.argument_validation_spec
        logger.debug(f"Registered internal engine commands: {', '.join(registered_classes)}")

    def get_running_internal_command(self) -> InternalEngineCommand | None:
        if len(self._command_instances) > 0:
            for cmd in self._command_instances.values():
                return cmd

    def create_internal_command(self, command_name: str) -> InternalEngineCommand:
        if command_name not in self._command_map.keys():
            raise ValueError(f"Command name '{command_name}' is not a known internal engine command")
        if command_name in self._command_instances.keys():
            raise ValueError(f"There is already a command instance for command name '{command_name}'")

        instance = self._command_map[command_name]()
        self._command_instances[command_name] = instance
        logger.debug(f"Created instance {type(instance).__name__} for command '{command_name}'")
        return instance

    def dispose_command(self, command_name):
        if command_name in self._command_instances.keys():
            del self._command_instances[command_name]
        else:
            logger.warning(f"No command '{command_name}' found to dispose. " +
                           f"Actual commands: {str(list(self._command_instances.keys()))}")

    def _finalize_instances(self):
        """ Finalize and dispose all command instances. """
        instances = list(self._command_instances.values())
        for cmd in instances:
            cmd.finalize()

    def get_command_definitions(self) -> list[CommandDefinition]:
        """ Create and return the list of LSP command definitions that specify how command arguments
        should be parsed. """
        if len(self._command_map) == 0:
            raise ValueError("Command map not initialized")
        command_definitions = []
        for example in examples:
            name = example.name
            spec = self._command_spec.get(name)
            if isinstance(spec, ArgSpec):
                parser = RegexNamedArgumentParser(regex=spec.regex)
                command_definitions.append(CommandDefinition(name=name, validator=parser.serialize(), docstring=example.example))
            else:
                command_definitions.append(CommandDefinition(name=name, validator=None, docstring=example.example))
        return command_definitions

class InternalEngineCommand(EngineCommand):
    """ Base class for internal engine commands.

    Adds support for long-running commands via a _run() generator method. The tick() base class method
    implements the state management of these commands.
    """
    argument_validation_spec: ArgSpec = ArgSpec.NoCheck()

    def __init__(self, name: str, registry: InternalCommandsRegistry) -> None:
        super().__init__(name)
        self._registry = registry
        self._failed = False
        self.has_run = False
        self.run_result: Generator[None, None, None] | None = None
        self.kvargs: dict[str, Any] = {}

    def validate_arguments(self, arguments: str):
        """ Validates the runtime argument string provided to the command against the command's ArgSpec.

        Raises ValueError if the argument is not valid. Otherwise, sets kvargs to the regex groups of the ArgSpec.

        Override for custom (non-regex) argument handling. """
        if self.argument_validation_spec == ArgSpec.NoCheckInstance:
            return {}
        groupdict = self.argument_validation_spec.validate_w_groups(argument=arguments)
        if groupdict is None:
            raise ValueError(f"Argument '{arguments}' for command '{self.name}' is not valid")
        self.kvargs = groupdict

    def _run(self) -> Generator[None, None, None] | None:
        """ Override to implement the command using a generator style where each yield pauses execution until the next tick
        (i.e. call to execute()). """
        # TODO consider mechanism to save/load command state so commands have a supported way to resume if engine crashes
        raise NotImplementedError()

    def fail(self):
        self._failed = True

    def has_failed(self):
        return self._failed

    def set_complete(self):
        super().set_complete()

    def finalize(self):
        super().finalize()
        self._registry.dispose_command(self.name)

    def tick(self) -> None:
        if self.is_finalized() or self.is_cancelled() or self.has_failed():
            # command should already be disposed and not end up here
            logger.warning(f"Did not expect internal command '{self.name}' here in its end state")
        elif self.is_execution_complete():
            self.finalize()
        else:
            if not self.has_run:
                try:
                    self.run_result = self._run()
                    self.has_run = True
                except Exception:
                    self.fail()
                    self._registry.dispose_command(self.name)
                    logger.error(f"Command '{self.name}' failed", exc_info=True)
                    return

            if self.run_result is None:
                self.set_complete()
                self.finalize()
            else:
                try:
                    next(self.run_result)
                except StopIteration:
                    self.set_complete()
                    self.finalize()
                except Exception:
                    self.fail()
                    self.finalize()
                    logger.error(f"Command '{self.name}' failed", exc_info=True)
