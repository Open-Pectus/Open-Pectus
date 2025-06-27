from __future__ import annotations
import logging
import time

from openpectus.lang.exec.tags import SystemTagName, Tag, TagDirection, TagFormatFunction, format_time_as_clock
from openpectus.lang.exec.events import BlockInfo, RunStateChange
from openpectus.lang.exec.tracer import Tracer

# Make sure the mark separator does not conflict with ArchiverTag delimiter.
# This wold make the archiver unable to write its archive file.
# MARK_SEPARATOR = ", "
MARK_SEPARATOR = "; "


logger = logging.getLogger(__name__)


class ReadingTag(Tag):
    """ Represents a common reading, i.e. a input tag with float values. """
    def __init__(self, name: str, unit: str | None = None, format_fn: TagFormatFunction | None = None) -> None:
        super().__init__(name, value=0.0, unit=unit, direction=TagDirection.Input, format_fn=format_fn)

    def set_value(self, val, *args, **kwargs):
        if val is not None:
            try:
                float(val)
            except Exception:
                raise ValueError(
                    f'ReadingTag "{self.name}" cannot be set to "{val}" because it cannot be coerced to float type.')
        super().set_value(val, *args, **kwargs)


class SelectTag(Tag):
    """ Represents a tag with choice values. """
    def __init__(self, name: str, value, unit: str | None,
                 choices: list[str], direction: TagDirection = TagDirection.NA) -> None:
        super().__init__(name=name, value=value, unit=unit, direction=direction)
        if choices is None or len(choices) == 0:
            raise ValueError(f'SelectTag "{self.name}" has no choices. Choices must be non-empty.')
        self.choices = choices

    def set_value(self, val, *args, **kwargs):
        assert val in self.choices, \
            f'SelectTag "{self.name}" cannot be set to "{val}" because it is not among the valid options: "{self.choices}".'
        super().set_value(val, *args, **kwargs)


class MarkTag(Tag):
    def __init__(self) -> None:
        super().__init__(name=SystemTagName.MARK)

    def set_value(self, val: int | float | str | None, tick_time: float, *args, **kwargs) -> None:
        """ Append value to existing value """
        assert isinstance(val, str), f"The Mark tag value must be a str, not a {type(val).__name__}"
        value = str(self.get_value() or "")
        if value == "":
            value = str(val)
        else:
            value += MARK_SEPARATOR + str(val)
        super().set_value(value, tick_time, *args, **kwargs)

    def archive(self) -> str | None:
        """ Reset value and return it """
        value = self.value
        super().set_value("", time.time())
        return str(value or "")


class AccumulatorTag(Tag):
    """ Generic accumulator tag. Can be used as the system tag
        SystemTagName.ACCUMULATED_VOLUME.
    """
    def __init__(self, name: str, totalizer: Tag):
        super().__init__(name)
        self.totalizer: Tag = totalizer
        self.unit = self.totalizer.unit
        self.v0: float | None = None

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(name="{self.name}", value="{self.value}", v0={self.v0})'

    def reset(self):
        self.v0 = self.totalizer.as_float()
        self.value = 0.0
        assert self.v0 is not None

    def on_start(self, run_id: str):
        self.reset()

    def on_tick(self, tick_time: float, increment_time: float):
        assert self.v0 is not None, f"Error in aggregator tag '{self.name}', v0 was not set."
        self.value = self.totalizer.as_float() - self.v0


class BlockTimeTag(Tag):
    tracer = Tracer(logger)

    class StackItem():
        def __init__(self, name):
            self.name = name
            self.value: float = 0.0

    def __init__(self):
        super().__init__(SystemTagName.BLOCK_TIME, unit="s", format_fn=format_time_as_clock)
        # need a custom stack because we have no real key. BlockInfo.key is different in
        # on_block_start and on_block_end
        self._stack: list[BlockTimeTag.StackItem] = []
        self._paused = False
        self.value = 0.0

    def on_start(self, run_id):
        self.value = 0.0
        self._stack.clear()
        self._stack.append(BlockTimeTag.StackItem("root"))
        self.tracer.trace()

    def on_block_start(self, block_info):
        self._stack.append(BlockTimeTag.StackItem(block_info.name))
        self.tracer.trace(f"{block_info.name=}")

    def on_block_end(self, block_info, new_block_info):
        self._stack.pop()
        self.tracer.trace(f"{block_info.name=}")

    def on_tick(self, tick_time, increment_time):
        if self._paused:
            return
        for item in self._stack:
            item.value += increment_time
        self.value = self.get_value()
        # self.tracer.trace(f"{self.value=}")

    def on_runstate_change(self, state_change):
        if state_change == RunStateChange.PAUSE:
            self._paused = True
        elif state_change == RunStateChange.UNPAUSE:
            self._paused = False

    def get_value(self):
        if len(self._stack) == 0:
            return 0.0
        item = self._stack[-1]
        return item.value

class ScopeTimeTag(Tag):
    tracer = Tracer(logger)

    def __init__(self):
        super().__init__(SystemTagName.SCOPE_TIME, unit="s", format_fn=format_time_as_clock)
        self._timers: dict[str, float] = {}
        self._stack: list[str] = []
        self._paused = False
        self.value = 0.0

    def on_start(self, run_id):
        self.value = 0.0
        self.tracer.trace()

    def on_scope_start(self, node_id):
        self.value = 0.0
        self.tracer.trace()

    def on_scope_activate(self, node_id):
        self._timers[node_id] = 0.0
        self._stack.append(node_id)
        self.tracer.trace()

    def on_scope_end(self, node_id):
        del self._timers[node_id]
        self._stack.pop()

    def on_tick(self, tick_time, increment_time):
        if self._paused:
            return
        for key in self._timers.keys():
            self._timers[key] += increment_time
        self.value = self.get_value()
        self.tracer.trace(f"{self.value}")

    def on_runstate_change(self, state_change):
        if state_change == RunStateChange.PAUSE:
            self._paused = True
        elif state_change == RunStateChange.UNPAUSE:
            self._paused = False

    def get_value(self):
        if len(self._stack) == 0:
            return 0.0
        node_id = self._stack[-1]
        try:
            return self._timers[node_id]
        except KeyError:
            logger.error(f"{self.__class__.__name__} | Stack error, node_id: {node_id}, keys: {self._timers.keys()}")
            return 0.0

class AccumulatorBlockTag(Tag):
    """ Implements a block accumulator. Can be used as the system tag
        SystemTagName.BLOCK_VOLUME.
    """
    def __init__(self, name: str, totalizer: Tag):
        super().__init__(name)
        self.totalizer: Tag = totalizer
        self.root_block = BlockInfo("", 0)
        self.accumulator_stack: list[AccumulatorTag] = []
        self.accumulator_stack.append(AccumulatorTag(self.root_block.key, self.totalizer))
        self.cur_block = self.root_block
        self.cur_accumulator = self.accumulator_stack[0]

        self.value = 0.0
        self.unit = self.totalizer.unit

    def on_start(self, run_id: str):
        self.cur_accumulator.on_start(run_id)

    def on_tick(self, tick_time: float, increment_time: float):
        # tick all accumulators in scope to update block values
        for acc in self.accumulator_stack:
            acc.on_tick(tick_time, increment_time)

        # apply the current value
        self.value = self.cur_accumulator.get_value()

    def on_block_start(self, block_info: BlockInfo):
        self.cur_block = block_info
        self.cur_accumulator = AccumulatorTag(self.cur_block.key, self.totalizer)
        self.accumulator_stack.append(self.cur_accumulator)

        assert self.run_id is not None, f"Error in AccumulatorBlockTag tag '{self.name}', run_id not set in on_block_start."
        self.cur_accumulator.on_start(self.run_id)

    def on_block_end(self, block_info: BlockInfo, new_block_info: BlockInfo | None):
        if len(self.accumulator_stack) == 0:
            raise ValueError("Stack is empty. This means on_block_end was called in error")
        self.accumulator_stack.pop()
        self.cur_accumulator = self.accumulator_stack[-1]


class AccumulatedColumnVolume(Tag):
    def __init__(self, name: str, column_volume: Tag, totalizer: Tag):
        super().__init__(name)
        self.totalizer: Tag = totalizer
        self.column_volume: Tag = column_volume
        self.unit = "CV"
        self.v0 = 0.0

    def reset(self):
        self.v0 = self.totalizer.as_float()
        self.value = 0.0
        assert self.v0 is not None

    def on_start(self, run_id: str):
        self.reset()

    def on_tick(self, tick_time: float, increment_time: float):
        cv = self.column_volume.as_float()
        v = self.totalizer.as_float()
        if cv == 0.0:
            self.value = None
        else:
            self.value = (v-self.v0) / cv
