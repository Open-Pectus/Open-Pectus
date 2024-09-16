# pyright: reportImportCycles=none
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:  # Only imports the below statements during type checking
    from openpectus.lang.exec.tags import TagCollection


logger = logging.getLogger(__name__)


class TagContext():
    """ Abstraction around a TagCollection that enables emitting the TagLifetime events
    to the wrapped tags. """
    def __init__(self, tags: TagCollection) -> None:
        self.tags: TagCollection = tags

    def emit_on_engine_configured(self):
        for tag in self.tags:
            try:
                tag.on_engine_configured(self)
            except Exception:
                logger.error(f"on_engine_configured failed for tag '{tag.name}'", exc_info=True)

    def emit_on_start(self):
        for tag in self.tags:
            try:
                tag.on_start(self)
            except Exception:
                logger.error(f"on_engine_start failed for tag '{tag.name}'", exc_info=True)

    def emit_on_tick(self, tick_time: float):
        for tag in self.tags:
            try:
                tag.on_tick(tick_time)
            except Exception:
                logger.error(f"on_tick failed for tag '{tag.name}'", exc_info=True)

    def emit_on_block_start(self, block_name: str, tick: int):
        for tag in self.tags:
            try:
                tag.on_block_start(BlockInfo(block_name, tick))
            except Exception:
                logger.error(f"on_block_start failed for tag '{tag.name}'", exc_info=True)

    def emit_on_block_end(self, block_name: str, new_block_name: str, tick: int):
        for tag in self.tags:
            try:
                tag.on_block_end(BlockInfo(block_name, tick), BlockInfo(new_block_name, tick))
            except Exception:
                logger.error(f"on_block_end failed for tag '{tag.name}'", exc_info=True)

    def emit_on_stop(self):
        for tag in self.tags:
            try:
                tag.on_stop()
            except Exception:
                logger.error(f"on_stop failed for tag '{tag.name}'", exc_info=True)

    def emit_on_engine_shutdown(self):
        for tag in self.tags:
            try:
                tag.on_engine_shutdown()
            except Exception:
                logger.error(f"on_engine_shutdown failed for tag '{tag.name}'", exc_info=True)


class TagLifetime():
    """ Defines the lifetime events that are available for tag implementations.
        The events are emitted by the Engine to both system and uod tags.
    """

    def on_engine_configured(self, context: TagContext):
        """ Invoked once on engine startup, after configuration and after
        the connection to hardware has been established. """
        pass

    def on_start(self, context: TagContext):
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

    def on_tick(self, tick_time: float):
        """ Is invoked on each tick.

        Intended for NA (calculated/derived) tags to calculate the
        value for the tick and apply it to the value property. """
        pass

    def on_stop(self):
        """ Is invoked by the Stop command when method is stopped. """
        pass

    def on_engine_shutdown(self):
        """ Invoked once when engine shuts down"""
        pass


@dataclass(frozen=True)
class BlockInfo:
    name: str
    tick: int

    @property
    def key(self) -> str :
        return self.name + "_" + str(self.tick)
