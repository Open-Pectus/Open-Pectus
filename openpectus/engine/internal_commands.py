from __future__ import annotations
import importlib
import logging
from typing import Any, Callable, Generator
from openpectus.engine.commands import EngineCommand
from openpectus.engine.models import EngineCommandEnum


logger = logging.getLogger(__name__)


_command_map: dict[str, Callable[[], InternalEngineCommand]] = {}
_command_instances: dict[str, InternalEngineCommand] = {}


def register_commands(engine):
    if len(_command_map) > 0:
        raise ValueError("Register may only run once per engine lifetime. " +
                         "Engine was probably not cleaned up with .cleanup()")

    def register(command_name: str, cls):
        _command_map[command_name] = lambda : cls(engine)
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

def get_running_internal_command() -> InternalEngineCommand | None:
    if len(_command_instances) > 0:
        for cmd in _command_instances.values():
            return cmd

def create_internal_command(command_name: str) -> InternalEngineCommand:
    if command_name not in _command_map.keys():
        raise ValueError(f"Command name '{command_name}' is not a known internal engine command")
    if command_name in _command_instances.keys():
        raise ValueError(f"There is already a command instance for command name '{command_name}'")

    instance = _command_map[command_name]()
    _command_instances[command_name] = instance
    logger.debug(f"Created instance {type(instance).__name__} for command '{command_name}'")
    return instance

def dispose_command(command_name):
    if command_name in _command_instances.keys():
        del _command_instances[command_name]
    else:
        logger.warning(f"No command '{command_name}' found to dispose. Actual commands: {str(_command_instances.keys())}")

def dispose_command_map():
    _command_map.clear()
    _command_instances.clear()


class InternalEngineCommand(EngineCommand):
    def __init__(self, name: str) -> None:
        super().__init__(name)
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
        # we don't need finalize for internal commands so we
        # just automatically progress to its end state.
        # This avoids wasting a tick for these commands and makes testing simpler
        self.finalize()

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
                    dispose_command(self.name)
                    logger.error(f"Command '{self.name}' failed", exc_info=True)
                    return

            if self.run_result is None:
                self.set_complete()
                dispose_command(self.name)
            else:
                try:
                    next(self.run_result)
                except StopIteration:
                    self.set_complete()
                    dispose_command(self.name)
                except Exception:
                    self.fail()
                    logger.error(f"Command '{self.name}' failed", exc_info=True)
                    dispose_command(self.name)
