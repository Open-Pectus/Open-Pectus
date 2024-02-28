from __future__ import annotations
from enum import Enum
import logging
from uuid import UUID
import pint
import inspect
from typing import Generator, List, Tuple
from typing_extensions import override
from openpectus.lang.exec.commands import SystemCommandEnum
from openpectus.lang.exec.errors import InterpretationError
from openpectus.lang.exec.runlog import RuntimeInfo, RuntimeRecordStateEnum

from openpectus.lang.model.pprogram import (
    PErrorInstruction,
    PInjectedNode,
    PNode,
    PProgram,
    PInstruction,
    PBlank,
    PBlock,
    PEndBlock,
    # PEndBlocks,
    PWatch,
    PAlarm,
    PCommand,
    PMark,
)

from openpectus.lang.exec.tags import (
    BASE_VALID_UNITS,
    TagCollection,
    TagValueCollection,
    SystemTagName,
)


logger = logging.getLogger(__name__)


class PNodeVisitor:
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class ARType(Enum):
    PROGRAM = "PROGRAM",
    BLOCK = "BLOCK",
    WATCH = "WATCH",
    ALARM = "ALARM",
    INJECTED = "INJECTED",


class ActivationRecord:
    def __init__(
        self,
        owner: PNode,
        start_time: float = -1.0,
        start_tags: TagValueCollection = TagValueCollection.empty()
    ) -> None:
        self.owner: PNode = owner
        self.start_time: float = start_time
        self.start_tags = start_tags
        self.complete: bool = False
        self.artype: ARType = self._get_artype(owner)

    def fill_start(self, start_time: float, start_tags: TagValueCollection):
        self.start_time: float = start_time
        self.start_tags = start_tags

    def _get_artype(self, node: PNode) -> ARType:
        if isinstance(node, PProgram):
            return ARType.PROGRAM
        elif isinstance(node, PBlock):
            return ARType.BLOCK
        elif isinstance(node, PWatch):
            return ARType.WATCH
        elif isinstance(node, PAlarm):
            return ARType.ALARM
        elif isinstance(node, PInjectedNode):
            return ARType.INJECTED
        else:
            raise NotImplementedError(f"ARType of node type '{type(node).__name__}' unknown")

    def __str__(self) -> str:
        return f"AR {self.owner} | {self.artype} | complete: {self.complete}"


class CallStack:
    def __init__(self):
        self._records = []

    @property
    def records(self) -> List[ActivationRecord]:
        return list(self._records)

    def push(self, ar: ActivationRecord):
        self._records.append(ar)

    def pop(self) -> ActivationRecord:
        return self._records.pop()

    def peek(self) -> ActivationRecord:
        return self._records[-1]

    def any(self) -> bool:
        return len(self._records) > 0

    def __str__(self):
        s = '\n'.join(repr(ar) for ar in reversed(self._records))
        s = f'CALL STACK\n{s}\n\n'
        return s

    def __repr__(self):
        return self.__str__()


class LogEntry():
    def __init__(self, time: float, unit_time: float | None = None, message: str = '') -> None:
        self.time: float = time
        self.unit_time: float | None = unit_time
        self.message: str = message


class InterpreterContext():
    """ Defines the context of program interpretation"""

    @property
    def tags(self) -> TagCollection:
        raise NotImplementedError()

    def schedule_execution(self, name: str, args: str | None = None, exec_id: UUID | None = None):
        raise NotImplementedError()


GenerationType = Generator[None, None, None] | None


class PInterpreter(PNodeVisitor):
    def __init__(self, program: PProgram, context: InterpreterContext) -> None:
        self._program = program
        self.context = context
        self.stack: CallStack = CallStack()
        self.interrupts: List[Tuple[ActivationRecord, GenerationType]] = []
        self.running: bool = False

        self.start_time: float = 0
        self._tick_time: float = 0
        self._tick_number: int = -1

        self.process_instr: GenerationType = None

        self.runtimeinfo: RuntimeInfo = RuntimeInfo()
        logger.info("Interpreter initialized")

    def get_marks(self) -> List[str]:
        records: list[tuple[str, int]] = []
        for r in self.runtimeinfo.records:
            if isinstance(r.node, PMark):
                completed_states = [st for st in r.states if st.state_name == RuntimeRecordStateEnum.Completed]
                for completed_state in completed_states:
                    end_tick = completed_state.state_tick
                    records.append((r.node.name, end_tick))

        def sort_fn(t: tuple[str, int]) -> int:
            return t[1]

        records.sort(key=sort_fn)
        return [t[0] for t in records]

    def inject_node(self, program: PProgram):
        """ Inject the node into the running program in the current scope to be executed as next instruction. """
        node = PInjectedNode(None)
        node.children = program.children
        ar = ActivationRecord(node, self._tick_time, self.context.tags.as_readonly())
        self._register_interrupt(ar, self._create_interrupt_handler(node, ar))

    def _interpret(self) -> GenerationType:
        """ Create generator for interpreting the main program. """
        self.running = True
        tree = self._program
        if tree is None:
            return None
        yield from self.visit(tree)

    def _update_tags(self):
        # Engine has no concept of scopes - or at least only program and current block.
        # What about intermediate blocks/scopes?
        # Does this relate to RunLog? Should that show intermediate scope times?

        # Clock         - seconds since epoch
        # Run Time      - 0 at start, increments when System State is not Stopped
        # Process Time  - 0 at start, increments when System State is Run
        # Block Time    - 0 at Block start, global but value refers to active block

        if self.stack.any():
            ar_program = self.stack.records[0]
            program_elapsed = self._tick_time - ar_program.start_time
            q_program = pint.Quantity(f'{program_elapsed} sec')
            self.context.tags.get(SystemTagName.RUN_TIME).set_quantity(q_program, self._tick_time)

            ar_block = self.stack.peek()
            # TODO block time should not include pause and hold time
            block_elapsed = self._tick_time - ar_block.start_time
            q_block = pint.Quantity(f'{block_elapsed} sec')
            self.context.tags.get(SystemTagName.BLOCK_TIME).set_quantity(q_block, self._tick_time)

    def _register_interrupt(self, ar: ActivationRecord, handler: GenerationType):
        logger.debug(f"Interrupt handler registered for {ar}")
        self.interrupts.append((ar, handler))

    def _unregister_interrupt(self, ar: ActivationRecord):
        pairs = list([(x, y) for (x, y) in self.interrupts if x is ar])
        for pair in pairs:
            self.interrupts.remove(pair)
            logger.debug(f"Interrupt handler unregistered for {ar}")

    def _run_interrupt_handlers(self):
        instr_count = 0
        for ar, handler in list(self.interrupts):
            logger.debug(f"Handler count: {len(self.interrupts)}")
            node = ar.owner
            if isinstance(node, (PWatch, PInjectedNode, PAlarm)):
                logger.debug(f"Interrupt {str(node)}")
                try:
                    assert handler is not None, "Handler is None"
                    next(handler)
                    instr_count += 1
                except StopIteration:
                    pass
                if ar.complete:
                    self._unregister_interrupt(ar)
                    if isinstance(node, PAlarm):
                        node.reset_state()
                        ar = ActivationRecord(node)
                        self._register_interrupt(ar, self._create_interrupt_handler(node, ar))
            else:
                logger.error(f"Interrupt for node type {str(node)} not implemented")
                raise NotImplementedError(f"Interrupt for node type {str(node)} not implemented")
        return instr_count > 0

    def _create_interrupt_handler(self, node: PNode, ar: ActivationRecord) -> GenerationType:
        ar.fill_start(self._tick_time, self.context.tags.as_readonly())
        self.stack.push(ar)
        yield from self.visit(node)
        self.stack.pop()

    def tick(self, tick_time: float, tick_number: int):
        self._tick_time = tick_time
        self._tick_number = tick_number

        logger.debug(f"Tick {self._tick_number}")

        if self.process_instr is None:
            self.process_instr = self._interpret()

        # update interpreter tags
        self._update_tags()

        # execute one iteration of program

        # TODO: be more clear about which errors to throw and which to handle
        # If there is no reason for interpreter to handle errors, might as well
        # just let engine do what it already does.
        # Also clarify which errors are expected (InterpretationError) and which are
        # unhandled (Exception)
        assert self.process_instr is not None, "self.process_instr is None"
        try:
            next(self.process_instr)
        except StopIteration:
            pass
        except Exception as ex:
            logger.error("Interpretation error", exc_info=True)
            raise InterpretationError("Interpreter error", ex)

        # execute one iteration of each interrupt
        try:
            work_done = self._run_interrupt_handlers()
            if not work_done:
                pass
        except Exception as ex:
            logger.error("Interpretation interrupt error", exc_info=True)
            raise InterpretationError("Interpreter error", ex)

    def stop(self):
        self.running = False
        self._program.reset_state()

    def _is_awaiting_threshold(self, node: PNode):
        if isinstance(node, PInstruction) and node.time is not None:
            block_elapsed = self.context.tags.get(SystemTagName.BLOCK_TIME).as_quantity()
            base_unit = self.context.tags.get(SystemTagName.BASE).get_value()
            assert isinstance(base_unit, str), \
                f"Base tag value must contain the base unit as a string. But its current value is '{base_unit}'"
            threshold_quantity = pint.Quantity(node.time, base_unit)
            if block_elapsed < threshold_quantity:
                logger.debug(f"Awaiting threshold: {threshold_quantity}, current: {block_elapsed}, time: {self._tick_time}")
                return True
            logger.debug(f"Done awaiting threshold {threshold_quantity} @ tick time: {self._tick_time}")
        return False

    def _evaluate_condition(self, condition_node: PWatch | PAlarm) -> bool:
        # TODO: improve error reporting. Even though these errors are caught by analyzers
        # they can still turn up here so we must report them faithfully for the user to handle
        c = condition_node.condition
        assert c is not None, "Error in condition"
        assert not c.error, f"Error parsing condition '{c.condition_str}'"
        assert c.tag_name, "Error in condition tag"
        assert c.tag_value, "Error in condition value"
        assert self.context.tags.has(c.tag_name), f"Unknown tag '{c.tag_name}' in condition '{c.condition_str}'"
        tag = self.context.tags.get(c.tag_name)
        tag_value = tag.as_quantity()
        # TODO if not unit specified, pick base unit
        expected_value = pint.Quantity(c.tag_value_numeric, c.tag_unit)
        if not tag_value.is_compatible_with(expected_value):
            logger.error(f"Incompatible units for values {tag_value} vs {expected_value}")
            raise ValueError("Incompatible units")

        result = None
        try:
            match c.op:
                case '<':
                    result = tag_value < expected_value
                case '<=':
                    result = tag_value <= expected_value
                case '=' | '==':
                    result = tag_value == expected_value
                case '>':
                    result = tag_value > expected_value
                case '>=':
                    result = tag_value >= expected_value
                case '!=':
                    result = tag_value != expected_value
                case  _:
                    pass
        except TypeError:
            msg = "Conversion error for values {!r} and {!r}".format(tag_value, expected_value)
            logger.error(msg, exc_info=True)
            raise ValueError("Conversion error")

        if result is None:
            raise ValueError(f"Unsupported operation: '{c.op}'")

        return result  # type: ignore

    def _visit_children(self, children: List[PNode] | None):
        ar = self.stack.peek()
        if children is not None:
            for child in children:
                if ar.complete:
                    break
                yield from self.visit(child)

    # Visitor Impl

    @override
    def visit(self, node):
        if not self.running:
            return

        # interrupts are visited multiple times. make sure to only create
        # a new record on the first visit
        record = self.runtimeinfo.get_last_node_record_or_none(node)
        if record is None:
            record = self.runtimeinfo.begin_visit(
                node,
                self._tick_time, self._tick_number,
                self.context.tags.as_readonly())

        # log all visits
        logger.debug(f"Visiting {node} at tick {self._tick_time}")

        # possibly wait for node threshold to expire
        while self._is_awaiting_threshold(node):
            record.add_state_awaiting_threshold(
                self._tick_time, self._tick_number,
                self.context.tags.as_readonly())
            yield

        # delegate to concrete visitor via base method
        result = super().visit(node)

        # allow visit methods to be non generators
        if inspect.isgenerator(result):
            yield from result
        else:
            yield

        record.set_end_visit(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

        logger.debug(f"Visit {node} done")

    def visit_PProgram(self, node: PProgram):
        ar = ActivationRecord(node, self._tick_time, self.context.tags.as_readonly())
        self.stack.push(ar)
        yield from self._visit_children(node.children)
        self.stack.pop()

    def visit_PBlank(self, node: PBlank):
        pass

    def visit_PMark(self, node: PMark):
        record = self.runtimeinfo.get_last_node_record(node)

        logger.info(f"Mark {str(node)}")

        record.add_state_started(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())
        record.add_state_completed(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

        yield  # comment if we dont want mark to always consume a tick

    def visit_PBlock(self, node: PBlock):
        record = self.runtimeinfo.get_last_node_record(node)

        ar = ActivationRecord(node, self._tick_time, self.context.tags.as_readonly())
        self.stack.push(ar)

        yield  # comment if we dont want block to always consume a tick

        record.add_state_started(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

        yield from self._visit_children(node.children)

        if not ar.complete:
            logger.debug(f"Block {node.name} idle")
        while not ar.complete and self.running:
            yield

        # await possible interrupt using the stack
        while not self.stack.peek() is ar:
            yield

        # now it's safe to pop
        self.stack.pop()

        record.add_state_completed(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

    def visit_PEndBlock(self, node: PEndBlock):
        record = self.runtimeinfo.get_last_node_record(node)
        record.add_state_started(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())
        for ar in reversed(self.stack.records):
            if ar.artype == ARType.BLOCK:
                ar.complete = True
                record.add_state_completed(
                    self._tick_time, self._tick_number,
                    self.context.tags.as_readonly())
                return
        logger.warning("End block found no block to end")

    def execute_system_command(self, node: PCommand):
        record = self.runtimeinfo.get_last_node_record(node)
        record.add_state_started(self._tick_time, self._tick_number, self.context.tags.as_readonly())

        if node.name == SystemCommandEnum.BASE:
            if node.args not in BASE_VALID_UNITS:
                record.add_state_failed(self._tick_time, self._tick_number, self.context.tags.as_readonly())
                raise InterpretationError(f"Base instruction has invalid argument '{node.args}'. \
                                            Value must be one of {', '.join(BASE_VALID_UNITS)}")
            self.context.tags[SystemTagName.BASE].set_value(node.args, self._tick_time)

        elif node.name == SystemCommandEnum.INCREMENT_RUN_COUNTER:
            rc_value = self.context.tags[SystemTagName.RUN_COUNTER].as_number() + 1
            self.context.tags[SystemTagName.RUN_COUNTER].set_value(rc_value, self._tick_time)

        else:
            record.add_state_failed(self._tick_time, self._tick_number, self.context.tags.as_readonly())
            raise InterpretationError(f"System instruction '{node.name}' is not supported")

        record.add_state_completed(self._tick_time, self._tick_number, self.context.tags.as_readonly())

    def visit_PCommand(self, node: PCommand):
        if SystemCommandEnum.has_value(node.name):
            logger.debug(f"Executing command {str(node)} as system instruction")
            self.execute_system_command(node)
        else:
            record = self.runtimeinfo.get_last_node_record(node)

            # Note: Commands can be resident and last multiple ticks.
            # The context (Engine) keeps track of this and we just
            # move on to the next instruction when tick() is invoked.
            # We do, however, provide the execution id to the context
            # so that it can update the runtime record appropriately.
            try:
                logger.debug(f"Executing command '{str(node)}' via engine")
                self.context.schedule_execution(node.name, node.args, record.exec_id)
            except Exception:
                record.add_state_failed(
                    self._tick_time, self._tick_number,
                    self.context.tags.as_readonly())
                logger.error(f"Command {node.name} scheduling failed", exc_info=True)

        yield

    def visit_PWatch(self, node: PWatch):
        yield from self.visit_WatchOrAlarm(node)

    def visit_PAlarm(self, node: PAlarm):
        yield from self.visit_WatchOrAlarm(node)

    def visit_WatchOrAlarm(self, node: PWatch | PAlarm):
        record = self.runtimeinfo.get_last_node_record(node)

        ar = self.stack.peek()
        if ar.owner is not node:
            ar = ActivationRecord(node)
            self._register_interrupt(ar, self._create_interrupt_handler(node, ar))
            record.add_state_awaiting_interrupt(
                self._tick_time, self._tick_number,
                self.context.tags.as_readonly())
        else:
            # On subsequent visits (originating from the interrupt handler), we evaluate
            # the condition. When true, the node is 'activated' and its body will run
            logger.debug(f"{str(node)} interrupt invoked")
            if node.activated:
                logger.debug(f"{str(node)} was previously activated")
            else:
                record.add_state_awaiting_condition(
                    self._tick_time, self._tick_number,
                    self.context.tags.as_readonly())

                while not ar.complete and self.running:
                    condition_result = self._evaluate_condition(node)
                    logger.debug(f"{str(node)} condition evaluated: {condition_result}")
                    if condition_result:
                        node.activated = True
                        logger.debug(f"{str(node)} executing")
                        record.add_state_started(
                            self._tick_time, self._tick_number,
                            self.context.tags.as_readonly())

                        yield from self._visit_children(node.children)
                        logger.debug(f"{str(node)} executed")
                        ar.complete = True
                        record.add_state_completed(
                            self._tick_time, self._tick_number,
                            self.context.tags.as_readonly())

                        logger.info(f"Interrupt complete {ar}")
                    else:
                        yield

    def visit_PInjectedNode(self, node: PInjectedNode):
        record = self.runtimeinfo.get_last_node_record(node)

        ar = self.stack.peek()
        if ar.owner is node:
            logger.debug(f"{str(node)} injected interrupt invoked")
            record.add_state_started(
                self._tick_time, self._tick_number,
                self.context.tags.as_readonly()
            )
            while not ar.complete and self.running:
                logger.debug(f"{str(node)} executing")
                yield from self._visit_children(node.children)
                logger.debug(f"{str(node)} executed")
                ar.complete = True
                logger.info(f"Injected interrupt complete {ar}")
                record.add_state_completed(
                    self._tick_time, self._tick_number,
                    self.context.tags.as_readonly())
        else:
            logger.error("Injected node error. Stack unwind required?")
            record.add_state_failed(
                self._tick_time, self._tick_number,
                self.context.tags.as_readonly())

    def visit_PErrorInstruction(self, node: PErrorInstruction):
        record = self.runtimeinfo.get_last_node_record(node)

        logger.error(f"Invalid instruction: {str(node)}")

        record.add_state_started(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())
        record.add_state_failed(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

        raise InterpretationError(f"Invalid instruction {str(node)}")
