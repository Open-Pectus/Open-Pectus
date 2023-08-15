from __future__ import annotations
from enum import Enum
import logging
import time
import pint
import inspect
from typing import Generator, List, Tuple
from typing_extensions import override

from openpectus.lang.model.pprogram import (
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
    TagCollection,
    DEFAULT_TAG_BLOCK_TIME,
    DEFAULT_TAG_RUN_TIME,
)


logging.basicConfig(format=' %(name)s :: %(levelname)-8s :: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# TODO define pause + hold behavior
# TODO add Alarm interpretation, including scope definition


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


class ActivationRecord:
    # TODO do we need tags here? Is Base global?
    def __init__(
        self, owner: PNode, start_time: float, start_tags: TagCollection
    ) -> None:
        self.owner: PNode = owner
        self.start_time: float = start_time
        self.start_tags = start_tags
        self.complete: bool = False
        self.artype: ARType = self._get_artype(owner)

    def _get_artype(self, node: PNode) -> ARType:
        if isinstance(node, PProgram):
            return ARType.PROGRAM
        elif isinstance(node, PBlock):
            return ARType.BLOCK
        elif isinstance(node, PWatch):
            return ARType.WATCH
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

    def schedule_execution(self, name: str, args: str) -> None:
        raise NotImplementedError()


GenerationType = Generator[None, None, None] | None


class PInterpreter(PNodeVisitor):
    def __init__(self, program: PProgram, context: InterpreterContext) -> None:
        self._program = program
        self.context = context
        self.logs: List[LogEntry] = []
        self.pause_node: PNode | None = None
        self.stack: CallStack = CallStack()
        self.interrupts: List[Tuple[ActivationRecord, GenerationType]] = []
        self.running: bool = False

        self.start_time: float = 0
        self.tick_time: float = 0

        self.process_instr: GenerationType = None

    def get_marks(self) -> List[str]:
        return [x.message for x in self.logs if x.message[0] != 'P']

    def _interpret(self) -> GenerationType:
        """ Create generator for interpreting the main program. """
        self.running = True
        tree = self._program
        if tree is None:
            return None
        yield from self.visit(tree)

    def _add_to_log(self, _time: float, unit_time: float | None, message: str):
        self.logs.append(LogEntry(
            time=_time,
            unit_time=unit_time,
            message=message)
        )

    def _update_tags(self):
        # TODO move to ExecutionEngine
        # Engine has no concept of scopes - or at least only program and current block.
        # What about intermediate blocks/scopes?
        # Does this relate to RunLog? Should that show intermediate scope times?
        if self.stack.any():
            ar_program = self.stack.records[0]
            program_elapsed = self.tick_time - ar_program.start_time
            q_program = pint.Quantity(f'{program_elapsed} sec')
            self.context.tags.get(DEFAULT_TAG_RUN_TIME).set_quantity(q_program)

            ar_block = self.stack.peek()
            # TODO block time should not include pause and hold time
            block_elapsed = self.tick_time - ar_block.start_time
            q_block = pint.Quantity(f'{block_elapsed} sec')
            self.context.tags.get(DEFAULT_TAG_BLOCK_TIME).set_quantity(q_block)

            # TODO implement remaining tags, e.g. SYSTEM STATE, RUN COUNTER

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
            if isinstance(node, PWatch):
                logger.debug(f"Interrupt {str(node)}")
                try:
                    assert handler is not None, "Handler is None"
                    next(handler)
                    instr_count += 1
                except StopIteration:
                    pass
                if ar.complete:
                    self._unregister_interrupt(ar)
            else:
                logger.error(f"Interrupt for node type {str(node)} not implemented")
                raise NotImplementedError(f"Interrupt for node type {str(node)} not implemented")
        return instr_count > 0

    def tick(self, tick_time: float):
        self.tick_time = tick_time

        logger.debug("Tick")

        if self.process_instr is None:
            self.process_instr = self._interpret()

        program_end = False
        interrupt_end = False

        # update interpreter tags
        self._update_tags()

        # TODO read uod.tags

        assert self.process_instr is not None, "self.process_instr is None"
        try:
            next(self.process_instr)
        except StopIteration:
            program_end = True
        except Exception:
            logger.error("Interpretation error", exc_info=True)
            self.pause()

        try:
            work_done = self._run_interrupt_handlers()
            if not work_done:
                interrupt_end = True
        except Exception:
            logger.error("Interpretation interrupt error", exc_info=True)
            self.pause()

        # TODO write uod.tags

        if program_end and interrupt_end:
            logger.info("Interpretation complete. Stopping")
            self.stop()

    def stop(self):
        self.running = False

    def pause(self):
        # TODO define pause behavior
        self.running = False

    def hold(self):
        # TODO define hold behavior
        pass

    def _is_awaiting_threshold(self, node: PNode):
        if isinstance(node, PInstruction) and node.time is not None:
            block_elapsed = self.context.tags.get(DEFAULT_TAG_BLOCK_TIME).as_quantity()
            time_quantity = pint.Quantity(node.time, "sec")
            if block_elapsed < time_quantity:
                logger.debug(f"Awaiting threshold: {time_quantity}, current: {block_elapsed}, time: {self.tick_time}")
                return True
            logger.debug(f"Done awaiting time: {self.tick_time}")
        return False

    def _evaluate_condition(self, condition_node: PWatch | PAlarm) -> bool:
        c = condition_node.condition
        assert c is not None, "Error in condition"
        assert not c.error, "Error parsing condition"
        assert c.tag_name, "Error in condition tag"
        assert c.tag_value, "Error in condition value"
        assert self.context.tags.has(c.tag_name)
        tag = self.context.tags.get(c.tag_name)
        tag_value = tag.as_quantity()
        # TODO if not unit specified, pick base unit
        expected_value = pint.Quantity(c.tag_value_numeric, c.tag_unit)
        if not tag_value.is_compatible_with(expected_value):
            logger.error("Incompatible units")
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

        # log all visits
        logger.debug(f"Visiting {node} at tick {self.tick_time}")

        # possibly wait for node threshold to expire
        while self._is_awaiting_threshold(node):
            yield

        # delegate to concrete visitor via base method
        result = super().visit(node)

        # allow visit methods to be non generators
        if inspect.isgenerator(result):
            yield from result
        else:
            yield

        logger.debug(f"Visit {node} done")

    def visit_PProgram(self, node: PProgram):
        self._add_to_log(time.time(), time.time(), "PProgram")
        ar = ActivationRecord(node, self.tick_time, TagCollection.create_system_tags())
        self.stack.push(ar)
        yield from self._visit_children(node.children)
        self.stack.pop()

    def visit_PBlank(self, node: PBlank):
        pass

    def visit_PMark(self, node: PMark):
        self._add_to_log(time.time(), node.time, node.name)
        logger.info(f"Mark {str(node)}")

    def visit_PBlock(self, node: PBlock):
        ar = ActivationRecord(node, self.tick_time, TagCollection.create_system_tags())
        self.stack.push(ar)

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

    def visit_PEndBlock(self, node: PEndBlock):
        for ar in reversed(self.stack.records):
            if ar.artype == ARType.BLOCK:
                ar.complete = True
                return
        logger.warning("End block found no block to end")

    def visit_PCommand(self, node: PCommand):
        try:
            # TODO commands can be resident and last multiple ticks
            # see example command ?
            logger.debug(f"Executing command {str(node)}")
            self.context.schedule_execution(node.name, node.args)
        except Exception:
            logger.error(f"Command {node.name} failed", exc_info=True)
        yield

        # TODO determine whether command is complete...

    def visit_PWatch(self, node: PWatch):
        def create_interrupt_handler(ar: ActivationRecord) -> GenerationType:
            # TODO will this work with nested interrupt handlers,
            # possibly including blocks?
            self.stack.push(ar)
            yield from self.visit_PWatch(node)
            self.stack.pop()

        ar = self.stack.peek()
        if ar.owner is not node:
            # TODO the ar gets the creation tick time. Is this correct?
            ar = ActivationRecord(node, self.tick_time, TagCollection.create_system_tags())
            self._register_interrupt(ar, create_interrupt_handler(ar))
        else:
            logger.debug(f"{str(node)} interrupt invoked")
            if node.activated:
                condition_result = True
                logger.debug(f"{str(node)} was previously activated")
            else:
                while not ar.complete and self.running:
                    condition_result = self._evaluate_condition(node)
                    logger.debug(f"{str(node)} condition evaluated: {condition_result}")
                    if condition_result:
                        node.activated = True
                        logger.debug(f"{str(node)} executing")
                        yield from self._visit_children(node.children)
                        logger.debug(f"{str(node)} executed")
                        ar.complete = True
                        logger.info(f"Interrupt complete {ar}")
                    else:
                        yield
