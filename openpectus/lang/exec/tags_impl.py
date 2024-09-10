import time

from openpectus.lang.exec.tags import Tag, TagDirection
from openpectus.lang.exec.tag_lifetime import BlockInfo, TagContext

# Make sure the mark separator does not conflict with ArchiverTag delimiter.
# This wold make the archiver unable to write its archive file.
#MARK_SEPARATOR = ", "
MARK_SEPARATOR = "; "


class ReadingTag(Tag):
    """ Represents a common reading, i.e. a input tag with float values. """
    def __init__(self, name: str, unit: str | None = None) -> None:
        super().__init__(name, value=0.0, unit=unit, direction=TagDirection.INPUT)


class SelectTag(Tag):
    """ Represents a tag with choice values. """
    def __init__(self, name: str, value, unit: str | None,
                 choices: list[str], direction: TagDirection = TagDirection.NA) -> None:
        super().__init__(name=name, value=value, unit=unit, direction=direction)
        if choices is None or len(choices) == 0:
            raise ValueError("choices must be non-empty")
        self.choices = choices


class MarkTag(Tag):
    def __init__(self) -> None:
        super().__init__(name="Mark")

    def set_value(self, val: int | float | str | None, tick_time: float) -> None:
        """ Append value to existing value """
        assert isinstance(val, str), f"The Mark tag value must be a str, not a {type(val).__name__}"
        value = str(self.get_value() or "")
        if value == "":
            value = str(val)
        else:
            value += MARK_SEPARATOR + str(val)
        super().set_value(value, tick_time)

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

    def reset(self):
        self.v0 = self.totalizer.as_float()
        self.value = 0.0
        assert self.v0 is not None

    def on_start(self, context: TagContext):
        self.reset()

    def on_tick(self, tick_time: float):
        assert self.v0 is not None
        self.value = self.totalizer.as_float() - self.v0


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
        self.context: TagContext | None = None

        self.value = 0.0
        self.unit = self.totalizer.unit

    def on_start(self, context: TagContext):
        self.context = context
        self.cur_accumulator.on_start(context)

    def on_tick(self, tick_time: float):
        # tick all accumulators in scope to update block values
        for acc in self.accumulator_stack:
            acc.on_tick(tick_time)

        # apply the current value
        self.value = self.cur_accumulator.get_value()

    def on_block_start(self, block_info: BlockInfo):
        self.cur_block = block_info
        self.cur_accumulator = AccumulatorTag(self.cur_block.key, self.totalizer)
        self.accumulator_stack.append(self.cur_accumulator)

        assert self.context is not None
        self.cur_accumulator.on_start(self.context)

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

    def on_start(self, context: TagContext):
        self.reset()

    def on_tick(self, tick_time: float):
        cv = self.column_volume.as_float()
        v = self.totalizer.as_float()
        if cv == 0.0:
            self.value = None
        else:
            self.value = (v-self.v0) / cv


def format_time_as_clock(value: float) -> str:
    import datetime
    date = datetime.datetime.fromtimestamp(value, datetime.UTC)
    tm = date.time()
    return f"{tm.hour:02}:{tm.minute:02}:{tm.second:02}"
