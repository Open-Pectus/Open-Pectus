""" Event subsystem that defines life-time events during method execution. """
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Iterable

logger = logging.getLogger(__name__)


class EventListener:
    """ Defines the listener interface and base class for engine life-time events. """
    def __init__(self) -> None:
        self.run_id: str | None = None

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(run_id="{self.run_id}")'

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
    """ Emitter of EventListener events.

    Enables emitting execution events to a collection of listeners.
    """
    def __init__(self, listeners: Iterable[EventListener]) -> None:
        self._listeners: list[EventListener] = list(listeners)

    def __str__(self) -> str:
        listeners = [str(listener) for listener in self._listeners]
        return f'{self.__class__.__name__}(_listeners={listeners})'

    def add_listener(self, listener: EventListener):
        self._listeners.append(listener)

    def emit_on_engine_configured(self):
        for element in self._listeners:
            try:
                element.on_engine_configured()
            except Exception:
                logger.error(f"on_engine_configured failed for element '{str(element)}'", exc_info=True)

    def emit_on_start(self, run_id: str):
        for element in self._listeners:
            try:
                element._on_before_start(run_id)
            except Exception:
                logger.error(f"on_before_start failed for element '{str(element)}'", exc_info=True)
        for element in self._listeners:
            try:
                element.on_start(run_id)
            except Exception:
                logger.error(f"on_engine_start failed for element '{str(element)}'", exc_info=True)

    def emit_on_tick(self, tick_time: float, increment_time: float):
        for element in self._listeners:
            try:
                element.on_tick(tick_time, increment_time)
            except Exception:
                logger.error(f"on_tick failed for element '{str(element)}'", exc_info=True)

    def emit_on_block_start(self, block_name: str, tick: int):
        for element in self._listeners:
            try:
                element.on_block_start(BlockInfo(block_name, tick))
            except Exception:
                logger.error(f"on_block_start failed for element '{str(element)}'", exc_info=True)

    def emit_on_block_end(self, block_name: str, new_block_name: str, tick: int):
        for element in self._listeners:
            try:
                element.on_block_end(BlockInfo(block_name, tick), BlockInfo(new_block_name, tick))
            except Exception:
                logger.error(f"on_block_end failed for element '{str(element)}'", exc_info=True)

    def emit_on_method_end(self):
        for element in self._listeners:
            try:
                element.on_method_end()
            except Exception:
                logger.error(f"on_method_end failed for element '{str(element)}'", exc_info=True)

    def emit_on_stop(self):
        for element in self._listeners:
            try:
                element.on_stop()
            except Exception:
                logger.error(f"on_stop failed for element '{str(element)}'", exc_info=True)

    def emit_on_engine_shutdown(self):
        for element in self._listeners:
            try:
                element.on_engine_shutdown()
            except Exception:
                logger.error(f"on_engine_shutdown failed for element '{str(element)}'", exc_info=True)


@dataclass(frozen=True)
class BlockInfo:
    name: str
    tick: int

    @property
    def key(self) -> str :
        """ Gets the block name as a unique name across a single excution. """
        return self.name + "_" + str(self.tick)
