from __future__ import annotations
from typing import Any, Generic, List, TypeVar

TContext = TypeVar('TContext')


class EngineCommand(Generic[TContext]):
    """ Interface for all commands runnable by engine. """
    def __init__(self, context: TContext) -> None:
        self.context: TContext = context

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

    def execute(self, args: List[Any]) -> None:
        self._exec_started = True
        self._exec_iterations += 1

    def is_execution_started(self) -> bool:
        return self._exec_started

    def get_iteration_count(self) -> int:
        """ Returns number of iterations executed. """
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

    def set_complete(self):
        self._exec_complete = True
