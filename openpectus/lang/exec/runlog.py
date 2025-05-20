from __future__ import annotations

import copy
import logging
from enum import StrEnum, auto
from typing import Dict
from uuid import UUID, uuid4

from openpectus.engine.commands import EngineCommand
from openpectus.lang.exec.tags import TagValueCollection
from openpectus.lang.exec.uod import UodCommand
import openpectus.lang.model.ast as p

logger = logging.getLogger(__name__)


class RuntimeInfo:
    """ Provides a log of the actions that take place during interpretation.

    It consists of a list of records. Each record has a name and a list of
    states. The record state contain a state name, time and the tag values
    at the time the state was created.

    As interpretation progresses, the program AST nodes (subclasses of p.Node)
    are visited and their semantics are executed. The records added are:

    - For all visited nodes, a record is added. The name of the record is
      provided by p.Node.runlog_name if overwritten by the particular subclass.
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

    def __str__(self) -> str:
        records = [str(record) for record in self.records]
        return f'{self.__class__.__name__}(records="{records}")'

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
        such that each invocation gets its own runlog item. This allows the client
        to force or cancel a particular command instance.
        """
        runlog = RunLog()
        runlog.id = self._get_runlog_id() or ""
        for r in self.records:
            try:
                items = self._get_record_runlog_items(r)
                runlog.items.extend(items)
            except Exception:
                logger.error(f"Failed to create runlog item for record {r}", exc_info=True)
        runlog.items.sort(key=lambda item: item.start)
        return runlog

    def _get_runlog_id(self) -> str | None:
        for r in self.records:
            if isinstance(r.node, p.ProgramNode):
                return str(r.node.id)

    def _get_record_runlog_items(self, r: RuntimeRecord) -> list[RunLogItem]:  # noqa C901
        if isinstance(r.node, (p.ProgramNode, p.BlankNode, p.CommentNode)):
            return []
        if r.name is None:
            if isinstance(r.node, (p.InjectedNode, p.ErrorInstructionNode)):
                return []
            node_name = str(r.node) if r.node is not None else "node is None"
            logger.error(f"Runtime record has empty name. node: {node_name}. Fix this error or add a rule exception.")
            return []
        if r.name == "Stop":
            return []

        items: list[RunLogItem] = []

        # Usually there is only a single start/complete state pair which is what is needed for a runlog item.
        # But, alas, alarms can be invoked any number of times for which all state information is placed in
        # the same runtime record. Therefore we need to expand these states into seperate run log items.
        # And because any node can be in a PAlarm body, this extends to all other nodes as well.
        split_states = self._split_states(r, include_prestart_states=False)
        # iterate the invocations
        for invocation_inx, invocation_states in enumerate(split_states):
            # is_before_first_invocation = False
            # has_more_invocations = invocation_inx < len(split_states) - 1
            item: RunLogItem | None = None
            command: EngineCommand | None = None
            # iterate the states of the invocation
            for inx, state in enumerate(invocation_states):
                is_start_state = inx == 0
                has_more_states = inx < len(invocation_states) - 1
                is_conclusive_state = state.state_name in [
                    RuntimeRecordStateEnum.Completed, RuntimeRecordStateEnum.Failed, RuntimeRecordStateEnum.Cancelled
                ]

                if is_start_state:
                    item = RunLogItem()
                    item.name = r.name
                    item.id = str(r.exec_id)  # Note is changed to command_exec_id later for uod commands
                    item.state = RunLogItemState.Started  # TODO possibly improve - could also be Waiting
                    item.start = state.state_time
                    item.start_values = state.values or TagValueCollection.empty()
                    item.cancellable = r.node.cancellable
                    item.cancelled = r.node.cancelled
                    item.forcible = r.node.forcible
                    item.forced = r.node.forced

                if state.state_name == RuntimeRecordStateEnum.Completed:
                    assert item is not None
                    item.state = RunLogItemState.Completed
                elif state.state_name == RuntimeRecordStateEnum.Failed:
                    assert item is not None
                    item.state = RunLogItemState.Failed
                elif state.state_name == RuntimeRecordStateEnum.Cancelled:
                    assert item is not None
                    item.state = RunLogItemState.Cancelled
                    item.cancelled = True
                elif state.state_name == RuntimeRecordStateEnum.Forced:
                    assert item is not None
                    item.state = RunLogItemState.Forced
                    item.forced = True
                elif state.state_name == RuntimeRecordStateEnum.UodCommandSet:
                    assert item is not None
                    logger.debug(f"Updating uod item id from record id {item.id} to" +
                                 f"record state command_exec_id {state.command_exec_id}")
                    item.id = str(state.command_exec_id)
                    command = state.command
                elif state.state_name == RuntimeRecordStateEnum.InternalEngineCommandSet:
                    assert item is not None
                    logger.debug(f"Updating internal engine item id from record id {item.id} to" +
                                 f"record state command_exec_id {state.command_exec_id}")
                    item.id = str(state.command_exec_id)
                    command = state.command
                elif state.state_name == RuntimeRecordStateEnum.AwaitingThreshold:
                    assert item is not None
                    item.state = RunLogItemState.AwaitingThreshold

                if not is_conclusive_state and item is not None:
                    item.cancellable = r.node.cancellable
                    item.forcible = r.node.forcible
                    if command is not None:
                        if isinstance(command, UodCommand):
                            item.cancellable = True  # PCommand.cancellable does not support uod commands
                        self._update_item_progress(item, command)
                    elif r.progress is not None:
                        self._update_item_progress(item, r)

                if is_conclusive_state:
                    assert item is not None
                    item.end = state.state_time
                    item.end_values = state.values or TagValueCollection. empty()
                    item.cancellable = False
                    item.forcible = False

                if not has_more_states or is_conclusive_state:
                    if item is not None and item.state not in [RunLogItemState.Unknown, RunLogItemState.AwaitingThreshold]:
                        items.append(item)
                        item = None
                        command = None

        return items

    def _split_states(self, r: RuntimeRecord, include_prestart_states: bool) -> list[list[RuntimeRecordState]]:
        """ Split a record's states into those of distint invocations."""
        if len(r.states) == 0:
            return []

        split_states: list[list[RuntimeRecordState]] = []

        if r.has_state(RuntimeRecordStateEnum.UodCommandSet):
            # UodCommandSet signifies the start of a uod command invocation
            split_states = self._split_states_by_state_name(
                r.states, RuntimeRecordStateEnum.UodCommandSet, include_prestart_states)
        elif isinstance(r.node, (p.AlarmNode, p.WatchNode)):
            # AwaitingCondition signifies the start of a new invocation for alarm and watch nodes
            split_states = self._split_states_by_state_name(
                r.states, RuntimeRecordStateEnum.AwaitingCondition, include_prestart_states)
        else:
            split_states = self._split_states_by_state_name(
                r.states, RuntimeRecordStateEnum.Started, include_prestart_states)

        return split_states

    def _split_states_by_state_name(
            self,
            states: list[RuntimeRecordState],
            state_name: RuntimeRecordStateEnum,
            include_prestart_states: bool) -> list[list[RuntimeRecordState]]:
        if len(states) == 0:
            return []

        # we need ordered states. if we cannot assume this, we would need to sort them
        self._check_record_states_ordered(states)

        split_states: list[list[RuntimeRecordState]] = []
        cur_instance_states: list[RuntimeRecordState] = []
        start_state_indices = [i for i, st in enumerate(states) if st.state_name == state_name]
        for i, st in enumerate(states):
            if len(start_state_indices) > 0 and i < min(start_state_indices):  # before the first start state
                if include_prestart_states:
                    # these could be used to produce a meta/root item for the invocation items
                    cur_instance_states.append(st)
            elif i in start_state_indices:  # at a start state
                if len(cur_instance_states) > 0:
                    split_states.append(cur_instance_states)
                cur_instance_states = [st]
            else:  # after a start state
                cur_instance_states.append(st)
        if len(cur_instance_states) > 0:
            split_states.append(cur_instance_states)
        return split_states

    def _check_record_states_ordered(self, states: list[RuntimeRecordState]):
        # temporarily verify that states are always ordered
        # if this is consistently the case, we can maybe ensure it as an invariant and remove the check
        for i, state in enumerate(states):
            if i > 0:
                prev_state = states[i-1]
                try:
                    assert prev_state.state_tick <= state.state_tick, "State tick out of order"
                    assert prev_state.state_time <= state.state_time, "State time out of order"
                except Exception:
                    raise

    def _update_item_progress(self, item: RunLogItem, source: EngineCommand | RuntimeRecord):
        if isinstance(source, EngineCommand):
            progress = source.get_progress()
            if isinstance(progress, float):
                item.progress = progress
            elif isinstance(progress, bool) and progress:
                item.progress = 0.5
            else:
                item.progress = None
        elif isinstance(source, RuntimeRecord):
            if isinstance(source.progress, float):
                item.progress = source.progress
            elif isinstance(source.progress, bool) and source.progress:
                item.progress = 0.5
            else:
                item.progress = None
        # logger.info(f"Updating progress to {item.progress}")

    def get_exec_record(self, exec_id: UUID) -> RuntimeRecord | None:
        """ Return record for the given exec_id or None if not found. """
        index = self._record_index.get(exec_id)
        if index is not None:
            return self._records[index]

    def get_command_and_record(self, command_exec_id: UUID) -> tuple[EngineCommand, RuntimeRecord] | None:
        """ Return (command, record) pair for the given command_exec_id or None if (both) not found. """
        for record in reversed(self.records):
            for state in record.states:
                if state.command_exec_id is not None and state.command_exec_id == command_exec_id:
                    if state.command is not None:
                        return state.command, record

    def get_last_node_record_or_none(self, node: p.Node) -> RuntimeRecord | None:
        for r in reversed(self._records):
            if r.node.id == node.id:
                return r

    def get_last_node_record(self, node: p.Node) -> RuntimeRecord:
        record = self.get_last_node_record_or_none(node)
        if record is None:
            raise ValueError("Node has no records")
        return record

    def get_node_records(self, node: p.Node, test_by_instance=False) -> list[RuntimeRecord]:
        """ Get the records that references the node.

        If test_by_instance is False (the default) references are tested by node id, otherwise
        references are tested by object reference. This is relevant when a method is edited while
        it runs, where nodes are replaced with new instances and these new instances must also
        be propagated to record node references.
        """
        if test_by_instance:
            return [r for r in self._records if r.node == node]
        else:
            return [r for r in self._records if r.node.id == node.id]

    def _add_record(self, record: RuntimeRecord, exec_id: UUID):
        index = len(self._records)
        self._records.append(record)
        self._record_index[exec_id] = index
        assert self._records[index].exec_id == exec_id
        self._last_exec_id = exec_id

    def begin_visit(
            self,
            node: p.Node,
            time: float, tick: int,
            start_values: TagValueCollection) -> RuntimeRecord:
        exec_id = uuid4()
        record = RuntimeRecord(node, exec_id=exec_id)
        record.visit_start_time = time
        record.visit_start_tick = tick
        record.start_values = start_values
        self._add_record(record, exec_id=exec_id)
        return record

    def find_instruction(
            self,
            instruction_name: str,
            arguments: str | None,
            start_index: int,
            instruction_state: RuntimeRecordStateEnum | None
            ) -> int | None:
        """ Find the first record with the given instruction name and state starting from start_index (incl).

        Return the index of the found record or None if record is not found.

        Use get_record_by_index to obtain the record of the index.
        """
        if start_index < 0:
            raise ValueError(f"start_index {start_index} is invalid")

        # create a copy to avoid race conditions cause by timer tick
        records_copy = self.records.copy()
        size = len(records_copy)
        if start_index > size - 1:
            return None

        for i in range(start_index, size):
            r = records_copy[i]
            if r.node.instruction_name == instruction_name:
                if arguments is None or r.node.arguments == arguments:
                    # logger.debug(f"Find record result: {i}, {instruction_name=}, {start_index=}")
                    # logger.debug(self.get_as_table())
                    if instruction_state is None:
                        return i
                    elif r.has_state(instruction_state):
                        return i

    def patch_node_references(self, program: p.ProgramNode):
        """ Patch node references to updated program nodes to account for edited method. """
        logger.info("Patching node references in runtime records")
        for r in self.records:
            if r.node is not None and not isinstance(r.node, p.ProgramNode):
                new_node = program.get_child_by_id(r.node.id)
                if new_node is None:
                    logger.error(f"No new node was found to replace {r.node}. Node cannot be patched")
                else:
                    if r.node != new_node:
                        r.node = new_node
                        logger.debug(f"Patched node reference {new_node}")
                    else:
                        logger.warning(f"Node not patched: {new_node} - old node already matched the new node!?")
        logger.info("Patching complete")

    def get_record_by_index(self, index: int) -> RuntimeRecord | None:
        if index < 0:
            raise ValueError(f"index {index} is invalid")
        records = self.records.copy()
        if index > len(records) - 1:
            return None
        else:
            return copy.copy(records[index])

    def get_as_table(self, description: str = "") -> str:
        records = self.records.copy()
        lines = [f"Runtime records: {description}"]
        lines.append("line | start | end   | runlog name          | node name            | states")
        lines.append("-----|-------|-------|----------------------|----------------------|-------------------")
        for r in records:
            name = f"{str(r.name):<20}" if r.name is not None else f"{str(r.node):<20}"
            node_name = f"{str(r.node.name):<20}" \
                if r.node.name is not None else "   -                  "
            line = f"{int(r.node.position.line):4d}" if r.node.position.line is not None else "   -"
            states = ", ".join([f"{st.state_name}: {st.state_tick}" for st in r.states])
            end = f"{r.visit_end_tick:5d}" if r.visit_end_tick != -1 else "    -"
            lines.append(f"{line}   {r.visit_start_tick:5d}   {end}   {name}   {node_name}   {states}")
        lines.append("-----|-------|-------|----------------------|----------------------|-------------------")
        return "\n".join(lines)

    def print_as_table(self, description: str = ""):
        print(self.get_as_table(description))

class RuntimeRecord:
    def __init__(self, node: p.Node, exec_id: UUID) -> None:
        self.exec_id: UUID = exec_id
        self.node = node
        self.name = node.runlog_name
        self.visit_start_time: float = -1.0
        self.visit_start_tick: int = -1
        self.visit_end_time: float = -1.0
        self.visit_end_tick: int = -1

        self.states: list[RuntimeRecordState] = []
        self.start_values: TagValueCollection | None = None
        self.end_values: TagValueCollection | None = None

        self.progress: float | None = None
        """ Used for progress for interpreter commands that don't have an command instance """

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(name="{self.name}")'

    @staticmethod
    def null_record() -> RuntimeRecord:
        # Returns a Null Object value that can be used when a real value is not available
        return RuntimeRecord(p.Node(), exec_id=uuid4())

    def __repr__(self) -> str:
        return f"{self.name} | States: {', '.join([str(st) for st in self.states])}"

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

    def add_state_started(self, time: float, tick: int, start_values: TagValueCollection):
        self.add_state(RuntimeRecordStateEnum.Started, time, tick, start_values)

    def add_state_completed(self, time: float, tick: int, end_values: TagValueCollection):
        self.add_state(RuntimeRecordStateEnum.Completed, time, tick, end_values)

    def add_state_failed(self, time: float, tick: int, end_values: TagValueCollection):
        self.add_state(RuntimeRecordStateEnum.Failed, time, tick, end_values)

    def add_state_cancelled(self, time: float, tick: int, state_values: TagValueCollection | None):
        self.add_state(RuntimeRecordStateEnum.Cancelled, time, tick, state_values)

    def add_state_forced(self, time: float, tick: int, state_values: TagValueCollection | None):
        self.add_state(RuntimeRecordStateEnum.Forced, time, tick, state_values)

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

    def add_state_internal_engine_command_set(
            self, command: EngineCommand,
            time: float, tick: int,
            state_values: TagValueCollection | None) -> UUID:
        state = self.add_state(RuntimeRecordStateEnum.InternalEngineCommandSet, time, tick, state_values)
        state.command = command
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


class RuntimeRecordState:
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
        return f'{self.__class__.__name__}(state_name="{self.state_name}")'

    def __repr__(self):
        return self.__str__()


class RuntimeRecordStateEnum(StrEnum):
    """ Defines the states runtime records can take """

    Visited = auto()
    """ Instruction node was visited"""
    UodCommandSet = auto()
    """ Uod command was set """
    InternalEngineCommandSet = auto()
    """ Internal engine command was set """
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
    """ Waiting command was forcibly started by user """
    Completed = auto()
    """ Command has completed """
    Failed = auto()
    """ Command has failed """

    @staticmethod
    def has_value(value: str):
        """ Determine if enum has this string value defined. Case sensitive. """
        return hasattr(RuntimeRecordStateEnum, value)


class RunLog:
    def __init__(self) -> None:
        self.id: str = ""
        self.items: list[RunLogItem] = []

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(id="{self.id}", items={self.items})'

    def size(self) -> int:
        return len(self.items)


class RunLogItem:
    def __init__(self) -> None:
        self.id: str = ""
        """ Exec_id of the command """
        self.name: str = ""
        self.start: float = 0
        self.end: float | None = None
        self.state: RunLogItemState = RunLogItemState.Unknown
        self.progress: float | None = None
        self.start_values: TagValueCollection = TagValueCollection.empty()
        self.end_values: TagValueCollection = TagValueCollection.empty()
        self.forcible: bool = False
        self.forced: bool = False
        self.cancellable: bool = False
        self.cancelled: bool = False

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(name="{self.name}")'


class RunLogItemState(StrEnum):
    """ Defines the states that commands in the run log can take """

    Unknown = auto()
    """ State unknown. Items in this state are not rendered. """
    AwaitingThreshold = auto()
    """ Waiting for threshold. Items in this state are not rendered """
    Started = auto()
    """ Command has started """
    Cancelled = auto()
    """ Command was cancelled. Either by overlapping command or explicitly by user """
    Forced = auto()
    """ Waiting command was forcibly started by user """
    Completed = auto()
    """ Command has completed """
    Failed = auto()
    """ Command failed """

    @staticmethod
    def has_value(value: str):
        """ Determine if enum has this string value defined. Case sensitive. """
        return hasattr(RunLogItemState, value)
