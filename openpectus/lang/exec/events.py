""" Event subsystem that defines life-time events during method execution. """
# pyright: reportImportCycles=false
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Iterable
import time

logger = logging.getLogger(__name__)


class PerformanceTimer:
    t0: float
    t1: float

    def __init__(self, listener):
        from openpectus.lang.exec.tags import Tag  # Avoid circular import by importing here.
        self._warned = False
        self.listener = listener
        self.is_tag = False
        if callable(listener) and hasattr(listener, "__self__"):
            self.is_tag = issubclass(getattr(getattr(listener, "__self__"), "__class__"), Tag)

    def __enter__(self):
        self.t0 = time.perf_counter()

    def __exit__(self, exc_type, exc_value, traceback):
        self.t1 = time.perf_counter()
        dt = self.t1-self.t0
        if self.is_tag and not self._warned and dt > 0.01:
            logger.warning(f"{self.listener.__name__} method for {self.listener.__self__} " +
                           f"is slow. Execution time: {dt:0.1f} s. This warning is only issued once.")
            self._warned = True


class EventListener:
    """ Defines the listener interface and base class for engine life-time events. """
    def __init__(self) -> None:
        self.run_id: str | None = None

    def on_engine_configured(self):
        """ Invoked once on engine startup, after configuration and after
        the connection to hardware has been established. """
        pass

    def _on_before_start(self, run_id: str):
        """ Is run by emitter to avoid having all subclasses call super().on_start(). """
        # An alternative approach would be to force subclasses to call super().on_start() using a meta class.
        # This is not supported by pyright though, so it would be a custom check at runtime, e.g.
        # https://stackoverflow.com/questions/67661091/how-can-i-make-it-a-requirement-to-call-super-from-within-an-abstract-method-o
        # or
        # https://stackoverflow.com/questions/66581157/how-to-enforce-mandatory-parent-method-call-when-calling-child-method
        self.run_id = run_id

    def on_start(self, run_id: str):
        """ Is invoked by the Start command when method is started. """
        pass

    def on_block_start(self, block_info: BlockInfo):
        """ Invoked just after a new block is started, before on_tick,
            in the same engine tick.
        """
        pass

    def on_block_end(self, block_info: BlockInfo, new_block_info: BlockInfo | None):
        """ Invoked just after a block is completed, before on_tick,
        in the same engine tick. """
        pass

    def on_tick(self, tick_time: float, increment_time: float):
        """ Is invoked on each tick.

        Intended for NA (calculated/derived) tags to calculate the
        value for the tick and apply it to the value property. """
        pass

    def on_method_end(self):
        """ Is invoked when method interpretation is complete. """
        pass

    def on_stop(self):
        """ Is invoked by the Stop command when method is stopped. """
        self.run_id = None

    def on_engine_shutdown(self):
        """ Invoked once when engine shuts down"""
        self.run_id = None


class EventEmitter:
    handle_names = [
        "on_engine_configured",
        "_on_before_start",
        "on_start",
        "on_tick",
        "on_block_start",
        "on_block_end",
        "on_method_end",
        "on_stop",
        "on_engine_shutdown",
    ]
    """ Emitter of EventListener events.

    Enables emitting execution events to a collection of listeners.
    """
    def __init__(self, listeners: Iterable[EventListener]) -> None:
        self._listeners: list[EventListener] = list(listeners)
        self._performance_timers = dict()
        for listener in self._listeners:
            for handle_name in self.handle_names:
                handle = getattr(listener, handle_name)
                self._performance_timers[handle] = PerformanceTimer(handle)

    def add_listener(self, listener: EventListener):
        self._listeners.append(listener)
        for handle_name in self.handle_names:
            handle = getattr(listener, handle_name)
            self._performance_timers[handle] = PerformanceTimer(handle)

    def emit_on_engine_configured(self):
        for listener in self._listeners:
            try:
                with self._performance_timers[listener.on_engine_configured]:
                    listener.on_engine_configured()
            except Exception:
                logger.error(f"on_engine_configured failed for listener '{listener}'", exc_info=True)

    def emit_on_start(self, run_id: str):
        for listener in self._listeners:
            try:
                with self._performance_timers[listener._on_before_start]:
                    listener._on_before_start(run_id)
            except Exception:
                logger.error(f"on_before_start failed for listener '{listener}'", exc_info=True)
        for listener in self._listeners:
            try:
                with self._performance_timers[listener.on_start]:
                    listener.on_start(run_id)
            except Exception:
                logger.error(f"on_engine_start failed for listener '{listener}'", exc_info=True)

    def emit_on_tick(self, tick_time: float, increment_time: float):
        for listener in self._listeners:
            try:
                with self._performance_timers[listener.on_tick]:
                    listener.on_tick(tick_time, increment_time)
            except Exception:
                logger.error(f"on_tick failed for listener '{listener}'", exc_info=True)

    def emit_on_block_start(self, block_name: str, tick: int):
        for listener in self._listeners:
            try:
                with self._performance_timers[listener.on_block_start]:
                    listener.on_block_start(BlockInfo(block_name, tick))
            except Exception:
                logger.error(f"on_block_start failed for listener '{listener}'", exc_info=True)

    def emit_on_block_end(self, block_name: str, new_block_name: str, tick: int):
        for listener in self._listeners:
            try:
                with self._performance_timers[listener.on_block_end]:
                    listener.on_block_end(BlockInfo(block_name, tick), BlockInfo(new_block_name, tick))
            except Exception:
                logger.error(f"on_block_end failed for listener '{listener}'", exc_info=True)

    def emit_on_method_end(self):
        for listener in self._listeners:
            try:
                with self._performance_timers[listener.on_method_end]:
                    listener.on_method_end()
            except Exception:
                logger.error(f"on_method_end failed for listener '{listener}'", exc_info=True)

    def emit_on_stop(self):
        for listener in self._listeners:
            try:
                with self._performance_timers[listener.on_stop]:
                    listener.on_stop()
            except Exception:
                logger.error(f"on_stop failed for listener '{str(listener)}'", exc_info=True)

    def emit_on_engine_shutdown(self):
        for listener in self._listeners:
            try:
                with self._performance_timers[listener.on_engine_shutdown]:
                    listener.on_engine_shutdown()
            except Exception:
                logger.error(f"on_engine_shutdown failed for listener '{listener}'", exc_info=True)


@dataclass(frozen=True)
class BlockInfo:
    name: str
    tick: int

    @property
    def key(self) -> str :
        """ Gets the block name as a unique name across a single excution. """
        return self.name + "_" + str(self.tick)
