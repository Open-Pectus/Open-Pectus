from __future__ import annotations

import inspect
import logging
from enum import Enum
from typing import Generator, Iterable
from uuid import UUID

from openpectus.lang.exec.events import EventEmitter
import openpectus.lang.exec.units as units
from openpectus.lang.exec.base_unit import BaseUnitProvider
from openpectus.lang.exec.commands import InterpreterCommandEnum
from openpectus.lang.exec.errors import (
    EngineError, InterpretationError, InterpretationInternalError, NodeInterpretationError
)
from openpectus.lang.exec.runlog import RuntimeInfo, RuntimeRecordStateEnum
from openpectus.lang.exec.tags import (
    TagCollection, SystemTagName,
)
from openpectus.lang.model.pprogram import (
    PCommandWithDuration,
    PComment,
    PErrorInstruction,
    PInjectedNode,
    PNode,
    PProgram,
    PInstruction,
    PBlank,
    PBlock,
    PEndBlock,
    PEndBlocks,
    PWatch,
    PAlarm,
    PMacro,
    PCallMacro,
    PCommand,
    PMark,
    PBatch,
)
from typing_extensions import override

logger = logging.getLogger(__name__)

term_uod = "Unit Operation Definition file."


def macro_calling_macro(node: PMacro, macros: dict[str, PMacro], name: str | None = None) -> list[str]:
    '''
    Recurse through macro to produce a path of calls it makes to other macros.
    This is used to identify if a macro will at some point call itself.
    '''
    name = name if name is not None else node.name
    assert node.children is not None
    for child in node.children:
        if isinstance(child, PCallMacro):
            if child.name == name:
                return [child.name]
            elif child.name in macros.keys():
                return [child.name] + macro_calling_macro(macros[child.name], macros, name)
    return []


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
    MACRO = "MACRO",
    INJECTED = "INJECTED",


class ActivationRecord:
    def __init__(
            self,
            owner: PNode,
            start_time: float = -1.0,
    ) -> None:
        self.owner: PNode = owner
        self.start_time: float = start_time
        self.complete: bool = False
        self.artype: ARType = self._get_artype(owner)

    def fill_start(self, start_time: float):
        self.start_time: float = start_time

    def _get_artype(self, node: PNode) -> ARType:
        if isinstance(node, PProgram):
            return ARType.PROGRAM
        elif isinstance(node, PBlock):
            return ARType.BLOCK
        elif isinstance(node, PWatch):
            return ARType.WATCH
        elif isinstance(node, PAlarm):
            return ARType.ALARM
        elif isinstance(node, PMacro):
            return ARType.MACRO
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
    def records(self) -> list[ActivationRecord]:
        return list(self._records)

    def iterate_from_top(self) -> Iterable[ActivationRecord]:
        for ar in reversed(self._records):
            yield ar

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

    def schedule_execution(self, name: str, exec_id: UUID | None = None, **kvargs):
        raise NotImplementedError()

    @property
    def emitter(self) -> EventEmitter:
        raise NotImplementedError()

    @property
    def base_unit_provider(self) -> BaseUnitProvider:
        raise NotImplementedError()


GenerationType = Generator[None, None, None] | None


class PInterpreter(PNodeVisitor):
    def __init__(self, program: PProgram, context: InterpreterContext) -> None:
        self._program = program
        self.context = context
        self.stack: CallStack = CallStack()
        self.interrupts: list[tuple[ActivationRecord, GenerationType]] = []
        self.macros: dict[str, PMacro] = dict()
        self.running: bool = False

        self.start_time: float = 0
        self._tick_time: float = 0
        self._tick_number: int = -1

        self.process_instr: GenerationType = None

        self.runtimeinfo: RuntimeInfo = RuntimeInfo()
        logger.debug("Interpreter initialized")

    def get_marks(self) -> list[str]:
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
        """ Inject the child nodes of program into the running program in the current scope
        to be executed as the next instruction. """
        node = PInjectedNode(None)
        node.children = program.children
        ar = ActivationRecord(node, self._tick_time)
        self._register_interrupt(ar, self._create_interrupt_handler(node, ar))

    def _interpret(self) -> GenerationType:
        """ Create generator for interpreting the main program. """
        self.running = True
        tree = self._program
        if tree is None:
            return None
        tree.reset_runtime_state(recursive=True)
        logger.info("Reset runtime state")
        yield from self.visit(tree)


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
                self.stack.push(ar)
                try:
                    assert handler is not None, "Handler is None"
                    next(handler)
                    instr_count += 1
                except StopIteration:
                    pass
                finally:
                    self.stack.pop()

                if ar.complete:
                    self._unregister_interrupt(ar)
                    if isinstance(node, PAlarm):
                        node.reset_runtime_state(recursive=True)
                        ar = ActivationRecord(node)
                        self._register_interrupt(ar, self._create_interrupt_handler(node, ar))
            else:
                raise NotImplementedError(f"Interrupt for node type {str(node)} not implemented")
        return instr_count > 0

    def _create_interrupt_handler(self, node: PNode, ar: ActivationRecord) -> GenerationType:
        ar.fill_start(self._tick_time)
        yield from self.visit(node)

    def tick(self, tick_time: float, tick_number: int):
        self._tick_time = tick_time
        self._tick_number = tick_number

        logger.debug(f"Tick {self._tick_number}")

        if self.process_instr is None:
            self.process_instr = self._interpret()

        # execute one iteration of program
        assert self.process_instr is not None, "self.process_instr is None"
        try:
            next(self.process_instr)
        except StopIteration:
            pass
        except AssertionError as ae:
            raise InterpretationError(message=str(ae), exception=ae)
        except (InterpretationInternalError, InterpretationError):
            raise
        except EngineError:  # a method call on context failed - engine will know what to do
            raise
        except Exception as ex:
            logger.error("Unhandled interpretation error", exc_info=True)
            raise InterpretationError("Interpreter error") from ex

        # execute one iteration of each interrupt
        try:
            work_done = self._run_interrupt_handlers()
            if not work_done:
                pass
        except AssertionError as ae:
            raise InterpretationError(message=str(ae), exception=ae)
        except (InterpretationInternalError, InterpretationError):
            logger.error("Interpreter error in interrupt handler", exc_info=True)
            raise
        except Exception as ex:
            logger.error("Unhandled interpretation error in interrupt handler", exc_info=True)
            raise InterpretationError("Interpreter error") from ex

    def stop(self):
        self.running = False
        self._program.reset_runtime_state(recursive=True)

    def _is_awaiting_threshold(self, node: PNode):
        if isinstance(node, PInstruction) and node.time is not None and not node.forced:
            base_unit = self.context.tags.get(SystemTagName.BASE).get_value()
            assert isinstance(base_unit, str), \
                f"Base tag value must contain the base unit as a string. But its current value is '{base_unit}'"
            unit_provider = self.context.base_unit_provider
            if not unit_provider.has(base_unit):
                raise NodeInterpretationError(node, f"Base unit error. The current base unit '{base_unit}' is \
                                              not registered in the {term_uod}")

            value_tag, block_value_tag = unit_provider.get_tags(base_unit)
            if not self.context.tags.has(value_tag):
                raise InterpretationInternalError(f"Threshold calculation error. The registered tag \
                                              '{value_tag}' for unit '{base_unit}' is currently unavailable")
            if not self.context.tags.has(block_value_tag):
                raise InterpretationInternalError(f"Threshold calculation error. The registered block tag \
                                              '{block_value_tag}' for unit '{base_unit}' is currently unavailable")

            value_tag, block_value_tag = self.context.tags[value_tag], self.context.tags[block_value_tag]
            is_in_block = self.context.tags[SystemTagName.BLOCK].get_value() not in [None, ""]

            threshold_value = str(node.time)
            threshold_unit = base_unit

            time_value = str(block_value_tag.get_value() if is_in_block else value_tag.get_value())
            time_unit = block_value_tag.unit if is_in_block else value_tag.unit

            try:
                # calculate result of 'value < threshold'
                result = units.compare_values(
                    '<', time_value, time_unit,
                    threshold_value, threshold_unit)
                if result:
                    logger.debug(
                        f"Node {node} is awaiting threshold: {threshold_value}, " +
                        f"current: {time_value}, base unit: '{base_unit}'")
                    return True

                logger.debug(
                    f"Node {node} is done awaiting threshold {threshold_value}, " +
                    f"current: {time_value}, base unit: '{base_unit}'")
            except Exception as ex:
                raise NodeInterpretationError(
                    node,
                    "Threshold comparison error. Failed to compare " +
                    f"value '{time_value}' to threshold '{threshold_value}'") from ex
        return False

    def _evaluate_condition(self, condition_node: PWatch | PAlarm) -> bool:
        c = condition_node.condition
        assert c is not None, "Error in condition"
        assert not c.error, f"Error parsing condition '{c.condition_str}'"
        assert c.tag_name, "Error in condition tag"
        assert c.tag_value, "Error in condition value"
        assert self.context.tags.has(c.tag_name), f"Unknown tag '{c.tag_name}' in condition '{c.condition_str}'"
        tag = self.context.tags.get(c.tag_name)
        tag_value, tag_unit = str(tag.get_value()), tag.unit
        # TODO: Possible enhancement: if no unit specified, pick base unit?
        expected_value, expected_unit = c.tag_value, c.tag_unit

        return units.compare_values(
            c.op,
            tag_value,
            tag_unit,
            expected_value,
            expected_unit)

    def _visit_children(self, children: list[PNode] | None):
        ar = self.stack.peek()
        if children is not None:
            for child in children:
                if ar.complete:
                    break
                yield from self.visit(child)

    # Visitor Impl

    @override
    def visit(self, node: PNode):
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
            if self.stack.peek().complete:
                logger.debug("Aborting threshold because parent block was complete")
                return

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
        ar = ActivationRecord(node, self._tick_time)
        self.stack.push(ar)
        yield from self._visit_children(node.children)
        # TODO consider awaiting uod command completion before emit_on_method_end
        self.context.emitter.emit_on_method_end()
        self.stack.pop()

    def visit_PBlank(self, node: PBlank):
        pass

    def visit_PMark(self, node: PMark):
        record = self.runtimeinfo.get_last_node_record(node)

        logger.info(f"Mark {str(node)}")

        try:
            mark_tag = self.context.tags.get("Mark")
            mark_tag.set_value(node.name, self._tick_time)
        except ValueError:
            logger.error("Failed to get Mark tag")

        record.add_state_started(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

        # we want this in but it breaks a lot of tests. we want to be able to manage that first
        # yield

        record.add_state_completed(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

    def visit_PBatch(self, node: PBatch):
        record = self.runtimeinfo.get_last_node_record(node)

        logger.info(f"Batch {str(node)}")

        try:
            batch_tag = self.context.tags.get("Batch Name")
            batch_tag.set_value(node.name, self._tick_time)
        except ValueError:
            logger.error("Failed to get Batch Name tag")

        record.add_state_started(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

        # we want this in but it breaks a lot of tests. we want to be able to manage that first
        # yield

        record.add_state_completed(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

    def visit_PMacro(self, node: PMacro):
        record = self.runtimeinfo.get_last_node_record(node)
        record.add_state_started(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())
        logger.info(f"Defining macro {node}")

        # Check if calling the macro will call the macro.
        # This would incur a cascade of macros which
        # is probably not intended.
        # Make a temporary dict of macros to which
        # this macro is added. This dict is only used
        # to try to determine if the macro will at some
        # point try to call itself.
        temporary_macros = self.macros.copy()
        temporary_macros[node.name] = node
        cascade = macro_calling_macro(node, temporary_macros)
        if cascade and node.name in cascade:
            record.add_state_cancelled(self._tick_time, self._tick_number, self.context.tags.as_readonly())
            if len(cascade) == 1:
                logger.warning(f'Macro "{node.name}" calls itself. This is not allowed.')
                raise NodeInterpretationError(node, f'Macro "{node.name}" calls itself. ' +
                                                    'Unfortunately, this is not allowed.')
            else:
                path = " which calls ".join(f'macro "{link}"' for link in cascade)
                logger.warning(f'Macro "{node.name}" calls itself by calling {path}. This is not allowed.')
                raise NodeInterpretationError(node, f'Macro "{node.name}" calls itself by calling {path}. ' +
                                                    'Unfortunately, this is not allowed.')

        if node.name in self.macros.keys():
            logger.warning(f'Re-defining macro with name "{node.name}"')
        self.macros[node.name] = node
        record.add_state_completed(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

    def visit_PCallMacro(self, node: PCallMacro):
        record = self.runtimeinfo.get_last_node_record(node)
        record.add_state_started(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

        if node.name not in self.macros.keys():
            logger.warning(f'No macro defined with name "{node.name}"')
            available_macros = "None"
            if len(self.macros.keys()):
                available_macros = ", ".join(f'"{macro}"' for macro in self.macros.keys())
            raise NodeInterpretationError(node, f'No macro defined with name "{node.name}". ' +
                                                f'Available macros: {available_macros}.')
            record.add_state_cancelled(self._tick_time, self._tick_number, self.context.tags.as_readonly())
            return

        macro_node = self.macros[node.name]
        ar = ActivationRecord(macro_node, self._tick_time)
        self.stack.push(ar)
        yield from self._visit_children(macro_node.children)
        self.stack.pop()

        record.add_state_completed(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

    def visit_PBlock(self, node: PBlock):
        record = self.runtimeinfo.get_last_node_record(node)

        ar = ActivationRecord(node, self._tick_time)
        self.stack.push(ar)
        self.context.tags[SystemTagName.BLOCK].set_value(node.name, self._tick_number)
        self.context.emitter.emit_on_block_start(node.name, self._tick_number)
        logger.debug(f"Block Tag set to {node.name}")

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

        # restore previous block name
        block_restored = False
        for ar in self.stack.iterate_from_top():
            if ar.artype == ARType.BLOCK:
                assert isinstance(ar.owner, PBlock)
                self.context.tags[SystemTagName.BLOCK].set_value(ar.owner.name, self._tick_number)
                self.context.emitter.emit_on_block_end(node.name, ar.owner.name, self._tick_number)
                logger.debug(f"Block Tag popped to {ar.owner.name}")
                block_restored = True
        if not block_restored:
            self.context.tags[SystemTagName.BLOCK].set_value(None, self._tick_number)
            self.context.emitter.emit_on_block_end(node.name, "", self._tick_number)
            logger.debug(f"Block Tag cleared from {node.name}")


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

    def visit_PEndBlocks(self, node: PEndBlocks):
        record = self.runtimeinfo.get_last_node_record(node)
        record.add_state_started(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())
        for ar in reversed(self.stack.records):
            if ar.artype == ARType.BLOCK:
                ar.complete = True
                logger.debug(f"EndBlocks ended block {ar.owner.display_name}")
        record.add_state_completed(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

    def execute_interpreter_command(self, node: PCommand):
        record = self.runtimeinfo.get_last_node_record(node)
        record.add_state_started(self._tick_time, self._tick_number, self.context.tags.as_readonly())

        if node.name == InterpreterCommandEnum.BASE:
            valid_units = self.context.base_unit_provider.get_units()
            if node.args is None or node.args not in valid_units:
                record.add_state_failed(self._tick_time, self._tick_number, self.context.tags.as_readonly())
                raise NodeInterpretationError(node, f"Base instruction has invalid argument '{node.args}'. \
                    Value must be one of {', '.join(valid_units)}")
            self.context.tags[SystemTagName.BASE].set_value(node.args, self._tick_time)

        elif node.name == InterpreterCommandEnum.INCREMENT_RUN_COUNTER:
            run_counter = self.context.tags[SystemTagName.RUN_COUNTER]
            rc_value = run_counter.as_number() + 1
            logger.debug(f"Run Counter incremented from {rc_value - 1} to {rc_value}")
            run_counter.set_value(rc_value, self._tick_time)

        elif node.name == InterpreterCommandEnum.RUN_COUNTER:
            try:
                new_value = int(node.args)
                logger.debug(f"Run Counter set to {new_value}")
                self.context.tags[SystemTagName.RUN_COUNTER].set_value(new_value, self._tick_time)
            except ValueError:
                raise NodeInterpretationError(node, f"Invalid argument '{node.args}'. Argument must be an integer")

        else:
            record.add_state_failed(self._tick_time, self._tick_number, self.context.tags.as_readonly())
            raise NodeInterpretationError(node, f"Interpreter command '{node.name}' is not supported")

        record.add_state_completed(self._tick_time, self._tick_number, self.context.tags.as_readonly())

    def visit_PCommand(self, node: PCommand):
        if InterpreterCommandEnum.has_value(node.name):
            logger.debug(f"Executing interpreter command {str(node)}")
            self.execute_interpreter_command(node)
        else:
            record = self.runtimeinfo.get_last_node_record(node)

            # Note: Commands can be resident and last multiple ticks.
            # The context (Engine) keeps track of this and we just
            # move on to the next instruction when tick() is invoked.
            # We do, however, provide the execution id to the context
            # so that it can update the runtime record appropriately.
            try:
                logger.debug(f"Executing command '{str(node)}' with args '{node.args}' via engine")
                self.context.schedule_execution(
                    name=node.name,
                    exec_id=record.exec_id,
                    unparsed_args=node.args)
            except Exception as ex:
                record.add_state_failed(
                    self._tick_time, self._tick_number,
                    self.context.tags.as_readonly())

                if isinstance(ex, EngineError):
                    raise
                else:
                    raise NodeInterpretationError(node, "Failed to pass command to engine") from ex

        yield

    def visit_PCommandWithDuration(self, node: PCommandWithDuration):
        record = self.runtimeinfo.get_last_node_record(node)

        if node.duration is not None and node.duration.error:
            record.add_state_failed(self._tick_time, self._tick_number, self.context.tags.as_readonly())
            raise NodeInterpretationError(node, "Parse error. Command duration not valid") from None
        try:
            logger.debug(f"Executing command '{str(node)}' via engine")
            if node.duration is None:
                self.context.schedule_execution(name=node.name, exec_id=record.exec_id)
            else:
                self.context.schedule_execution(
                    name=node.name,
                    exec_id=record.exec_id,
                    time=node.duration.time,
                    unit=node.duration.unit
                )
        except Exception as ex:
            record.add_state_failed(
                self._tick_time, self._tick_number,
                self.context.tags.as_readonly())
            raise NodeInterpretationError(node, "Failed to pass command to engine") from ex

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
                    condition_result = False
                    if node.cancelled:
                        record.add_state_cancelled(self._tick_time, self._tick_number, self.context.tags.as_readonly())
                        logger.info(f"Instruction {node} cancelled")
                        ar.complete = True
                        return
                    elif node.forced:
                        record.add_state_forced(self._tick_time, self._tick_number, self.context.tags.as_readonly())
                        logger.info(f"Instruction {node} forced")
                        condition_result = True
                    else:
                        try:
                            condition_result = self._evaluate_condition(node)
                        except AssertionError:
                            raise
                        except Exception as ex:
                            raise NodeInterpretationError(node, "Error evaluating condition: " + str(ex))
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

    def visit_PComment(self, node: PComment):
        pass

    def visit_PErrorInstruction(self, node: PErrorInstruction):
        record = self.runtimeinfo.get_last_node_record(node)

        logger.error(f"Invalid instruction: {str(node)}")

        record.add_state_started(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())
        record.add_state_failed(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

        raise NodeInterpretationError(node, f"Invalid instruction '{node.code}'")
