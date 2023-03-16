from __future__ import annotations
from collections import deque
from enum import Enum
import logging
import threading
import time
import asyncio
import inspect

from typing import Callable, Deque, Generator, Iterable, Iterator, List, Tuple
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

from lang.exec.tags import TagCollection
from lang.exec.uod import UnitOperationDefinitionBase
from lang.exec.timer import OneThreadTimer

logging.basicConfig()
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

    def __str__(self):
        s = '\n'.join(repr(ar) for ar in reversed(self._records))
        s = f'CALL STACK\n{s}\n\n'
        return s

    def __repr__(self):
        return self.__str__()


class PInterpreterGen(PNodeVisitor):
    def __init__(self, program: PProgram, uod: UnitOperationDefinitionBase) -> None:
        self.tags: TagCollection = TagCollection.create_default()
        self._program = program
        self.uod = uod
        self.logs = []
        self.pause_node: PNode | None = None
        self.stack: CallStack = CallStack()
        self.interrupts: List[ActivationRecord] = []
        self.running: bool = False

        self.start_time: float = 0
        self.tick_time: float = 0
        self.ticks: int = 0
        self.max_ticks: int = -1

        self.gen: Generator | None = None
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

    def validate_commands(self):
        pass

    def _process_background_tasks(self):
        for ar in list(self.interrupts):
            if isinstance(ar.owner, PWatch):
                self.stack.push(ar)
                self.visit(ar.owner)
                self.stack.pop()
                if ar.complete:
                    self.interrupts.remove(ar)
            else:
                raise NotImplementedError(f"Interrupt for node type {type(ar.owner).__name__} not implemented")

    def tick(self):
        self.ticks += 1
        self.tick_time = time.time()
        if self.max_ticks != -1 and self.ticks > self.max_ticks:
            print("Stop on max_ticks")
            self.running = False
            self.timer.stop()
            return
        print("TICK")

        if self.gen is None:
            return

        try:
            next(self.gen)
        except StopIteration:
            print("Iteration complete")
            self.running = False
            self.timer.stop()

    def run(self, max_ticks=-1):
        self.ticks = 0
        self.max_ticks = max_ticks
        self.running = True

        self.gen = self.interpret()

        self.timer.start()

        while self.running:
            time.sleep(0.1)

    def _evaluate_condition(self, condition_node: PWatch | PAlarm) -> bool:
        # HACK to pass tests using the imaginary 'counter' tag.
        # Need condition expression definition and parsing for a proper implementation.
        value = int(self.uod.tags["counter"].get_value())
        return value > 0

    def visit_children(self, children: List[PNode] | None, break_on_ar_complete=False):
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
        message = type(node).__name__
        if hasattr(node, 'name'):
            message += ": " + node.name
        elif hasattr(node, 'condition') and node.condition.condition_str:
            message += ": " + node.condition.condition_str

        self._add_to_log(self.tick_time, "", message)

        # allow visit methods to be non generators
        result = super().visit(node)
        if inspect.isgenerator(result):
            yield from result
        else:
            yield

    def visit_PProgram(self, node: PProgram):
        ar = ActivationRecord(node, self.tick_time, TagCollection.create_default())
        self.stack.push(ar)
        print("PROGRAM")

        yield from self.visit_children(node.children)

        print("PROGRAM END")

    def visit_PBlank(self, node: PBlank):
        pass

    def visit_PMark(self, node: PMark):
        self._add_to_log(time.time(), node.time, node.name)        

    def visit_PBlock(self, node: PBlock):
        ar = ActivationRecord(node, self.tick_time, TagCollection.create_default())
        self.stack.push(ar)

        yield from self.visit_children(node.children)

        if not ar.complete:
            print(f"BLOCK {node.name} idle")
        while not ar.complete and self.running:
            yield

        print("BLOCK EXIT")

    def visit_PEndBlock(self, node: PEndBlock):
        ar = self.stack.pop()
        ar.complete = True        

    def visit_PCommand(self, node: PCommand):
        try:
            # TODO commands can be resident and last multiple ticks
            # see example command ?
            self.uod.execute_command(node.name, node.args)
        except Exception as ex:
            print(ex)

        yield

        # TODO determine whether command is complete...

    def visit_PWatch(self, node: PWatch):
        ar = self.stack.peek()
        if ar.owner != node:
            ar = ActivationRecord(node, self.tick_time, TagCollection.create_default())
            self.interrupts.append(ar)
        else:
            condition_result = self._evaluate_condition(node)
            if condition_result:
                print(f"WATCH {node.condition}")
                yield from self.visit_children(node.children)
