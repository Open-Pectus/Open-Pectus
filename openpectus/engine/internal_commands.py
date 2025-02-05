from __future__ import annotations
import importlib
import logging
from typing import Any, Callable, Generator
from openpectus.engine.commands import EngineCommand
from openpectus.engine.models import EngineCommandEnum


logger = logging.getLogger(__name__)


class InternalCommandsRegistry:
    def __init__(self, engine):
        self.engine = engine
        self._command_map: dict[str, Callable[[], InternalEngineCommand]] = {}
        self._command_instances: dict[str, InternalEngineCommand] = {}

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
                        # register via a function here to obtain the right closure
                        register(command_name, cls)
                        registered_classes.append(cls_name)
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


class InternalEngineCommand(EngineCommand):
    """ Base class for internal engine commands.

    Adds support for long-running commands via a _run() generator method. The tick() base class method
    implements the state management of these commands.
    """
    def __init__(self, name: str, registry: InternalCommandsRegistry) -> None:
        super().__init__(name)
        self._registry = registry
        self._failed = False
        self.has_run = False
        self.run_result: Generator[None, None, None] | None = None
        self.kvargs: dict[str, Any] = {}

    def _run(self) -> Generator[None, None, None] | None:
        """ Override to implement the command using a generator style
        where each yield pauses execution until the next tick (i.e. call to execute()). """
        raise NotImplementedError()

    def init_args(self, kvargs: dict[str, Any]):
        self.kvargs = kvargs

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
