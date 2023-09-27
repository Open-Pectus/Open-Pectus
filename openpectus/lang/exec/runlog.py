from __future__ import annotations
from enum import StrEnum, auto
from typing import List
from openpectus.engine.commands import EngineCommand
from openpectus.lang.exec.commands import CommandRequest

from openpectus.lang.exec.tags import TagValueCollection
from openpectus.lang.model.pprogram import PNode


class RunLog():
    def __init__(self) -> None:
        self._items: List[RunLogItem] = []

    def get_items(self) -> List[RunLogItem]:
        return list(self._items)

    def get_item_by_cmd(self, req: CommandRequest) -> RunLogItem | None:
        for item in self._items:
            if item.command_req == req:
                return item

    def get_item_by_node(self, node: PNode) -> RunLogItem | None:
        for item in self._items:
            # NOTE: using identity equality
            if item.node is node:
                return item

    def add_waiting(self, req: CommandRequest, cmd: EngineCommand, time: float, tick: int) -> RunLogItem:
        item = RunLogItem(req)
        item.command = cmd
        item.start = time
        item.start_tick = tick
        item.states = [RunLogItemState.Waiting]
        self._items.append(item)
        return item

    def add_waiting_node(self, req: CommandRequest, node: PNode, time: float, tick: int) -> RunLogItem:
        item = RunLogItem(req)
        item.node = node
        item.start = time
        item.start_tick = tick
        item.states = [RunLogItemState.Waiting]
        self._items.append(item)
        return item

    def add_completed(self, req: CommandRequest, time: float, tick: int, tags: TagValueCollection) -> RunLogItem:
        """ Add an item that is immidiately started and completed """
        item = RunLogItem(req)
        item.start = time
        item.start_tick = tick
        item.end = time
        item.end_tick = tick
        item.states = [RunLogItemState.Started, RunLogItemState.Completed]
        item.start_values = tags
        item.end_values = tags
        self._items.append(item)
        return item


class RunLogItem():
    def __init__(self, command_req: CommandRequest) -> None:
        self.command_req: CommandRequest = command_req
        self.command: EngineCommand | None = None
        self.node: PNode | None = None
        self.start: float | None = None
        self.start_tick: int = -1
        self.end: float | None = None
        self.end_tick: int = -1
        self.states: List[RunLogItemState] = []
        self.start_values: TagValueCollection | None = None
        self.end_values: TagValueCollection | None = None

    def add_start_state(self, time: float, tick: int, start_tags: TagValueCollection):
        self.start = time
        self.start_tick = tick
        self.add_state(RunLogItemState.Started)
        self.start_values = start_tags

    def add_state(self, state: RunLogItemState):
        self.states.append(state)

    def add_end_state(self, state: RunLogItemState, time: float, tick: int, end_tags: TagValueCollection):
        self.end = time
        self.end_tick = tick
        self.states.append(state)
        self.end_values = end_tags


class RunLogItemState(StrEnum):
    """ Defines the states that commands in the run log can take """
    Waiting = auto()
    """ Waiting for threshold or condition """
    Started = auto()
    """ Command has started """
    Cancelled = auto()
    """ Command was cancelled. Either by overlapping command or explicitly by user """
    Forced = auto()
    """ Waiting command was forcibly started """
    Completed = auto()
    """ Command has completed """
    Failed = auto()
    """ Command failed """

    @staticmethod
    def has_value(value: str):
        """ Determine if enum has this string value defined. Case sensitive. """
        return hasattr(RunLogItemState, value)
