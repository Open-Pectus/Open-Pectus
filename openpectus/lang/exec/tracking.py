import logging
from typing import Callable
import uuid

from openpectus.engine.commands import EngineCommand
from openpectus.engine.models import EngineCommandEnum
from openpectus.lang.exec.commands import CommandRequest
from openpectus.lang.exec.runlog import RunLog, RuntimeInfo, RuntimeRecord, RuntimeRecordStateEnum
from openpectus.lang.exec.tags import TagValueCollection
import openpectus.lang.model.ast as p

logger = logging.getLogger(__name__)

class Tracking():
    """ Manages tracking . API replaces the runtimeinfo API """
    def __init__(self, runtimeinfo: RuntimeInfo, tags: TagValueCollection, node_accessor: Callable[[str], p.Node | None],
                 enabled: bool = False):
        self.runtimeinfo = runtimeinfo
        self.tags = tags
        self.node_accessor = node_accessor
        self.tick_time: float = 0.0
        self.tick_number: int = 0
        self.enabled = enabled
        logger.info(f"Tracking instance {id(self)} created")

    def tick(self, tick_time: float, tick_number: int):
        # tracking must have its own time because interpreter's
        # time is not always available

        self.tick_time = tick_time
        self.tick_number = tick_number

    def enable(self):
        logger.info("Tracking enabled")
        self.enabled = True

    def disable(self):
        logger.info("Tracking disabled")
        self.enabled = False

    @property
    def records(self):
        return self.runtimeinfo.records_filtered

    def get_runlog(self) -> RunLog:
        return self.runtimeinfo.get_runlog()

    def has_instance_id(self, instance_id: str) -> bool:
        return instance_id in self.runtimeinfo._instance_record_map.keys()

    def create_instance_id(self, name: str) -> str:
        """ Create an instance id for an invocation of instruction from outside the interpreter,
        like Start/Stop or ad-hoc commands requested from a frontend user via the aggregator.

        This causes a null node and matching record (and Created state) to be created which owns
        the states related to the instruction instance.
        """
        null_record, null_node = self.runtimeinfo.create_nulls(name)
        self.runtimeinfo._add_record(null_record)
        return self.create_node_instance_id(null_node)

    def create_node_instance_id(self, node: p.Node) -> str:
        """ Create an instance id for an invocation of the provided Node.

        This is the default way used by calls from interpreter which always have a node context.
        A 'Created' state is added to the record with the new instance_id
        """
        if not self.enabled and not self.silently_skip(node):
            logger.warning("Trying to create instance_id while tracking is disabled")

        instance_id = str(uuid.uuid4())
        record = self.runtimeinfo.get_record_by_node(node.id)
        if record is None:
            logger.error(f"Failed to create instance id because no record was found for node: {node}", stack_info=True)
        else:
            self._add_record_state(instance_id, record, RuntimeRecordStateEnum.Created)
        return instance_id

    def create_injected_node_records(self, node: p.InjectedNode):
        def register(node: p.Node):
            record = RuntimeRecord.from_node(node)
            self.runtimeinfo._injected_node_map[node.id] = node
            self.runtimeinfo._add_record(record)
        register(node)
        for child_node in node.get_child_nodes(recursive=True):
            register(child_node)

    def get_known_node_by_id(self, node_id: str) -> p.Node | None:
        if node_id in self.runtimeinfo._null_node_map.keys():
            return self.runtimeinfo._null_node_map[node_id]
        elif node_id in self.runtimeinfo._injected_node_map.keys():
            return self.runtimeinfo._injected_node_map[node_id]
        else:
            return self.node_accessor(node_id)

    def get_record_by_instance_id(self, instance_id: str) -> RuntimeRecord | None:
        return self.runtimeinfo.get_record_by_instance(instance_id)

    def get_record_by_instance(self, instance: CommandRequest | EngineCommand | p.Node) -> RuntimeRecord | None:
        match instance:
            case CommandRequest() as req:
                return self.runtimeinfo.get_record_by_instance(req.instance_id)
            case EngineCommand() as cmd:
                return self.runtimeinfo.get_record_by_instance(cmd.instance_id)
            case p.Node() as node:
                return self.runtimeinfo.get_record_by_node(node.id)

    def get_command(self, instance_id: str) -> EngineCommand | None:
        record = self.runtimeinfo.get_record_by_instance(instance_id)
        if record is not None:
            states = record.get_states_by_instance(instance_id)
            for state in states:
                if state.command is not None:
                    return state.command

    def mark_started(self, instance: CommandRequest | EngineCommand | p.Node):
        if self.silently_skip(instance):
            return
        record = self.get_record_by_instance(instance)
        if record is None:
            raise ValueError(f"Invalid {instance=}. No record found")
        node = self.get_known_node_by_id(record.node_id)
        if node is None:
            raise ValueError(f"Invalid record. Node '{record.node_id}' not found")
        instance_id = record.last_instance_id or self.create_node_instance_id(node)
        self._add_record_state(instance_id, record, RuntimeRecordStateEnum.Started)

    def mark_uod_command_started(self, command: EngineCommand):
        if self.silently_skip(command):
            return
        instance_id = command.instance_id
        record = self.runtimeinfo.get_record_by_instance(instance_id)
        if record is None:
            raise ValueError(f"Invalid {instance_id=}. No record found")
        self._add_record_state(instance_id, record, RuntimeRecordStateEnum.Started)
        self._add_record_state(instance_id, record, RuntimeRecordStateEnum.UodCommandSet, command=command)

    def mark_internal_command_started(self, command: EngineCommand):
        if self.silently_skip(command):
            return
        instance_id = command.instance_id
        record = self.runtimeinfo.get_record_by_instance(instance_id)
        if record is None:
            # hmm this may occur for an ad-hoc command...
            raise ValueError(f"Invalid {instance_id=}. No record found")
        self._add_record_state(instance_id, record, RuntimeRecordStateEnum.Started)
        self._add_record_state(instance_id, record, RuntimeRecordStateEnum.InternalEngineCommandSet, command=command)

    def mark_completed(self, instance: CommandRequest | EngineCommand | p.Node, update_node=True):
        if self.silently_skip(instance):
            return
        record = self.get_record_by_instance(instance)
        if record is None:
            raise ValueError(f"Invalid {instance=}. No record found")
        node = self.get_known_node_by_id(record.node_id)
        if node is None:
            raise ValueError(f"Invalid record. Node {record.node_id=} not found")
        instance_id = record.last_instance_id or self.create_node_instance_id(node)

        if update_node:
            node = self.get_known_node_by_id(record.node_id)
            if node is None:
                raise ValueError(f"Invalid node_id '{record.node_id}'. No matching record found")
            else:
                if not node.failed:
                    node.completed = True
        self._add_record_state(instance_id, record, RuntimeRecordStateEnum.Completed)

    def mark_failed(self, instance: CommandRequest | EngineCommand | p.Node, update_node=True):
        """ Track the instruction as failed and update record state and node accorrdingly. """
        if self.silently_skip(instance):
            return

        match instance:
            case CommandRequest() as req:
                instance_id = req.instance_id
                record = self.runtimeinfo.get_record_by_instance(instance_id)
            case EngineCommand() as cmd:
                instance_id = cmd.instance_id
                record = self.runtimeinfo.get_record_by_instance(instance_id)
            case p.Node() as node:
                record = self.runtimeinfo.get_record_by_node(node.id)
                if record is None:
                    raise ValueError(f"Invalid {instance}. No record found")
                if record.last_instance_id is None:
                    raise ValueError(f"Invalid {instance}. No instances found")
                instance_id = record.last_instance_id

        if record is None:
            raise ValueError(f"Invalid {instance}. No record found")
        if update_node:
            node = self.get_known_node_by_id(record.node_id)
            assert node is not None
            node.failed = True
        self._add_record_state(instance_id, record, RuntimeRecordStateEnum.Failed)

    def silently_skip(self, instance: CommandRequest | EngineCommand | p.Node) -> bool:
        # Start, Restart and Stop operate too early and late for the mark_* methods to work. But it
        # is safe to just skip them as these records are not used for the runlog.
        skip_command_names = [EngineCommandEnum.START, EngineCommandEnum.RESTART, EngineCommandEnum.STOP]
        command_name = ""
        match instance:
            case CommandRequest() as command_req:
                command_name = command_req.name
            case EngineCommand() as command:
                command_name = command.name
            case p.NullNode():
                command_name = instance.command_name
            case p.Node():
                command_name = str(instance)
            case _:
                logger.error(f"Invalid instance type: {type(instance)}")

        if command_name in skip_command_names:
            return True
        elif not self.enabled:
            logger.warning(f"Skipping non-skip command {command_name} because tracking was not enabled")
            return True
        return False

    def mark_cancelled(self, instance: CommandRequest | EngineCommand | p.Node, update_node=True):
        if self.silently_skip(instance):
            return
        record = self.get_record_by_instance(instance)
        if record is None:
            raise ValueError(f"Invalid {instance=}. No record found")
        node = instance if isinstance(instance, p.Node) else self.get_known_node_by_id(record.node_id)
        if node is None:
            raise ValueError(f"Invalid record. Node {record.node_id=} not found")
        if update_node:
            if not node.cancel():
                logger.error(f"Cancel failed for node {node}")
                raise ValueError(f"Cancel failed for node {node}")
            # TODO why was this here?
            # if not node.completed and not node.failed:
            #     node.completed = True
        instance_id = record.last_instance_id or self.create_node_instance_id(node)
        self._add_record_state(instance_id, record, RuntimeRecordStateEnum.Cancelled)

    def mark_forced(self, instance: CommandRequest | EngineCommand | p.Node, update_node=True):
        if self.silently_skip(instance):
            return
        record = self.get_record_by_instance(instance)
        if record is None:
            raise ValueError(f"Record not found {instance=}")
        node = self.get_known_node_by_id(record.node_id)
        if node is None:
            raise ValueError(f"Invalid record. Node not found {record.node_id=}")
        if update_node:
            if not node.force():
                logger.error(f"Force failed for node {node}")
                raise ValueError(f"Force failed for node {node}")
        instance_id = record.last_instance_id or self.create_node_instance_id(node)
        self._add_record_state(instance_id, record, RuntimeRecordStateEnum.Forced)

    def mark_awaiting_condition(self, node: p.Node):
        if self.silently_skip(node):
            return
        record = self.runtimeinfo.get_record_by_node(node.id)
        if record is None:
            raise ValueError(f"Invalid node {node}. No matching record found")
        instance_id = record.last_instance_id or self.create_node_instance_id(node)
        self._add_record_state(instance_id, record, RuntimeRecordStateEnum.AwaitingCondition)

    def mark_awaiting_threshold(self, node: p.Node):
        if self.silently_skip(node):
            return
        record = self.runtimeinfo.get_record_by_node(node.id)
        if record is None:
            raise ValueError(f"Invalid node {node}. No matching record found")
        instance_id = record.last_instance_id or self.create_node_instance_id(node)
        self._add_record_state(instance_id, record, RuntimeRecordStateEnum.AwaitingThreshold)

    def _add_record_state(self, instance_id: str, record: RuntimeRecord, state: RuntimeRecordStateEnum,
                          command: EngineCommand | None = None):
        """ Helper method to add record state using the interpreter's current time/tick and tag values """
        node = self.get_known_node_by_id(record.node_id)
        if node is None:
            raise ValueError(f"Invalid record node id {record.node_id}. No matching node found")

        if self.silently_skip(node):
            return

        if state in [RuntimeRecordStateEnum.Started, RuntimeRecordStateEnum.Completed, RuntimeRecordStateEnum.Failed]:
            state_values = self.tags
        else:
            state_values = None

        record._add_state(instance_id, state, self.tick_time, self.tick_number,
                          state_values=state_values, node=node, command=command)
        # logger.debug(f"Added tracking state, node: {node}, state: {state}, tick_number: {self.interpreter._tick_number}")
        info = self.runtimeinfo
        if instance_id not in info._instance_record_map.keys():
            index = info._node_record_map[record.node_id]
            info._instance_record_map[instance_id] = index
