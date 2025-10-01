from __future__ import annotations

import copy
import logging
from enum import StrEnum, auto
import traceback
from typing import Dict
import uuid

from openpectus.engine.commands import EngineCommand
from openpectus.lang.exec.tags import TagValueCollection
from openpectus.lang.exec.uod import UodCommand
import openpectus.lang.model.ast as p


logger = logging.getLogger(__name__)


class NodeLight:
    def __init__(self, node: p.Node):
        self.id = node.id
        self.position = node.position
        self.name = node.name
        self.runlog_name = node.runlog_name
        self.instruction_name = node.instruction_name
        self.arguments = node.arguments
        self.cancellable = node.cancellable
        self.cancelled = node.cancelled
        self.forcible = node.forcible
        self.forced = node.forced
        self._class_name = node.__class__.__name__

    def __str__(self):
        return f"{self.__class__.__name__}(instruction_name='{self.instruction_name}', " + \
            f"arguments={self.arguments}, id='{self.id}', _class_name='{self._class_name}')"

    def __repr__(self):
        return self.__str__()

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

    def __init__(self) -> None:
        self._records: list[RuntimeRecord] = []
        self._node_record_map: Dict[str, int] = {}
        """ maps node id to record index """
        self._instance_record_map: Dict[str, int] = {}
        """ maps instance_id to record index """
        self._null_node_map: Dict[str, p.NullNode] = {}
        """ maps node id to NullNode """
        self._injected_node_map: Dict[str, p.Node] = {}
        """ maps node id to injected nodes """
        logger.info(f"RuntimeInfo instance {id(self)} created")

    def size(self):
        return len(self._records)

    def __str__(self) -> str:
        records = [str(record) for record in self.records]
        return f'{self.__class__.__name__}(records="{records}")'

    def create_nulls(self, name: str) -> tuple[RuntimeRecord, p.NullNode]:
        """ Returns a Null Object record that can be used when a real value is not available.
        In addition, a Null Object node is created and referenced by the record. This will be available
        from get_known_nodes...
        """
        node = p.NullNode(id=str(uuid.uuid4()))
        node.arguments = name
        self._null_node_map[node.id] = node
        return RuntimeRecord.from_node(node), node

    @property
    def records(self) -> list[RuntimeRecord]:
        return list(self._records)

    @property
    def records_filtered(self) -> list[RuntimeRecord]:
        return [r for r in self._records if not r.node._class_name == "NullNode"]

    def get_runlog(self) -> RunLog:
        """ Transmogrify the runtime records into the RunLog shape that clients
        understand.

        Notably, it removes records with no name and unscrambles uod states
        such that each invocation gets its own runlog item. This allows the client
        to force or cancel a particular command instance.
        """
        runlog = RunLog()
        runlog.id = self._get_runlog_id() or ""
        for r in self.records_filtered:
            try:
                items = self._get_record_runlog_items(r)
                runlog.items.extend(items)
            except Exception:
                logger.error(f"Failed to create runlog item for record {r}", exc_info=True)
                raise
        runlog.items.sort(key=lambda item: item.start)
        return runlog

    def _get_runlog_id(self) -> str | None:
        for r in self.records:
            if isinstance(r.node, p.ProgramNode):
                return str(r.node.id)

    def _get_record_runlog_items(self, r: RuntimeRecord) -> list[RunLogItem]:  # noqa C901
        if isinstance(r.node, (p.ProgramNode, p.BlankNode, p.CommentNode, p.InjectedNode)):
            return []
        if r.name is None:
            if isinstance(r.node, (p.ErrorInstructionNode)):
                return []
            node_name = str(r.node) if r.node is not None else "node is None"
            logger.error(f"Runtime record has empty name. node: {node_name}. Fix this error or add a rule exception.")
            return []
        if r.name == "Stop": # TODO use enum access
            return []

        items: list[RunLogItem] = []

        # Usually there is only a single start/complete state pair which is what is needed for a runlog item.
        # But, alas, alarms can be invoked any number of times for which all state information is placed in
        # the same runtime record. Therefore we need to expand these states into seperate run log items.
        # And because any node can be in a PAlarm body, this extends to all other nodes as well.
        split_states = self._split_states_by_instance_id(r)
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
                    # item.name = r.name  # TODO use state name from possibly more recent node
                    # item.id = state.instance_id
                    # item.state = RunLogItemState.Started  # TODO possibly improve - could also be Waiting
                    # item.start = state.state_time
                    # item.start_values = state.values or r.start_values or TagValueCollection.empty()
                    # item.cancellable = r.node.cancellable
                    # item.cancelled = r.node.cancelled
                    # item.forcible = r.node.forcible
                    # item.forced = r.node.forced
                    item.name = state.name
                    item.id = state.instance_id
                    item.state = RunLogItemState.Started  # TODO possibly improve - could also be Waiting                    
                    item.start = state.state_time
                    item.start_values = state.values or r.start_values or TagValueCollection.empty()

                if item is not None:
                    item.cancellable = state.cancellable
                    item.cancelled = state.cancelled
                    item.forcible = state.forcible
                    item.forced = state.forced

                if state.state_name == RuntimeRecordStateEnum.Completed:
                    assert item is not None
                    item.state = RunLogItemState.Completed
                elif state.state_name == RuntimeRecordStateEnum.Failed:
                    assert item is not None
                    item.state = RunLogItemState.Failed
                    item.cancelled = True  #W HACK just to demonstrate in frontend that another color is picked
                elif state.state_name == RuntimeRecordStateEnum.Cancelled:
                    assert item is not None
                    item.state = RunLogItemState.Cancelled
                    # item.cancelled = True
                    # item.cancellable = False
                elif state.state_name == RuntimeRecordStateEnum.Forced:
                    assert item is not None
                    item.state = RunLogItemState.Forced
                    # item.forced = True
                    # item.forcible = False
                elif state.state_name == RuntimeRecordStateEnum.UodCommandSet:
                    command = state.command
                elif state.state_name == RuntimeRecordStateEnum.InternalEngineCommandSet:
                    command = state.command
                elif state.state_name == RuntimeRecordStateEnum.AwaitingThreshold:
                    assert item is not None, f"Item for record {r} was unexpectedly None in state {state.state_name}. States: {invocation_states}"
                    item.state = RunLogItemState.AwaitingThreshold

                if not is_conclusive_state and item is not None:
                    # item.cancellable = r.node.cancellable
                    # item.forcible = r.node.forcible
                    if command is not None:
                        if isinstance(command, UodCommand):
                            item.cancellable = True  # Node.cancellable does not support uod commands
                        self._update_item_progress(item, command)
                    elif r.progress is not None:
                        self._update_item_progress(item, r)

                if is_conclusive_state:
                    assert item is not None
                    item.end = state.state_time
                    item.end_values = state.values or TagValueCollection.empty()
                    item.cancellable = False
                    item.forcible = False

                if not has_more_states or is_conclusive_state:
                    if item is not None and item.state not in [RunLogItemState.Unknown, RunLogItemState.AwaitingThreshold]:
                        items.append(item)
                        item = None
                        command = None

        return items

    def _split_states_by_instance_id(self, r: RuntimeRecord) -> list[list[RuntimeRecordState]]:
        """ Split a record's states into those of distint invocations."""
        states_map: dict[str, list[RuntimeRecordState]] = {}
        for st in r.states:
            if st.instance_id not in states_map.keys():
                states_map[st.instance_id] = [st]
            else:
                states_map[st.instance_id].append(st)
        split_states = [states_map[item] for item in states_map.keys()]
        return split_states

    def _split_states(self, r: RuntimeRecord, include_prestart_states: bool) -> list[list[RuntimeRecordState]]:
        """ Split a record's states into those of distint invocations."""
        if len(r.states) == 0:
            return []

        split_states: list[list[RuntimeRecordState]] = []

        # We should probably just split by instance_id now

        if r.has_state(RuntimeRecordStateEnum.UodCommandSet):
            # UodCommandSet signifies the start of a uod command invocation
            split_states = self._split_states_by_state_name(
                r.states, RuntimeRecordStateEnum.UodCommandSet, include_prestart_states)
        elif r.has_state(RuntimeRecordStateEnum.InternalEngineCommandSet):
            # UodCommandSet signifies the start of a uod command invocation
            split_states = self._split_states_by_state_name(
                r.states, RuntimeRecordStateEnum.InternalEngineCommandSet, include_prestart_states)
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

    def get_record_by_node(self, node_id: str) -> RuntimeRecord | None:
        """ Return record for the given exec_id or None if not found. """
        index = self._node_record_map.get(node_id)
        if index is not None:
            return self._records[index]

    def get_record_by_instance(self, instance_id: str) -> RuntimeRecord | None:
        index = self._instance_record_map.get(instance_id)
        if index is not None:
            if index < self.size():
                return self.records[index]
            logger.error(
                f"get_record_by_instance_id failed to find record {instance_id=} because its index was too large. " +
                f"{index=}, size={self.size()}"
            )

    def _add_record(self, record: RuntimeRecord):
        index = len(self._records)
        self._records.append(record)
        self._node_record_map[record.node_id] = index

    def begin_visit(
            self,
            node: p.Node,
            time: float, tick: int,
            start_values: TagValueCollection) -> RuntimeRecord:
        record = RuntimeRecord.from_node(node)
        record.visit_start_time = time
        record.visit_start_tick = tick
        record.start_values = start_values
        self._add_record(record)
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

    def find_command(
            self,
            command_name: str,
            arguments: str | None,
            start_index: int,
            instruction_state: RuntimeRecordStateEnum | None
            ) -> int | None:
        """ Find the first record with the given command name and state starting from start_index (incl).

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
            for command_state in [RuntimeRecordStateEnum.InternalEngineCommandSet, RuntimeRecordStateEnum.UodCommandSet]:
                state = r.get_state(command_state)
                if state is not None:
                    assert state.instruction_name is not None
                    if state.instruction_name == command_name:
                        if arguments is None or state.arguments == arguments:
                            # logger.debug(f"Find record result: {i}, {instruction_name=}, {start_index=}")
                            # logger.debug(self.get_as_table())
                            if instruction_state is None:
                                return i
                            elif r.has_state(instruction_state):
                                return i

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
        lines = [f"Runtime records | {description}"]
        lines.append("line | start | end   | runlog name          | node name            | states")
        lines.append("-----|-------|-------|----------------------|----------------------|-------------------")
        for r in records:
            name = f"{str(r.name):<20}" if r.name is not None else f"{str(r.node):<20}"
            node_name = f"{str(r.name):<20}" \
                if r.node.name is not None else "   -                  "
            line = f"{int(r.node.position.line):4d}" if r.node.position.line is not None else "   -"
            states = ", ".join([f"{st.state_name}: {st.state_tick}" for st in r.states])
            end = f"{r.visit_end_tick:5d}" if r.visit_end_tick != -1 else "    -"
            lines.append(f"{line}   {r.visit_start_tick:5d}   {end}   {name}   {node_name}   {states}")
        lines.append("-----|-------|-------|----------------------|----------------------|-------------------")
        return "\n".join(lines)

    def get_as_table_alt(self, description: str = "") -> str:
        records = self.records.copy()
        lines = [f"\nRuntime records | {description}"]
        lines.append("line | start | end   | runlog name          | node name            |")
        lines.append("-----|-------|-------|----------------------|----------------------|")
        for r in records:
            name = f"{str(r.name):<20}" if r.name is not None else f"{str(r.node):<20}"
            node_name = f"{str(r.name):<20}" \
                if r.node.name is not None else "   -                  "
            line = f"{int(r.node.position.line):4d}" if r.node.position.line is not None else "   -"
            end = f"{r.visit_end_tick:5d}" if r.visit_end_tick != -1 else "    -"
            lines.append(f"{line}   {r.visit_start_tick:5d}   {end}   {name}   {node_name}")
            for st in r.states:
                st_line = f"       {st.instance_id}  {st.state_name}  {st.state_tick}  {st.command}"
                lines.append(st_line)
        return "\n".join(lines)

    def print_as_table(self, description: str = ""):
        print(self.get_as_table(description))

    def with_edited_program(self, program: p.ProgramNode) -> RuntimeInfo:
        """ Return a deep copy with node references set to nodes in program. Does not
        modify any existing records.

        Note: Uses RuntimeRecordState.clone() which does not change command and command_exec_id.
        """
        instance = RuntimeInfo()
        for r in self.records:
            # clone record and add the clone
            record = r.with_edited_node(program)
            instance._add_record(record)
        return instance

class RuntimeRecord:
    def __init__(self, node: NodeLight) -> None:
        """ Create new node. This only happens in
        - RuntimeInfo.begin_visit() which creates and assigns a random value
        - null_record() which creates and assigns a random value
        - clone() / with_edited_node() which copy the existing value

        Name and runlog name is complex.
        Node values: (name, runlog_name, instruction_name, arguments, class)
        For engine commands:
            want name = 'Start', node: ('Start', 'NullNode', '', 'Start, ?)
        For interpreter command:
            Blank name == "", node: ("", "", "", "", NodeLight/BlankNode)
            Block name == "Block: A", node: ("A", "Block A", "Block", "A")



        Note: Changes to node fields must be mirrored in clone() and with_edited_program(). """
        self.node_id: str = node.id
        self.node: NodeLight = node
        self.name: str | None = node.runlog_name
        self.instruction_name = node.instruction_name
        self.arguments = node.arguments
        self.visit_start_time: float = -1.0
        self.visit_start_tick: int = -1
        self.visit_end_time: float = -1.0
        self.visit_end_tick: int = -1

        self.states: list[RuntimeRecordState] = []
        self.start_values: TagValueCollection | None = None
        self.end_values: TagValueCollection | None = None

        self.progress: float | None = None
        """ Used for progress for interpreter commands that don't have an command instance """

    @staticmethod
    def from_node(node: p.Node) -> RuntimeRecord:
        return RuntimeRecord(NodeLight(node))


    def __str__(self) -> str:
        return f'{self.__class__.__name__}(name="{self.name}, node_id={self.node_id}")'

    def __repr__(self) -> str:
        return f"{self.name or self.node._class_name} | States: {', '.join([str(st) for st in self.states])}"

    # -- regular state --

    def has_state(self, state: RuntimeRecordStateEnum) -> bool:
        return any([st for st in self.states if st.state_name == state])

    def get_state(self, state: RuntimeRecordStateEnum, first=True) -> RuntimeRecordState | None:
        states = [st for st in self.states if st.state_name == state]
        if len(states) == 0:
            return None
        elif first:
            return states[0]
        else:
            return states[-1]

    def get_states_by_instance(self, instance_id: str) -> list[RuntimeRecordState]:
        return [state for state in self.states if state.instance_id == instance_id]

    def _add_state(self,
                   instance_id: str,
                   state: RuntimeRecordStateEnum,
                   time: float, tick: int,
                   state_values: TagValueCollection | None,
                   node: p.Node,
                   command: EngineCommand | None = None
                   ):  # -> RuntimeRecordState:
        record_state = RuntimeRecordState(instance_id, state, time, tick, state_values)
        record_state.command = command
        record_state.update_from_node(node)

        if __debug__:
            #fail_on_duplicate = False
            fail_on_duplicate = True
            # check duplicate state for instance
            for st in self.states:
                if st.instance_id == instance_id and st.state_name == state:
                    logger.warning(f"Duplicate state '{state}' for instance {instance_id} in record {self}")
                    for line in traceback.format_stack():
                        print(line)
                    if fail_on_duplicate:
                        raise Exception(f"Failing because duplicate state '{state}' was encountered")

        self.states.append(record_state)

    @property
    def last_instance_id(self) -> str | None:
        """ Returns instance_id of the last state or None if the record has no states """
        if len(self.states) == 0:
            return None
        return self.states[-1].instance_id

    def set_end_visit(self, time: float, tick: int, end_values: TagValueCollection):
        self.visit_end_time = time
        self.visit_end_tick = tick
        self.end_values = end_values

    # -- command state --

    def clone(self) -> RuntimeRecord:
        instance = RuntimeRecord(self.node)

        instance.name = self.node.name
        instance.visit_start_time = self.visit_start_time
        instance.visit_start_tick = self.visit_start_tick
        instance.visit_end_time = self.visit_end_time
        instance.visit_end_tick = instance.visit_end_tick

        instance.states = [s.clone() for s in self.states]
        instance.start_values = None if self.start_values is None else self.start_values.clone()
        instance.end_values = None if self.end_values is None else self.end_values.clone()

        instance.progress = self.progress
        return instance


    def with_edited_node(self, program: p.ProgramNode) -> RuntimeRecord:
        """ Clones the record, updates the node to the matching node in the new program and returns the clone """
        instance = self.clone()
        if self.node.id != "":
            new_node = program.get_child_by_id(self.node.id)
            if new_node is None:
                if self.node._class_name == p.NullNode.__name__:
                    raise NotImplementedError(f"Failed to copy record for NullNode {self.node} - what to do?")
                else:
                    raise ValueError(f"Failed to copy record for node {self.node} - No new node available")
            else:
                instance.node = NodeLight(new_node)
        return instance

class RuntimeRecordState:
    def __init__(
            self,
            instance_id: str,
            state: RuntimeRecordStateEnum,
            time: float, tick: int,
            values: TagValueCollection | None
    ) -> None:
        self.instance_id: str = instance_id
        self.state_name: RuntimeRecordStateEnum = state
        self.state_time: float = time
        self.state_tick: int = tick
        self.values: TagValueCollection | None = values
        self.command: EngineCommand | None = None

        self.name: str = ""
        self.instruction_name: str = ""
        self.arguments: str = ""
        self.cancellable: bool = False
        self.cancelled: bool = False
        self.forcible: bool = False
        self.forced: bool = False

    def update_from_node(self, node: p.Node):
    #def update_from_node(self, node: NodeLight):
        """ Update the record state's values from node """
        self.name = node.runlog_name or node.name
        self.instruction_name = node.instruction_name
        self.arguments = node.arguments
        self.cancellable = node.cancellable
        self.cancelled = node.cancelled
        self.forcible = node.forcible
        self.forced = node.forced

        logger.warning(f"Updating state from node {self.cancellable=}, {self.cancelled=} | {self.forcible=}, {self.forced=}")

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(state_name="{self.state_name}, instance_id={self.instance_id}")'

    def __repr__(self):
        return self.__str__()

    def clone(self) -> RuntimeRecordState:
        """ Note: command and command_exec_id are copied from existing state. These reference
        command objects outside or RuntimeInfo. """
        values = None if self.values is None else self.values.clone()
        # TODO HMM - should we reuse instance_id's? 
        instance = RuntimeRecordState(self.instance_id, self.state_name, self.state_time, self.state_tick, values)
        instance.command = self.command
        instance.name = self.name
        instance.cancellable = self.cancellable
        instance.cancelled = self.cancelled
        instance.forcible = self.forcible
        instance.forced = self.forced
        return instance


class RuntimeRecordStateEnum(StrEnum):
    """ Defines the states runtime records can take """

    Created = auto()
    """ Instruction node was assigned instance_id """
    UodCommandSet = auto()
    """ Uod command was set """
    InternalEngineCommandSet = auto()
    """ Internal engine command was set """
    AwaitingThreshold = auto()
    """ Waiting for threshold """
    AwaitingCondition = auto()
    """ Waiting for condition """
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
        """ Instance id of the command """
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


def assert_Runlog_HasItem(runtimeinfo: RuntimeInfo, name: str):
    runlog = runtimeinfo.get_runlog()
    for item in runlog.items:
        if item.name == name:
            return
    item_names = [item.name for item in runlog.items]
    raise AssertionError(f"Runlog has no item named '{name}'. It has these names:  {','.join(item_names)}")

def assert_Runlog_HasNoItem(runtimeinfo: RuntimeInfo, name: str):
    runlog = runtimeinfo.get_runlog()
    item_names = [item.name for item in runlog.items]
    for item in runlog.items:
        if item.name == name:
            raise AssertionError(f"Runlog has item named '{name}' which was not expected. " +
                                 f"It has these names:  {','.join(item_names)}")

def assert_Runlog_HasItem_Started(runtimeinfo: RuntimeInfo, name: str):
    runlog = runtimeinfo.get_runlog()
    for item in runlog.items:
        if item.name == name and item.state == RunLogItemState.Started:
            return
    raise AssertionError(f"Runlog has no item named '{name}' in Started state")

def assert_Runlog_HasItem_Completed(runtimeinfo: RuntimeInfo, name: str, min_times=1):
    occurrences = 0
    runlog = runtimeinfo.get_runlog()
    for item in runlog.items:
        if item.name == name and item.state == RunLogItemState.Completed:
            occurrences += 1

    if occurrences < min_times:
        raise AssertionError(
            f"Runlog item named '{name}' did not occur in Completed state at least " +
            f"{min_times} time(s). It did occur {occurrences} time(s)")

def assert_Runtime_HasRecord(runtimeinfo: RuntimeInfo, name: str):
    for r in runtimeinfo.records:
        if r.name == name:
            return
    raise AssertionError(f"Runtime has no record named '{name}'")

def assert_Runtime_HasRecord_Started(runtimeinfo: RuntimeInfo, name: str):
    for r in runtimeinfo.records:
        if r.name == name and r.has_state(RuntimeRecordStateEnum.Started):
            return
    raise AssertionError(f"Runtime has no record named '{name}' in state Started")

def assert_Runtime_HasRecord_Completed(runtimeinfo: RuntimeInfo, name: str):
    for r in runtimeinfo.records:
        if r.name == name and r.has_state(RuntimeRecordStateEnum.Started):
            return
    raise AssertionError(f"Runtime has no record named '{name}' in state Completed")
