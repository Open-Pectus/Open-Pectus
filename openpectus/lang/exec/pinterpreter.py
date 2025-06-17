from __future__ import annotations

import logging
from enum import Enum
from typing import Generator, Iterable
from uuid import UUID

from openpectus.lang.exec.argument_specification import ArgSpec
from openpectus.lang.exec.events import EventEmitter
from openpectus.lang.exec.regex import REGEX_DURATION, get_duration_end
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
from openpectus.lang.exec.visitor import NodeGenerator, NodeVisitor
import openpectus.lang.model.ast as p
from typing_extensions import override

logger = logging.getLogger(__name__)

term_uod = "Unit Operation Definition file."


def macro_calling_macro(node: p.MacroNode, macros: dict[str, p.MacroNode], name: str | None = None) -> list[str]:
    '''
    Recurse through macro to produce a path of calls it makes to other macros.
    This is used to identify if a macro will at some point call itself.
    '''
    name = name if name is not None else node.name
    assert node.children is not None
    for child in node.children:
        if isinstance(child, p.CallMacroNode):
            if child.name == name:
                return [child.name]
            elif child.name in macros.keys():
                return [child.name] + macro_calling_macro(macros[child.name], macros, name)
    return []


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
            owner: p.Node,
            start_time: float = -1.0,
    ) -> None:
        self.owner: p.Node = owner
        self.start_time: float = start_time
        self.complete: bool = False
        self.artype: ARType = self._get_artype(owner)

    def fill_start(self, start_time: float):
        self.start_time: float = start_time

    def _get_artype(self, node: p.Node) -> ARType:
        if isinstance(node, p.ProgramNode):
            return ARType.PROGRAM
        elif isinstance(node, p.BlockNode):
            return ARType.BLOCK
        elif isinstance(node, p.WatchNode):
            return ARType.WATCH
        elif isinstance(node, p.AlarmNode):
            return ARType.ALARM
        elif isinstance(node, p.MacroNode):
            return ARType.MACRO
        elif isinstance(node, p.InjectedNode):
            return ARType.INJECTED
        else:
            raise NotImplementedError(f"ARType of node type '{type(node).__name__}' unknown")

    def __str__(self) -> str:
        return f"AR {self.owner} | {self.artype} | complete: {self.complete}"

    def __repr__(self):
        return self.__str__()


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

    def find_by_owner_id(self, id: str) -> ActivationRecord | None:
        for r in self.iterate_from_top():
            if r.owner.id == id:
                return r

    def __str__(self):
        if len(self._records) == 0:
            return "CallStack (empty)"
        s = '\n\t'.join(repr(ar) for ar in reversed(self._records))
        s = f'CallStack (size: {len(self.records)})\n{s}\n\n'
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

    def schedule_execution(self, name: str, arguments: str = "", exec_id: UUID | None = None):
        raise NotImplementedError()

    @property
    def emitter(self) -> EventEmitter:
        raise NotImplementedError()

    @property
    def base_unit_provider(self) -> BaseUnitProvider:
        raise NotImplementedError()


GenerationType = Generator[None, None, None] | None


class PInterpreter(NodeVisitor):
    def __init__(self, program: p.ProgramNode, context: InterpreterContext) -> None:
        self._program = program
        self.context = context
        self.stack: CallStack = CallStack()
        self.interrupts: list[tuple[ActivationRecord, NodeGenerator]] = []
        self.macros: dict[str, p.MacroNode] = dict()
        self.running: bool = False

        self.start_time: float = 0
        self._tick_time: float = 0
        self._tick_number: int = -1

        self._process_instr: NodeGenerator | None = None

        self._ffw: bool = False
        self._ffw_target_node_id: str | None = None

        self.runtimeinfo: RuntimeInfo = RuntimeInfo()
        logger.debug("Interpreter initialized")


    def update_method_and_ffw(self, program: p.ProgramNode):
        """ Update method while method is running. """
        # set new program, and patch state to point to new nodes, set ffw and advance generator to get to where we were

        # collect node id from old method. The id will match the corresponding node in the new method
        if self._program.active_node is None:
            raise ValueError("Edit cannot be performed when no current node is set")
        # if self._program.active_node.started:
        #     raise ValueError(f"Active node {self._program.active_node} already started")
        target_node_id = self._program.active_node.id

        # patch runtimeinfo records to reference new nodes - before or after ffw? should not matter
        self.runtimeinfo.patch_node_references(program)
        self._patch_node_references(program)

        # verify that target is not completed - if so ffw won't find it
        self._program = program
        self._process_instr = None  # clear so either tick or us may set it
        target_node = program.get_child_by_id(target_node_id)  # find target node in new ast
        if target_node is None:
            logger.error(f"FFW aborted because target node {target_node_id} was not found in new ast")
            raise ValueError(
                f"Error modifying method. The target node_id {target_node_id} was not found in the updated method.")
        elif target_node.completed:
            logger.error("FFW aborted. Target node has already completed")
            raise ValueError(
                f"Error modifying method. The target node_id {target_node_id} has already completed.")

        self._ffw = True
        self._ffw_target_node_id = target_node_id

        # Start fast-forward (FFW) from start to target_node_id
        logger.info("FFW starting, target node: " + str(target_node))
        ffw_process_instr = self._interpret()
        while self._ffw:
            # TODO fix loop:
            # - support ending in interrupt handler when ffw_process_instr is exhausted
            try:
                next(ffw_process_instr)
                if not self._ffw:
                    logger.debug("FFW found, target node id: " + self._ffw_target_node_id)
            except StopIteration:
                self._ffw = False
                logger.error(f"FFW failed, node {self._ffw_target_node_id} could not be reached (main).")
                raise Exception(f"FFW failed, node {self._ffw_target_node_id} could not be reached (main).")
            try:
                if self._ffw:
                    pass
                    self._run_interrupt_handlers()
                    if not self._ffw:
                        logger.debug("FFW found in interrupts, target node id: " + self._ffw_target_node_id)
            except Exception:
                logger.error("Exception during FFW interrupt handler")
                raise

        # set prepared generator as the new source for tick()
        self._process_instr = ffw_process_instr
        logger.info("FFW complete")

    def _patch_node_references(self, program: p.ProgramNode):
        """ Patch node references to updated program nodes to account for edited method. """
        logger.info("Patching node references in interpreter interrupts")
        for ar, _ in self.interrupts:
            node = ar.owner
            if node is not None and not isinstance(node, p.ProgramNode):
                new_node = program.get_child_by_id(node.id)
                if new_node is None:
                    logger.error(f"No new node was found to replace {node}. Node cannot be patched")
                else:
                    if ar.owner != new_node:
                        ar.owner = new_node
                        logger.debug(f"Patched node reference {new_node}")
                    else:
                        logger.warning(f"Node not patched: {new_node} - old node already matched the new node!?")

        # TODO get rid of this when moving macro processing to analyser
        logger.info("Patching node references in interpreter macros")
        for name, node in self.macros.items():
            if node is not None and not isinstance(node, p.ProgramNode):
                new_node = program.get_child_by_id(node.id)
                if new_node is None:
                    logger.error(f"No new node was found to replace {node}. Node cannot be patched")
                else:
                    assert isinstance(new_node, p.MacroNode)
                    if node != new_node:
                        self.macros[name] = new_node
                        logger.debug(f"Patched node reference {new_node}")
                    else:
                        logger.warning(f"Node not patched: {new_node} - old node already matched the new node!?")

        logger.info("Patching complete")

    def get_marks(self) -> list[str]:
        records: list[tuple[str, int]] = []
        for r in self.runtimeinfo.records:
            if isinstance(r.node, p.MarkNode):
                completed_states = [st for st in r.states if st.state_name == RuntimeRecordStateEnum.Completed]
                for completed_state in completed_states:
                    end_tick = completed_state.state_tick
                    records.append((r.node.name, end_tick))

        def sort_fn(t: tuple[str, int]) -> int:
            return t[1]

        records.sort(key=sort_fn)
        return [t[0] for t in records]

    def inject_node(self, program: p.ProgramNode):
        """ Inject the child nodes of program into the running program in the current scope
        to be executed as the next instruction. """
        node = p.InjectedNode()
        for n in program.children:
            node.append_child(n)
        ar = ActivationRecord(node, self._tick_time)
        self._register_interrupt(ar, self._create_interrupt_handler(node, ar))

    def _interpret(self) -> NodeGenerator:
        """ Create generator for interpreting the main program. """
        self.running = True
        tree = self._program
        if tree is None:
            return None

        yield from self.visit(tree)

    def _register_interrupt(self, ar: ActivationRecord, handler: NodeGenerator):
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
            if isinstance(node, (p.WatchNode, p.InjectedNode, p.AlarmNode)):
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
                    if isinstance(node, p.AlarmNode):
                        node.reset_runtime_state(recursive=True)
                        ar = ActivationRecord(node)
                        self._register_interrupt(ar, self._create_interrupt_handler(node, ar))
            else:
                raise NotImplementedError(f"Interrupt for node type {str(node)} not implemented")
        return instr_count > 0

    def _create_interrupt_handler(self, node: p.Node, ar: ActivationRecord) -> NodeGenerator:
        ar.fill_start(self._tick_time)
        yield from self.visit(node)

    def tick(self, tick_time: float, tick_number: int):  # noqa C901
        self._tick_time = tick_time
        self._tick_number = tick_number

        logger.debug(f"Tick {self._tick_number}")

        if self._process_instr is None:
            self._process_instr = self._interpret()

        # execute one iteration of program
        assert self._process_instr is not None, "self.process_instr is None"
        try:
            next(self._process_instr)
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
            self._run_interrupt_handlers()
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

    def _is_awaiting_threshold(self, node: p.Node):
        if node.completed:
            return False

        if node.threshold is not None and not node.forced:
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

            threshold_value = str(node.threshold)
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

    def _evaluate_condition(self, node: p.NodeWithCondition) -> bool:
        c = node.condition
        assert c is not None, "Error in condition"
        assert not c.error, f"Error parsing condition '{node.condition_part}'"
        assert c.tag_name, "Error in condition tag"
        assert c.tag_value, "Error in condition value"
        assert self.context.tags.has(c.tag_name), f"Unknown tag '{c.tag_name}' in condition '{node.condition_part}'"
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

    def _visit_children(self, node: p.NodeWithChildren) -> NodeGenerator:
        ar = self.stack.peek()
        for child in node.children:
            if ar.complete:
                break
            yield from self.visit(child)

    # Visitor Impl

    @override
    def visit(self, node: p.Node) -> NodeGenerator:
        if not self.running:
            return

        if self._ffw:
            logger.debug(f"Visiting {node} during FFW")
            if self._ffw_target_node_id == node.id:
                # we have reached the ffw target node, disable ffw to make the generator ready for normal use
                self._ffw = False
                yield

            elif node.completed:
                # node was completed so all its children are as well
                # TODO: possibly return here ...
                yield
            else:
                # node was not started and must be visited in ffw mode
                # TODO: what if ffw is completed during this??
                node.started = True
                yield from super().visit(node)
                node.completed = True
                return
        else:
            # track the active node before any possible threshold
            self._program.active_node = node

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
            # TODO verify that we don't get duplicate await runtime states here
            record.add_state_awaiting_threshold(
                self._tick_time, self._tick_number,
                self.context.tags.as_readonly())
            yield

        node.started = True

        # delegate to concrete visitor method via base method
        yield from super().visit(node)

        if not node.completed:
            record.set_end_visit(
                self._tick_time, self._tick_number,
                self.context.tags.as_readonly())

        logger.debug(f"Visit {node} done")
        node.completed = True

    def visit_ProgramNode(self, node: p.ProgramNode) -> NodeGenerator:
        if not self._ffw:
            ar = ActivationRecord(node, self._tick_time)
            self.stack.push(ar)
            self.context.emitter.emit_on_scope_start(node.id)
            self.context.emitter.emit_on_scope_activate(node.id)

        yield from self._visit_children(node)

        # Note: This event means that the last line of the method is complete.
        # The method may change later by an edit, so it doesn't necessarily mean
        # that the method has ended.
        self.context.emitter.emit_on_method_end()

        # Avoid returning from the visit. This makes it possible to inject or edit
        # code at the bottom of the method which will then be added as new child nodes
        # of the ProgramNode.
        # There may also be commands that still run, in particular Alarm which runs
        # indefinitely
        # In particular, we don emit scope end for the root scope and we don't pop the program node AR from the stack
        while self.running:
            yield

    def visit_BlankNode(self, node: p.BlankNode) -> NodeGenerator:
        if self._ffw:
            return

        # avoid advancing into whitespace-only code lines
        while node.has_only_trailing_whitespace:
            logging.debug(f"Dont interpret node {node} with has_only_trailing_whitespace")
            node.started = False
            yield


    def visit_MarkNode(self, node: p.MarkNode) -> NodeGenerator:
        if self._ffw:
            return

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

        yield

        record.add_state_completed(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

    def visit_BatchNode(self, node: p.BatchNode) -> NodeGenerator:
        if self._ffw:
            return

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

        yield

        record.add_state_completed(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

    def visit_MacroNode(self, node: p.MacroNode) -> NodeGenerator:
        if self._ffw:
            raise NotImplementedError("FFW not yet implemented for Macro instructions")

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

        yield

    def visit_CallMacroNode(self, node: p.CallMacroNode) -> NodeGenerator:
        if self._ffw:
            raise NotImplementedError("FFW not yet implemented for Macro instructions")

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
        yield from self._visit_children(macro_node)
        self.stack.pop()

        record.add_state_completed(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

    def visit_BlockNode(self, node: p.BlockNode) -> NodeGenerator:
        record = self.runtimeinfo.get_last_node_record(node)
        ar: ActivationRecord | None = None

        if not self._ffw:
            ar = ActivationRecord(node, self._tick_time)
            self.stack.push(ar)
            self.context.tags[SystemTagName.BLOCK].set_value(node.name, self._tick_number)
            self.context.emitter.emit_on_block_start(node.name, self._tick_number)
            self.context.emitter.emit_on_scope_start(node.id)
            logger.debug(f"Block Tag set to {node.name}")

            yield

            self.context.emitter.emit_on_scope_activate(node.id)
            record.add_state_started(
                self._tick_time, self._tick_number,
                self.context.tags.as_readonly())

        yield from self._visit_children(node)

        if not self._ffw:
            if ar is None:
                ar = self.stack.find_by_owner_id(node.id)
                assert ar is not None, "AR is none in second visit_Block part"

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
                    assert isinstance(ar.owner, p.BlockNode)
                    self.context.tags[SystemTagName.BLOCK].set_value(ar.owner.name, self._tick_number)
                    self.context.emitter.emit_on_block_end(node.name, ar.owner.name, self._tick_number)
                    logger.debug(f"Block Tag popped to {ar.owner.name}")
                    block_restored = True
            if not block_restored:
                self.context.tags[SystemTagName.BLOCK].set_value(None, self._tick_number)
                self.context.emitter.emit_on_block_end(node.name, "", self._tick_number)
                logger.debug(f"Block Tag cleared from {node.name}")
            self.context.emitter.emit_on_scope_end(node.id)

    def visit_EndBlockNode(self, node: p.EndBlockNode) -> NodeGenerator:
        if self._ffw:
            return

        record = self.runtimeinfo.get_last_node_record(node)
        record.add_state_started(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())
        for ar in reversed(self.stack.records):
            if ar.artype == ARType.BLOCK:
                ar.complete = True
                logger.debug(f"EndBlock ended block {ar.owner.display_name}")
                record.add_state_completed(
                    self._tick_time, self._tick_number,
                    self.context.tags.as_readonly())
                return
        logger.warning("End block found no block to end")
        yield from ()

    def visit_EndBlocksNode(self, node: p.EndBlocksNode) -> NodeGenerator:
        if self._ffw:
            return

        yield from ()

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

    def visit_InterpreterCommandNode(self, node: p.InterpreterCommandNode) -> NodeGenerator:  # noqa C901
        if self._ffw:
            return

        yield from ()

        record = self.runtimeinfo.get_last_node_record(node)
        record.add_state_started(self._tick_time, self._tick_number, self.context.tags.as_readonly())

        if node.instruction_name == InterpreterCommandEnum.BASE:
            valid_units = self.context.base_unit_provider.get_units()
            if node.arguments is None or node.arguments not in valid_units:
                record.add_state_failed(self._tick_time, self._tick_number, self.context.tags.as_readonly())
                raise NodeInterpretationError(node, f"Base instruction has invalid argument '{node.arguments}'. \
                    Value must be one of {', '.join(valid_units)}")
            self.context.tags[SystemTagName.BASE].set_value(node.arguments, self._tick_time)

        elif node.instruction_name == InterpreterCommandEnum.INCREMENT_RUN_COUNTER:
            run_counter = self.context.tags[SystemTagName.RUN_COUNTER]
            rc_value = run_counter.as_number() + 1
            logger.debug(f"Run Counter incremented from {rc_value - 1} to {rc_value}")
            run_counter.set_value(rc_value, self._tick_time)

        elif node.instruction_name == InterpreterCommandEnum.RUN_COUNTER:
            try:
                new_value = int(node.arguments)
                logger.debug(f"Run Counter set to {new_value}")
                self.context.tags[SystemTagName.RUN_COUNTER].set_value(new_value, self._tick_time)
            except ValueError:
                raise NodeInterpretationError(node, f"Invalid argument '{node.arguments}'. Argument must be an integer")

        elif node.instruction_name == InterpreterCommandEnum.WAIT:
            # possibly just import cmd registry
            arg_spec = ArgSpec.Regex(regex=REGEX_DURATION)
            groupdict = arg_spec.validate_w_groups(argument=node.arguments)
            if groupdict is None:
                raise NodeInterpretationError(node, f"Invalid argument '{node.arguments}'. Argument must be a duration")

            time = float(groupdict["number"])
            unit = groupdict["number_unit"]
            duration_end_time = get_duration_end(self._tick_time, time, unit)
            duration_end_time -= 0.1  # account for the final yield
            start = self._tick_time
            duration = duration_end_time - start
            logger.debug(f"Wait {duration=}")
            while self._tick_time < duration_end_time and not node.forced:
                if duration > 0:
                    progress = (self._tick_time - start) / duration
                    record.progress = progress
                yield

        else:
            record.add_state_failed(self._tick_time, self._tick_number, self.context.tags.as_readonly())
            raise NodeInterpretationError(node, f"Interpreter command '{node.instruction_name}' is not supported")

        record.add_state_completed(self._tick_time, self._tick_number, self.context.tags.as_readonly())
        yield  # avoid other instructions starting in this tick, to allow tests to consistently detect the completed state

    def visit_EngineCommandNode(self, node: p.EngineCommandNode) -> NodeGenerator:
        if self._ffw:
            return

        record = self.runtimeinfo.get_last_node_record(node)

        # Note: Commands can be resident and last multiple ticks.
        # The context (Engine) keeps track of this and we just
        # move on to the next instruction when tick() is invoked.
        # We do, however, provide the execution id to the context
        # so that it can update the runtime record appropriately.
        try:
            logger.debug(f"Executing command '{node}' via engine")
            self.context.schedule_execution(
                name=node.instruction_name,
                arguments=node.arguments,
                exec_id=record.exec_id)
        except Exception as ex:
            record.add_state_failed(
                self._tick_time, self._tick_number,
                self.context.tags.as_readonly())

            if isinstance(ex, EngineError):
                raise
            else:
                raise NodeInterpretationError(node, "Failed to pass engine command to engine") from ex

        yield

    def visit_UodCommandNode(self, node: p.UodCommandNode) -> NodeGenerator:
        if self._ffw:
            return

        record = self.runtimeinfo.get_last_node_record(node)

        # Note: Commands can be resident and last multiple ticks.
        # The context (Engine) keeps track of this and we just
        # move on to the next instruction when tick() is invoked.
        # We do, however, provide the execution id to the context
        # so that it can update the runtime record appropriately.
        try:
            logger.debug(f"Executing command '{node}' via engine")
            self.context.schedule_execution(
                name=node.instruction_name,
                arguments=node.arguments,
                exec_id=record.exec_id)
        except Exception as ex:
            record.add_state_failed(
                self._tick_time, self._tick_number,
                self.context.tags.as_readonly())

            if isinstance(ex, EngineError):
                raise
            else:
                raise NodeInterpretationError(node, "Failed to pass uod command to engine") from ex

        yield

    def visit_WatchNode(self, node: p.WatchNode) -> NodeGenerator:
        yield from self.visit_WatchOrAlarm(node)

    def visit_AlarmNode(self, node: p.AlarmNode) -> NodeGenerator:
        yield from self.visit_WatchOrAlarm(node)

    def visit_WatchOrAlarm(self, node: p.WatchNode | p.AlarmNode) -> NodeGenerator:
        if self._ffw:
            yield from self._visit_children(node)
            return

        record = self.runtimeinfo.get_last_node_record(node)

        ar = self.stack.peek()
        if ar.owner.id != node.id:
            ar = ActivationRecord(node)
            self.context.emitter.emit_on_scope_start(node.id)
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
                        self.context.emitter.emit_on_scope_activate(node.id)
                        logger.debug(f"{str(node)} executing")
                        record.add_state_started(
                            self._tick_time, self._tick_number,
                            self.context.tags.as_readonly())

                        yield from self._visit_children(node)
                        logger.debug(f"{str(node)} executed")
                        ar.complete = True
                        self.context.emitter.emit_on_scope_end(node.id)
                        record.add_state_completed(
                            self._tick_time, self._tick_number,
                            self.context.tags.as_readonly())

                        logger.info(f"Interrupt complete {ar}")
                    else:
                        yield

    def visit_InjectedNode(self, node: p.InjectedNode) -> NodeGenerator:
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
                yield from self._visit_children(node)
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

    def visit_CommentNode(self, node: p.CommentNode) -> NodeGenerator:
        if self._ffw:
            return

        # avoid advancing into whitespace-only code lines
        while node.has_only_trailing_whitespace:
            node.started = False
            yield


    def visit_ErrorInstructionNode(self, node: p.ErrorInstructionNode) -> NodeGenerator:
        record = self.runtimeinfo.get_last_node_record(node)

        logger.error(f"Invalid instruction: {str(node)}:\n{node.line}")

        record.add_state_started(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())
        record.add_state_failed(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

        raise NodeInterpretationError(node, f"Invalid instruction '{node.name}'")
