from __future__ import annotations
from enum import StrEnum, auto
from typing import Dict, List
from uuid import UUID, uuid4
from openpectus.engine.commands import EngineCommand

from openpectus.lang.exec.tags import TagValueCollection
from openpectus.lang.model.pprogram import PNode, PProgram


class RuntimeInfo():
    """ Provides a log of the actions that take place during interpretation.

    It consists of a list of records. Each record has a name and a list of
    states. The record state contain a state name, time and the tag values
    at the time the state was created.

    As interpretation progresses, the program AST nodes (subclasses of PNode)
    are visited and their semantics are executed. The records added are:

    - For all visited nodes, a record is added. The name of the record is
      provided by PNode.runlog_name if overwritten by the particular subclass.
      When a record is created, its exec_id is given a random UUID.

    - Instructions that are interpreted via an interrupt, reuse the record
      that was created when the node was first visited.

      Alarms too?

    - Engine commands are currently not contained in records.

    - Uod commands are executed via context.schedule_execution(). The interpreter
      does not know what happens after that. The engine updates the record as
      these commands are executed, cancelled etc. The record states are provided
      with the command instance as well as a command_exec_id that tracks a
      particular command instance. This means that one record may hold states
      for different invocations (and instances) of the same command.
    """
    def __init__(self) -> None:
        self._records: list[RuntimeRecord] = []
        self._record_index: Dict[UUID, int] = {}

    @property
    def records(self) -> list[RuntimeRecord]:
        return list(self._records)

    def get_runlog(self) -> RunLog:
        """ Transmogrify the runtime records into the RunLog shape that clients
        understand.

        Notably, it removes records with no name and unscrambles uod states
        such that each invocation gets its own record. This allows the client
        to force or cancel a particular command instance.
        """
        items: list[RunLogItem] = []

        runlog = RunLog()
        runlog.id = ""
        runlog.items = items

        for r in self.records:
            if isinstance(r.node, PProgram):
                runlog.id = str(r.node.id)
            if r.name is None:
                continue

            item = RunLogItem()
            item.name = r.name
            item.id = str(r.exec_id)
            #item.progress

            if r.has_state(RuntimeRecordStateEnum.UodCommandSet):
                # sanity check
                set_count = len([st for st in r.states if st.state_name == RuntimeRecordStateEnum.UodCommandSet])
                start_count = len([st for st in r.states if st.state_name == RuntimeRecordStateEnum.Started])
                complete_count = len([st for st in r.states if st.state_name == RuntimeRecordStateEnum.Completed])
                assert set_count < 2, f"{set_count=} was greater than 1 - unexpected?!"
                assert start_count < 2, f"{start_count=} was greater than 1 - unexpected?!"
                assert complete_count < 2, f"{complete_count=} was greater than 1 - unexpected?!"
            if r.has_state(RuntimeRecordStateEnum.Completed):
                item.state = RunLogItemState.Completed
                state = r.get_state(RuntimeRecordStateEnum.Completed)
                item.end = state.state_time
                item.end_values = state.values.non_system_tags_collection() if state.values is not None else TagValueCollection.empty()
            elif r.has_state(RuntimeRecordStateEnum.Failed):
                item.state = RunLogItemState.Failed
                state = r.get_state(RuntimeRecordStateEnum.Failed)
                item.end = state.state_time
                item.end_values = state.values.non_system_tags_collection() if state.values is not None else TagValueCollection.empty()
            elif r.has_state(RuntimeRecordStateEnum.Cancelled):
                item.state = RunLogItemState.Cancelled
                state = r.get_state(RuntimeRecordStateEnum.Cancelled)
                item.end = state.state_time
                item.end_values = state.values.non_system_tags_collection() if state.values is not None else TagValueCollection.empty()
            elif r.has_state(RuntimeRecordStateEnum.Forced):
                item.state = RunLogItemState.Forced
            elif r.has_state(RuntimeRecordStateEnum.Started):
                item.state = RunLogItemState.Started
                state = r.get_state(RuntimeRecordStateEnum.Started)
                item.start = state.state_time
                item.start_values = state.values.non_system_tags_collection() if state.values is not None else TagValueCollection.empty()
            else:
                item.state = RunLogItemState.Waiting

            if item.start is None:
                # TODO this should not happen, should it?
                item.start = r.visit_start_time

            items.append(item)
        return runlog

    def get_exec_record(self, exec_id: UUID) -> RuntimeRecord:
        index = self._record_index.get(exec_id)
        if index is not None:
            return self._records[index]
        raise ValueError(f"exec_id {exec_id} has no record")

    def get_uod_command_and_record(self, command_exec_id: UUID) -> tuple[EngineCommand, RuntimeRecord] | None:
        for record in reversed(self.records):
            for state in record.states:
                if state.command_exec_id is not None and state.command_exec_id == command_exec_id:
                    if state.command is not None:
                        return state.command, record

    def get_last_node_record_or_none(self, node: PNode) -> RuntimeRecord | None:
        for r in reversed(self._records):
            if r.node == node:
                return r

    def get_last_node_record(self, node: PNode) -> RuntimeRecord:
        record = self.get_last_node_record_or_none(node)
        if record is None:
            raise ValueError("Node has no records")
        return record

    def get_node_records(self, node: PNode) -> List[RuntimeRecord]:
        return [r for r in self._records if r.node.id == node.id]

    def _add_record(self, record: RuntimeRecord, exec_id: UUID):
        index = len(self._records)
        self._records.append(record)
        self._record_index[exec_id] = index
        assert self._records[index].exec_id == exec_id
        self._last_exec_id = exec_id

    def begin_visit(
            self,
            node: PNode,
            time: float, tick: int,
            start_values: TagValueCollection) -> RuntimeRecord:
        exec_id = uuid4()
        record = RuntimeRecord(node, exec_id=exec_id)
        record.visit_start_time = time
        record.visit_start_tick = tick
        record.start_values = start_values
        self._add_record(record, exec_id=exec_id)
        return record


class RuntimeRecord():
    def __init__(self, node: PNode, exec_id: UUID) -> None:
        self.exec_id: UUID = exec_id
        self.node = node
        self.name = node.runlog_name
        self.visit_start_time: float = -1.0
        self.visit_start_tick: int = -1
        self.visit_end_time: float = -1.0
        self.visit_end_tick: int = -1

        self.states: List[RuntimeRecordState] = []
        self.start_values: TagValueCollection | None = None
        self.end_values: TagValueCollection | None = None

    def __repr__(self) -> str:
        return f"{self.name} | States: {', '.join([str(st) for st in self.states ])}"

    # -- regular state --

    def has_state(self, state: RuntimeRecordStateEnum) -> bool:
        return any([st for st in self.states if st.state_name == state])

    def get_state(self, state: RuntimeRecordStateEnum, first=True) -> RuntimeRecordState:
        states = [st for st in self.states if st.state_name == state]
        if first:
            return states[0]
        else:
            return states[-1]

    def add_state(self,
                  state: RuntimeRecordStateEnum,
                  time: float, tick: int,
                  state_values: TagValueCollection | None) -> RuntimeRecordState:
        record_state = RuntimeRecordState(state, time, tick, state_values)
        self.states.append(record_state)
        return record_state

    def add_state_awaiting_threshold(self, time: float, tick: int, state_values: TagValueCollection | None):
        self.add_state(RuntimeRecordStateEnum.AwaitingThreshold, time, tick, state_values)

    def add_state_awaiting_condition(self, time: float, tick: int, state_values: TagValueCollection | None):
        self.add_state(RuntimeRecordStateEnum.AwaitingCondition, time, tick, state_values)

    def add_state_awaiting_interrupt(self, time: float, tick: int, state_values: TagValueCollection | None):
        self.add_state(RuntimeRecordStateEnum.AwaitingInterrrupt, time, tick, state_values)

    def add_state_started(self, time: float, tick: int, end_values: TagValueCollection):
        self.add_state(RuntimeRecordStateEnum.Started, time, tick, end_values)

    def add_state_completed(self, time: float, tick: int, end_values: TagValueCollection):
        self.add_state(RuntimeRecordStateEnum.Completed, time, tick, end_values)

    def add_state_failed(self, time: float, tick: int, end_values: TagValueCollection):
        self.add_state(RuntimeRecordStateEnum.Failed, time, tick, end_values)

    def set_end_visit(self, time: float, tick: int, end_values: TagValueCollection):
        self.visit_end_time = time
        self.visit_end_tick = tick
        self.end_values = end_values

    # -- command state --

    def add_state_uod_command_set(self, uod_command: EngineCommand,
                                  time: float, tick: int,
                                  state_values: TagValueCollection | None) -> UUID:
        state = self.add_state(RuntimeRecordStateEnum.UodCommandSet, time, tick, state_values)
        state.command = uod_command
        state.command_exec_id = uuid4()
        return state.command_exec_id

    def add_command_state_cancelled(
            self, command_exec_id: UUID,
            time: float, tick: int, end_values: TagValueCollection):
        state = self.add_state(RuntimeRecordStateEnum.Cancelled, time, tick, end_values)
        state.command_exec_id = command_exec_id

    def add_command_state_started(
            self, command_exec_id: UUID,
            time: float, tick: int, end_values: TagValueCollection):
        state = self.add_state(RuntimeRecordStateEnum.Started, time, tick, end_values)
        state.command_exec_id = command_exec_id

    def add_command_state_completed(
            self, command_exec_id: UUID,
            time: float, tick: int, end_values: TagValueCollection):
        state = self.add_state(RuntimeRecordStateEnum.Completed, time, tick, end_values)
        state.command_exec_id = command_exec_id

    def add_command_state_failed(
            self, command_exec_id: UUID,
            time: float, tick: int, end_values: TagValueCollection):
        state = self.add_state(RuntimeRecordStateEnum.Failed, time, tick, end_values)
        state.command_exec_id = command_exec_id


class RuntimeRecordState():
    def __init__(
            self,
            state: RuntimeRecordStateEnum,
            time: float, tick: int,
            values: TagValueCollection | None
            ) -> None:
        self.state_name: RuntimeRecordStateEnum = state
        self.state_time: float = time
        self.state_tick: int = tick
        self.values: TagValueCollection | None = values
        self.command: EngineCommand | None = None
        self.command_exec_id: UUID | None = None

    def __str__(self) -> str:
        return f"{self.state_name}"


class RuntimeRecordStateEnum(StrEnum):
    """ Defines the states runtime records can take """

    Visited = auto()
    """ Instruction node was visited"""
    UodCommandSet = auto()
    """ Uod command was set """
    AwaitingThreshold = auto()
    """ Waiting for threshold """
    AwaitingCondition = auto()
    """ Waiting for condition """
    AwaitingInterrrupt = auto()
    """ Instruction is awaiting invocation by interrupt """
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
        return hasattr(RuntimeRecordStateEnum, value)


class RunLog():
    def __init__(self) -> None:
        self.id: str = ""
        self.items: List[RunLogItem] = []


class RunLogItem():
    def __init__(self) -> None:
        self.id: str = ""
        self.name: str = ""
        self.start: float = 0
        self.end: float | None = None
        self.state: RunLogItemState = RunLogItemState.Waiting
        self.progress: float | None = None
        self.start_values: TagValueCollection = TagValueCollection.empty()
        self.end_values: TagValueCollection = TagValueCollection.empty()


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
