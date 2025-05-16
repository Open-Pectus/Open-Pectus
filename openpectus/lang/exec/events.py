""" Event subsystem that defines life-time events during method execution. """
# pyright: reportImportCycles=false
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import logging
import sys
from typing import Iterable
import time



logger = logging.getLogger(__name__)


class RunStateChange(StrEnum):
    PAUSE = "Pause"
    UNPAUSE = "Unpause"


class EventListener:
    """ Defines the listener interface and base class for engine life-time events. """
    def __init__(self) -> None:
        super(EventListener, self).__init__()

        self.run_id: str | None = None

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(run_id="{self.run_id}")'

    def on_engine_configured(self):
        """ Invoked once on engine startup, after configuration and after
        the connection to hardware has been established. """

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

    def on_scope_start(self, node_id: str):
        pass

    def on_scope_activate(self, node_id: str):
        pass

    def on_scope_end(self, node_id: str):
        pass

    def on_tick(self, tick_time: float, increment_time: float):
        """ Is invoked on each tick.

        Intended for NA (calculated/derived) tags to calculate the
        value for the tick and apply it to the value property. """
        pass

    def on_runstate_change(self, state_change: RunStateChange):
        """ Is invoked when method interpretation is complete. """
        pass

    def on_method_end(self):
        """ Is invoked when interpretation of the last method line is complete. Note: This does
        not necessarily mean that interpretation ends:
        - Any alarms still have their condition evaluated and may execute
        - The method may be modified by the user and the new lines will start executing
        """
        pass

    def on_stop(self):
        """ Is invoked by the Stop command when method is stopped. """
        self.run_id = None

    def on_engine_shutdown(self):
        """ Invoked once when engine shuts down"""
        self.run_id = None


class PerformanceTimer(EventListener):
    """ Monitors execution time of event handlers and warns if they're slow. """

    def __init__(self, listener: EventListener):
        from openpectus.lang.exec.tags import Tag  # Avoid circular import by importing here.
        self._t0: float = 0.0
        self._warned = False
        self._listener = listener
        self._is_tag = isinstance(listener, Tag)
        self._event_name: str = ""

    def __enter__(self):
        # hack to get name of the calling method which is the event handler
        frame = sys._getframe().f_back
        if frame is not None:
            self._event_name = frame.f_code.co_name
        else:
            self._event_name = "(unknown)"
        self._t0 = time.perf_counter()

    def __exit__(self, exc_type, exc_value, traceback):
        t1 = time.perf_counter()
        dt = t1 - self._t0
        if self._is_tag and not self._warned and dt > 0.01:
            logger.warning(f"{self._listener} event handler '{self._event_name}' " +
                           f"is slow. Execution time: {dt:0.1f} s. This warning is only issued once.")
            self._warned = True
        self._event_name = ""

    def on_engine_configured(self):
        with self:
            self._listener.on_engine_configured()

    def _on_before_start(self, run_id: str):
        self.run_id = run_id
        with self:
            self._listener._on_before_start(run_id)

    def on_start(self, run_id: str):
        with self:
            self._listener.on_start(run_id)

    def on_block_start(self, block_info: BlockInfo):
        with self:
            self._listener.on_block_start(block_info)

    def on_block_end(self, block_info: BlockInfo, new_block_info: BlockInfo | None):
        with self:
            self._listener.on_block_end(block_info, new_block_info)

    def on_scope_start(self, node_id: str):
        with self:
            self._listener.on_scope_start(node_id)

    def on_scope_activate(self, node_id: str):
        with self:
            self._listener.on_scope_activate(node_id)

    def on_scope_end(self, node_id: str):
        with self:
            self._listener.on_scope_end(node_id)

    def on_tick(self, tick_time: float, increment_time: float):
        with self:
            self._listener.on_tick(tick_time, increment_time)

    def on_runstate_change(self, state_change: RunStateChange):
        with self:
            self._listener.on_runstate_change(state_change)

    def on_method_end(self):
        with self:
            self._listener.on_method_end()

    def on_stop(self):
        with self:
            self._listener.on_stop()
        self.run_id = None

    def on_engine_shutdown(self):
        with self:
            self._listener.on_engine_shutdown()
        self.run_id = None

    def __str__(self) -> str:
        return f"PerformanceTimer(listener: {self._listener}, warned: {self._warned}, is_tag: {self._is_tag}"


class EventEmitter:
    """ Emitter of EventListener events.

    Enables emitting execution events to a collection of listeners.
    """
    def __init__(self, listeners: Iterable[EventListener]) -> None:
        self._use_perf_timers = True
        self._listeners: list[EventListener] = []
        for listener in listeners:
            self.add_listener(listener)

    def __str__(self) -> str:
        listeners = [str(listener) for listener in self._listeners]
        return f'{self.__class__.__name__}(_listeners={listeners})'

    def add_listener(self, listener: EventListener):
        if self._use_perf_timers:
            self._listeners.append(PerformanceTimer(listener))
        else:
            self._listeners.append(listener)

    def emit_on_engine_configured(self):
        for listener in self._listeners:
            try:
                listener.on_engine_configured()
            except Exception:
                logger.error(f"on_engine_configured failed for listener '{listener}'", exc_info=True)

    def emit_on_start(self, run_id: str):
        for listener in self._listeners:
            try:
                listener._on_before_start(run_id)
            except Exception:
                logger.error(f"on_before_start failed for listener '{listener}'", exc_info=True)
        for listener in self._listeners:
            try:
                listener.on_start(run_id)
            except Exception:
                logger.error(f"on_engine_start failed for listener '{listener}'", exc_info=True)

    def emit_on_tick(self, tick_time: float, increment_time: float):
        for listener in self._listeners:
            try:
                listener.on_tick(tick_time, increment_time)
            except Exception:
                logger.error(f"on_tick failed for listener '{listener}'", exc_info=True)

    def emit_on_block_start(self, block_name: str, tick: int):
        for listener in self._listeners:
            try:
                listener.on_block_start(BlockInfo(block_name, tick))
            except Exception:
                logger.error(f"on_block_start failed for listener '{listener}'", exc_info=True)

    def emit_on_block_end(self, block_name: str, new_block_name: str, tick: int):
        for listener in self._listeners:
            try:
                listener.on_block_end(BlockInfo(block_name, tick), BlockInfo(new_block_name, tick))
            except Exception:
                logger.error(f"on_block_end failed for listener '{listener}'", exc_info=True)

    def emit_on_scope_start(self, node_id: str):
        for listener in self._listeners:
            try:
                listener.on_scope_start(node_id)
            except Exception:
                logger.error(f"on_scope_start failed for listener '{listener}'", exc_info=True)

    def emit_on_scope_activate(self, node_id: str):
        for listener in self._listeners:
            try:
                listener.on_scope_activate(node_id)
            except Exception:
                logger.error(f"on_scope_activate failed for listener '{listener}'", exc_info=True)

    def emit_on_scope_end(self, node_id: str):
        for listener in self._listeners:
            try:
                listener.on_scope_end(node_id)
            except Exception:
                logger.error(f"on_scope_end failed for listener '{listener}'", exc_info=True)

    def emit_on_runstate_change(self, state_change: RunStateChange):
        for listener in self._listeners:
            try:
                listener.on_runstate_change(state_change)
            except Exception:
                logger.error(f"on_runstate_change failed for listener '{listener}'", exc_info=True)

    def emit_on_method_end(self):
        for listener in self._listeners:
            try:
                listener.on_method_end()
            except Exception:
                logger.error(f"on_method_end failed for listener '{listener}'", exc_info=True)

    def emit_on_stop(self):
        for listener in self._listeners:
            try:
                listener.on_stop()
            except Exception:
                logger.error(f"on_stop failed for listener '{listener}'", exc_info=True)

    def emit_on_engine_shutdown(self):
        for listener in self._listeners:
            try:
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
