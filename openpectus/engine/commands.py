from __future__ import annotations
from typing import Any, Generic, TypeVar


CommandArgs = dict[str, Any]
""" Command arguments"""


class EngineCommand():
    """ Interface for commands runnable by engine. """
    def __init__(self, name) -> None:
        self.name: str = name
        self._cancelled: bool = False
        self._initialized: bool = False
        self._exec_started: bool = False
        self._exec_iterations: int = -1
        self._exec_complete: bool = False
        self._progress: bool | float = False
        self._finalized: bool = False

    def initialize(self):
        self._initialized = True

    def is_initialized(self) -> bool:
        return self._initialized

    def execute(self, args: CommandArgs) -> None:
        self._exec_started = True
        self._exec_iterations += 1

    def is_execution_started(self) -> bool:
        return self._exec_started

    def get_iteration_count(self) -> int:
        """ Returns number of iterations executed. The first iteration is number 0. """
        return self._exec_iterations

    def is_execution_complete(self) -> bool:
        return self._exec_complete

    def finalize(self):
        self._finalized = True

    def is_finalized(self) -> bool:
        return self._finalized

    def cancel(self):
        self._cancelled = True

    def is_cancelled(self) -> bool:
        return self._cancelled

    def set_progress(self, progress: bool | float):
        self._progress = progress

    def get_progress(self) -> bool | float:
        return self._progress

    def set_complete(self):
        self._exec_complete = True

    def force(self):
        pass


TContext = TypeVar('TContext')


class ContextEngineCommand(Generic[TContext], EngineCommand):
    """ Extension of EngineCommand that provides a typed context.

    This allows Uod commands to extend EngineCommand without importing Engine.
    """
    def __init__(self, context: TContext, name: str) -> None:
        super().__init__(name)
        self.context: TContext = context
