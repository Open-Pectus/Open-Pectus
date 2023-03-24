from __future__ import annotations
from enum import Enum
import logging
import time
import pint
import inspect

from typing import Generator, List, Tuple
from typing_extensions import override
from lang.model.pprogram import (
    TimeExp,
    PNode,
    PProgram,
    PBlank,
    PBlock,
    PEndBlock,
    PEndBlocks,
    PWatch,
    PAlarm,
    PCommand,
    PMark,
)

from lang.exec.tags import (
    TagCollection,
    DEFAULT_TAG_BLOCK_TIME,
    DEFAULT_TAG_RUN_TIME,
)
from lang.exec.uod import UnitOperationDefinitionBase
from lang.exec.timer import OneThreadTimer


logging.basicConfig(format=' %(name)s :: %(levelname)-8s :: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


TICK_INTERVAL = 0.1

# TODO add Alarm interpretation, including scope definition
# TODO add timings (depends on units)
# TODO condition expressions when defined in grammar
# TODO validate condition expression identifiers against known tags
# TODO if tags have an SI unit, validate the unit against that, eg. 'Watch: TT01 > 50 degC'


class PNodeVisitor:
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class SemanticAnalyzer(PNodeVisitor):
    def visit_PProgram(self, node: PProgram):
        print("program")
        if node.children is not None:
            for child in node.children:
                self.visit(child)

    def visit_PBlank(self, node: PBlank):
        print("blank")

    def visit_PMark(self, node: PMark):
        print("mark: " + node.name)


class ARType(Enum):
    PROGRAM = "PROGRAM",
    BLOCK = "BLOCK",
    WATCH = "WATCH",


class ActivationRecord:
    def __init__(
        self, owner: PNode, start_time: float, start_tags: TagCollection
    ) -> None:
        self.owner = owner
        self.start_time = start_time
        self.start_tags = start_tags
        self.complete = False
        self.artype: ARType = self._get_artype(owner)

    def _get_artype(self, node: PNode):
        if isinstance(node, PProgram):
            return ARType.PROGRAM
        elif isinstance(node, PBlock):
            return ARType.BLOCK
        elif isinstance(node, PWatch):
            return ARType.WATCH
        else:
            raise NotImplementedError("ARType of node unknown")

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


class PInterpreter(PNodeVisitor):
    def __init__(self, program: PProgram, uod: UnitOperationDefinitionBase) -> None:
        self.tags: TagCollection = TagCollection.create_default()
        self._program = program
        self.uod = uod
        self.logs = []
        self.pause_node: PNode | None = None
        self.stack: CallStack = CallStack()
        self.interrupts: List[Tuple[ActivationRecord, Generator]] = []
        self.running: bool = False

        self.start_time: float = 0
        self.tick_time: float = 0
        self.ticks: int = 0
        self.max_ticks: int = -1

        self.process_instr: Generator | None = None
        self.timer = OneThreadTimer(TICK_INTERVAL, self.tick)

    def get_marks(self) -> List[str]:
        return [x["message"] for x in self.logs if x["message"][0] != 'P']

    def interpret(self) -> Generator:
        self.running = True
        tree = self._program
        if tree is None:
            return ''
        yield from self.visit(tree)

    def _add_to_log(self, _time, unit_time, message):
        self.logs.append({"time": _time, "unit_time": unit_time, "message": message})

    def _update_tags(self):
        if self.stack.any():
            ar_program = self.stack.records[0]
            program_elapsed = self.tick_time - ar_program.start_time
            q_program = pint.Quantity(f'{program_elapsed} sec')
            self.tags.get(DEFAULT_TAG_RUN_TIME).set_quantity(q_program)

            ar_block = self.stack.peek()
            # TODO block time should not include pause and hold time
            block_elapsed = self.tick_time - ar_block.start_time
            q_block = pint.Quantity(f'{block_elapsed} sec')
            self.tags.get(DEFAULT_TAG_BLOCK_TIME).set_quantity(q_block)

            # TODO implement remaining tags, e.g. SYSTEM STATE, RUN COUNTER

    def register_interrupt(self, ar: ActivationRecord, handler: Generator):
        logger.debug(f"Interrupt handler registered for {ar}")
        self.interrupts.append((ar, handler))

    def unregister_interrupt(self, ar: ActivationRecord):
        pairs = [(x, y) for (x, y) in self.interrupts if x is ar]
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
                    next(handler)
                    instr_count += 1
                except StopIteration:
                    pass
                if ar.complete:
                    self.unregister_interrupt(ar)
            else:
                logger.error(f"Interrupt for node type {str(node)} not implemented")
                raise NotImplementedError(f"Interrupt for node type {str(node)} not implemented")
        return instr_count > 0

    def tick(self):
        self.ticks += 1
        self.tick_time = time.time()
        if self.max_ticks != -1 and self.ticks > self.max_ticks:
            logger.info(f"Stopping because max_ticks {self.max_ticks} was reached")
            self.running = False
            self.timer.stop()
            return
        logger.debug("Tick")

        if self.process_instr is None:
            self.process_instr = self.interpret()

        program_end = False
        interrupt_end = False

        # update interpreter tags
        self._update_tags()

        # TODO read uod.tags

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
        self.timer.stop()

    def pause(self):
        # TODO define pause behavior
        self.running = False

    def run(self, max_ticks=-1):
        logger.info("Interpretation started")
        self.ticks = 0
        self.max_ticks = max_ticks
        self.running = True
        self.timer.start()

        while self.running:
            time.sleep(0.1)

    def _evaluate_condition(self, condition_node: PWatch | PAlarm) -> bool:
        # TODO Need condition expression definition and parsing for a proper implementation.
        # TODO implement assert as analyzer check
        # TODO implement unit compability as analyzer check
        c = condition_node.condition
        assert c is not None, "Error in condition"
        try:
            c.parse()
        except Exception:
            logger.error(f"Condition parse error: {str(condition_node)}", exc_info=True)
            return False

        assert c.tag_name, "Error in condition"
        tag_name = c.tag_name.upper()

        # TODO implement assert as analyzer check
        assert self.tags.has(tag_name) or self.uod.tags.has(tag_name)
        tag = self.tags.get(tag_name) if self.tags.has(tag_name) else self.uod.tags.get(tag_name)
        tag_value = tag.as_quantity()
        # TODO if not unit specified, pick base unit
        # TODO add analyzer check for unit compability
        expected_value = pint.Quantity(c.rhs)
        if not tag_value.is_compatible_with(expected_value):  # type: ignore
            logger.error("Incompatible units")
            raise ValueError("Incompatible units")

        # TODO consider pushing this to a condition.evaluate() method
        # but do we want ast nodes to depend on tags?
        match c.op:
            case '<':
                return tag_value < expected_value
            case '<=':
                return tag_value <= expected_value
            case '=' | '==':
                return tag_value == expected_value
            case '>':
                return tag_value > expected_value
            case '>=':
                return tag_value >= expected_value
            case '!=':
                return tag_value != expected_value
            case  _:
                raise ValueError(f"Unsupported operation: '{c.op}'")

    def visit_children(self, children: List[PNode] | None):
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

        # allow visit methods to be non generators
        result = super().visit(node)
        if inspect.isgenerator(result):
            yield from result
        else:
            yield

        logger.debug(f"Visit {node} done")

    def visit_PProgram(self, node: PProgram):
        ar = ActivationRecord(node, self.tick_time, TagCollection.create_default())
        self.stack.push(ar)
        yield from self.visit_children(node.children)
        self.stack.pop()

    def visit_PBlank(self, node: PBlank):
        pass

    def visit_PMark(self, node: PMark):
        self._add_to_log(time.time(), node.time, node.name)
        logger.info(f"Mark {str(node)}")

    def visit_PBlock(self, node: PBlock):
        ar = ActivationRecord(node, self.tick_time, TagCollection.create_default())
        self.stack.push(ar)

        yield from self.visit_children(node.children)

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
            self.uod.execute_command(node.name, node.args)
        except Exception:
            logger.error(f"Command {node.name} failed", exc_info=True)
        yield

        # TODO determine whether command is complete...

    def visit_PWatch(self, node: PWatch):
        def create_interrupt_handler(ar: ActivationRecord) -> Generator:
            self.stack.push(ar)
            yield from self.visit_PWatch(node)
            self.stack.pop()

        ar = self.stack.peek()
        if ar.owner is not node:
            ar = ActivationRecord(node, self.tick_time, TagCollection.create_default())            
            self.register_interrupt(ar, create_interrupt_handler(ar))            
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
                        yield from self.visit_children(node.children)
                        logger.debug(f"{str(node)} executed")
                        ar.complete = True
                        logger.info(f"Interrupt complete {ar}")
                    else:
                        yield
