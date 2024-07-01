

from openpectus.lang.exec.tags import Tag, TagDirection
from openpectus.lang.exec.tag_lifetime import BlockInfo, TagContext


class ReadingTag(Tag):
    def __init__(self, name: str, unit: str | None = None) -> None:
        super().__init__(name, value=0.0, unit=unit, direction=TagDirection.INPUT)


class SelectTag(Tag):
    def __init__(self, name: str, value, unit: str | None,
                 choices: list[str], direction: TagDirection = TagDirection.NA) -> None:
        super().__init__(name=name, value=value, unit=unit, direction=direction)
        if choices is None or len(choices) == 0:
            raise ValueError("choices must be non-empty")
        self.choices = choices


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

    def on_tick(self):
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

    def on_tick(self):
        # tick all accumulators in scope to update block values
        for acc in self.accumulator_stack:
            acc.on_tick()

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

    def on_tick(self):
        cv = self.column_volume.as_float()
        v = self.totalizer.as_float()
        if cv == 0.0:
            self.value = None
        else:
            self.value = (v-self.v0) / cv
