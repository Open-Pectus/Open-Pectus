from __future__ import annotations

import logging
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
from openpectus.lang.exec.visitor import (
    NodeGenerator, NodeVisitor, NodeAction, NullableActionResult, PrependNodeGenerator,
    run_ffw_tick, run_tick, run_ffw
)
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



class CallStack:
    def __init__(self):
        self._records: list[p.BlockNode | p.ProgramNode] = []

    def push(self, node: p.BlockNode | p.ProgramNode):
        self._records.append(node)

    def pop(self) -> p.BlockNode:
        if len(self._records) < 2:
            raise ValueError("May not pop off the root node")
        node = self._records.pop()
        assert isinstance(node, p.BlockNode)
        return node

    def peek(self) -> p.BlockNode | p.ProgramNode:
        return self._records[-1]

    def __str__(self):
        if len(self._records) == 0:
            return "CallStack (empty)"
        s = '\n\t'.join(repr(block) for block in reversed(self._records))
        s = f'CallStack (size: {len(self._records)})\n{s}\n\n'
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


class Interrupt:
    def __init__(self, node: p.NodeWithChildren, actions: NodeGenerator):
        self.node = node
        self.actions = actions


class PInterpreter(NodeVisitor):
    def __init__(self, program: p.ProgramNode, context: InterpreterContext) -> None:
        self._program = program
        self.context = context
        self.stack: CallStack = CallStack()
        self._interrupts_map: dict[str, Interrupt] = {}
        self.macros: dict[str, p.MacroNode] = dict()

        self.start_time: float = 0
        self._tick_time: float = 0
        self._tick_number: int = -1

        self._generator: NodeGenerator | None = None

        self.runtimeinfo: RuntimeInfo = RuntimeInfo()
        logger.debug("Interpreter initialized")


    # TODO fix
    def update_method_and_ffw(self, program: p.ProgramNode):
        """ Update method while method is running. """
        # set new program, and patch state to point to new nodes, set ffw and advance generator to get to where we were
        raise NotImplementedError("Edit currently not working")

        # collect node id from old method. The id will match the corresponding node in the new method
        if self._program.active_node is None:
            raise ValueError("Edit cannot be performed when no current node is set")
        logger.debug(f"The active node is {self._program.active_node}")
        logger.debug(f"The active node states are {self._program.active_node.started=} | {self._program.active_node.completed=}")
        target_node_id = self._program.active_node.id

        # patch runtimeinfo records to reference new nodes - before or after ffw? should not matter
        self.runtimeinfo.patch_node_references(program)
        self._patch_node_references(program)

        # verify that target is not completed - if so ffw won't find it
        self._program = program
        self._generator = None  # clear so either tick or us may set it
        target_node = program.get_child_by_id(target_node_id)  # find target node in new ast
        if target_node is not None:
            logger.debug(f"The target node states are {target_node.started=} | {target_node.completed=}")

        if target_node is None:
            logger.error(f"FFW aborted because target node {target_node_id} was not found in new ast")
            raise ValueError(
                f"Error modifying method. The target node_id {target_node_id} was not found in the updated method.")

        # Start fast-forward (FFW) from start to target_node_id
        logger.info(f"FFW starting, target node: {target_node}")
        # create the generator for the new program
        gen = self.visit_ProgramNode(self._program)

        # Fast-forward skipping over actions in history
        main_complete = False
        active_interrupt_keys = list(self._interrupts_map.keys())
        while not main_complete or len(active_interrupt_keys) > 0:
            if not main_complete:
                try:
                    x = run_ffw_tick(gen)
                    if isinstance(x, NullableActionResult):
                        main_complete = True
                        gen = PrependNodeGenerator(x, gen)
                    elif x:
                        main_complete = True
                    else:                   
                        # None was yielded, just continue
                        pass
                except Exception:
                    logger.error("Exception during FFW main handler", exc_info=True)
                    raise

            if len(active_interrupt_keys) > 0:
                active_interrupt_keys_copy = list(active_interrupt_keys)
                for key in active_interrupt_keys_copy:
                    interrupt = self._interrupts_map[key]
                    try:
                        x = run_ffw_tick(interrupt.actions)
                        if isinstance(x, NullableActionResult):
                            interrupt.actions = PrependNodeGenerator(x, interrupt.actions)
                            active_interrupt_keys.remove(key)
                        elif x:
                            active_interrupt_keys.remove(key)
                        else:
                            pass
                    except Exception:
                        logger.error("Exception during FFW interrupt handler", exc_info=True)
                        raise

        # set prepared generator as the new source for tick()
        self._generator = gen
        logger.info("FFW complete")

    def _patch_node_references(self, program: p.ProgramNode):  # noqa C901
        """ Patch node references to updated program nodes to account for a running method edit. """
        logger.info("Patching node references in stack")
        for inx, node in enumerate(self.stack._records):
            # why the check against ProgramNode?
            if node is not None and not isinstance(node, p.ProgramNode):
                new_node = program.get_child_by_id(node.id)
                if new_node is None:
                    logger.error(f"No new node was found to replace {node}. Node cannot be patched")
                else:
                    if node != new_node:
                        if isinstance(new_node, p.BlockNode):
                            self.stack._records[inx] = new_node
                            logger.debug(f"Patched node reference {new_node}")
                        else:
                            logger.error(f"Node reference not patched {new_node}. A NodeWithChildren instance is required")
                    else:
                        logger.warning(f"Node not patched: {new_node} - old node already matched the new node!?")

        logger.info("Patching node references in interpreter interrupts")
        keys = list(self._interrupts_map.keys())
        for key in keys:
            if key in self._interrupts_map.keys():
                interrupt = self._interrupts_map[key]
                if interrupt.node is not None and not isinstance(interrupt.node, p.ProgramNode):
                    new_node = program.get_child_by_id(interrupt.node.id)
                    if new_node is None:
                        logger.error(f"No new node was found to replace {interrupt.node}. Node cannot be patched")
                    else:
                        if interrupt.node != new_node:
                            if isinstance(new_node, p.NodeWithChildren):
                                interrupt.node = new_node
                                logger.debug(f"Patched node reference {new_node}")
                            else:
                                logger.error(f"Node reference not patched {new_node}. A NodeWithChildren instance is required")
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
        # Note: registers visit rather than visit_InjectedNode because visit has not been
        # run for the node unlike Watch and Alarm
        self._register_interrupt(node, self.visit(node))

    def _register_interrupt(self, node: p.NodeWithChildren, handler: NodeGenerator):
        logger.debug(f"Interrupt handler registered for {node}")        
        self._interrupts_map[node.id] = Interrupt(node, handler)

    def _unregister_interrupt(self, node: p.NodeWithChildren):
        if node.id in self._interrupts_map.keys():
            del self._interrupts_map[node.id]
            logger.debug(f"Interrupt handler unregistered for {node}")

    def tick(self, tick_time: float, tick_number: int):  # noqa C901
        self._tick_time = tick_time
        self._tick_number = tick_number

        logger.debug(f"Tick {self._tick_number}")

        if self._generator is None:
            self._generator = self.visit_ProgramNode(self._program)

        # execute one iteration of program
        assert self._generator is not None
        try:
            run_tick(self._generator)
        except StopIteration:
            logger.debug("Main generator exhausted")
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
        interrupts = list(self._interrupts_map.values())
        for interrupt in interrupts:
            logger.debug(f"Executing interrupt tick for node {interrupt.node}")
            try:
                run_tick(interrupt.actions)
            except StopIteration:
                logger.debug(f"Interrupt generator {interrupt.node} exhausted")
                if isinstance(interrupt.node, p.AlarmNode):
                    logger.debug(f"Restarting completed Alarm {interrupt.node}")
                    self._re_register_alarm_interrupt(interrupt.node)
            except AssertionError as ae:
                raise InterpretationError(message=str(ae), exception=ae)
            except (InterpretationInternalError, InterpretationError):
                logger.error("Interpreter error in interrupt handler", exc_info=True)
                raise
            except Exception as ex:
                logger.error("Unhandled interpretation error in interrupt handler", exc_info=True)
                raise InterpretationError("Interpreter error") from ex

    def stop(self):
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
        for child in node.children:
            if node.children_complete:
                break
            child_result = self.visit(child)
            if node.children_complete:
                break
            yield from child_result
        node.children_complete = True


    # Visitor Impl

    @override
    def visit(self, node: p.Node) -> NodeGenerator:
        def start(node):
            self._program.active_node = node

            # interrupts are visited multiple times. make sure to only create
            # a new record on the first visit
            record = self.runtimeinfo.get_last_node_record_or_none(node)
            if record is None:
                record = self.runtimeinfo.begin_visit(
                    node,
                    self._tick_time, self._tick_number,
                    self.context.tags.as_readonly())
        # use custom name to avoid action name collision with actions in the visit_* method
        yield NodeAction(node, start, name="visit_start")

        # log all visits
        logger.debug(f"Visiting {node} at tick {self._tick_time}")

        # possibly wait for node threshold to expire
        if not node.started and not node.completed:
            if self._is_awaiting_threshold(node):
                self._add_record_state_awaiting_threshold(node)

            while self._is_awaiting_threshold(node):
                yield

        # threshold has passed
        node.started = True

        # delegate to concrete visitor method via base method
        yield from super().visit(node)

        def end(node):
            record = self.runtimeinfo.get_last_node_record(node)
            record.set_end_visit(
                self._tick_time, self._tick_number,
                self.context.tags.as_readonly())

        # use custom name to avoid action name collision with actions in the visit_* method
        yield NodeAction(node, end, name="visit_end", tick_break=True)

        logger.debug(f"Visit {node} done")

    def visit_ProgramNode(self, node: p.ProgramNode) -> NodeGenerator:
        def start(node):
            self.stack.push(node)
            self.context.emitter.emit_on_scope_start(node.id, "Program", "")
            self.context.emitter.emit_on_scope_activate(node.id, "Program", "")
        yield NodeAction(node, start)

        yield from self._visit_children(node)

        # Note: This event means that the last line of the method is complete.
        # The method may change later by an edit, so it doesn't necessarily mean
        # that the method has ended.
        yield NodeAction(node, lambda node: self.context.emitter.emit_on_method_end(), "emit_on_method_end")

        # Avoid returning from the visit. This makes it possible to inject or edit
        # code at the bottom of the method which will then be added as new child nodes
        # of the ProgramNode.
        # There may also be commands that still run, in particular Alarm which runs
        # indefinitely
        # In particular, we don emit scope end for the root scope and we don't pop the program node AR from the stack
        while True:
            yield

    def visit_BlankNode(self, node: p.BlankNode) -> NodeGenerator:
        # avoid advancing into whitespace-only code lines
        # TODO consider edit mode
        while node.has_only_trailing_whitespace:
            node.started = False
            yield
        node.completed = True

    def visit_MarkNode(self, node: p.MarkNode) -> NodeGenerator:
        logger.info(f"Mark {str(node)}")

        def do(node):
            assert isinstance(node, p.MarkNode)
            try:
                mark_tag = self.context.tags.get("Mark")
                mark_tag.set_value(node.name, self._tick_time)
            except ValueError:
                logger.error(f"Failed to get Mark tag {node.name}")

            self._add_record_state_started(node)
            self._add_record_state_complete(node)
            node.completed = True
        yield NodeAction(node, do)


    def visit_BatchNode(self, node: p.BatchNode) -> NodeGenerator:
        logger.info(f"Batch {str(node)}")

        def do(node):
            assert isinstance(node, p.BatchNode)
            try:
                batch_tag = self.context.tags.get("Batch Name")
                batch_tag.set_value(node.name, self._tick_time)
            except ValueError:
                logger.error("Failed to get Batch Name tag")
            self._add_record_state_started(node)
            self._add_record_state_complete(node)
            node.completed = True
        yield NodeAction(node, do)


    def visit_MacroNode(self, node: p.MacroNode) -> NodeGenerator:
        # TODO handle FFW

        record = self.runtimeinfo.get_last_node_record(node)
        record.add_state_started(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())
        logger.info(f"Defining macro {node}")

        # TODO move this check to an analyzer
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

    # TODO fix
    def visit_CallMacroNode(self, node: p.CallMacroNode) -> NodeGenerator:
        # TODO handle FFW

        record = self.runtimeinfo.get_last_node_record(node)
        record.add_state_started(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

        if node.name not in self.macros.keys():
            logger.warning(f'No macro defined with name "{node.name}"')
            available_macros = "None"
            if len(self.macros.keys()):
                available_macros = ", ".join(f'"{macro}"' for macro in self.macros.keys())
            self._add_record_state_failed(node)
            raise NodeInterpretationError(
                node, 
                f'No macro defined with name "{node.name}". Available macros: {available_macros}.')

        macro_node = self.macros[node.name]
        yield from self._visit_children(macro_node)
        record.add_state_completed(
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())
        # This works - but does it break something, e.g. runlog?
        macro_node.reset_runtime_state(recursive=True)

    def visit_BlockNode(self, node: p.BlockNode) -> NodeGenerator:

        def try_aquire_block_lock(node):
            assert isinstance(node, p.BlockNode)
            scope = self.stack.peek()
            if not isinstance(scope, p.BlockNode) or scope == node.parent:
                logger.debug(f"Block lock for {node} aquired")
                node.lock_aquired = True

        if not node.lock_aquired:
            while not node.lock_aquired:
                logger.debug(f"Waiting to aquire block lock for {node}")
                try_aquire_block_lock(node)
                if node.lock_aquired:
                    break
                yield

        def push_to_stack(node):
            assert isinstance(node, p.BlockNode)
            node.lock_aquired = True
            self.stack.push(node)
            self.context.tags[SystemTagName.BLOCK].set_value(node.name, self._tick_number)
            self.context.emitter.emit_on_block_start(node.name, self._tick_number)
            self.context.emitter.emit_on_scope_start(node.id, "Block", node.arguments)
            logger.debug(f"Block Tag set to {node.name}")
        yield NodeAction(node, push_to_stack)

        def emit_scope_activated(node):
            self.context.emitter.emit_on_scope_activate(node.id, "Block", node.arguments)
            self._add_record_state_started(node)
        yield NodeAction(node, emit_scope_activated)

        yield from self._visit_children(node)

        while not node.children_complete:
            yield

        # allow possible interrrupts time to acquire the block lock before the node's following-siblings are executed
        yield

        # wait for End block(s) to mark the node as completed
        while not node.completed:
            yield

    def visit_EndBlockNode(self, node: p.EndBlockNode) -> NodeGenerator:
        def end_block(node):
            assert isinstance(node, p.EndBlockNode)
            self._add_record_state_started(node)
            if not isinstance(self.stack.peek(), p.BlockNode):
                logger.debug(f"No blocks to end for node {node}")
                self._add_record_state_cancelled(node)
                return
            old_block = self.stack.pop()
            new_block = self.stack.peek()
            logger.debug(f"Ending block {old_block}")
            new_block_name = new_block.name if isinstance(new_block, p.BlockNode) else None
            self.context.tags[SystemTagName.BLOCK].set_value(new_block_name, self._tick_number)
            self.context.emitter.emit_on_block_end(old_block.name, new_block_name or "", self._tick_number)
            old_block.children_complete = True
            old_block.completed = True
            self._add_record_state_complete(node)
            self._add_record_state_complete(old_block)
            self._abort_block_interrupts(old_block)
            node.completed = True
        yield NodeAction(node, end_block)

    def visit_EndBlocksNode(self, node: p.EndBlocksNode) -> NodeGenerator:
        def end_blocks(node):
            assert isinstance(node, p.EndBlocksNode)
            self._add_record_state_started(node)
            if not isinstance(self.stack.peek(), p.BlockNode):
                logger.debug(f"No blocks to end for node {node}")
                self._add_record_state_cancelled(node)
                return
            while isinstance(self.stack.peek(), p.BlockNode):
                old_block = self.stack.pop()
                new_block = self.stack.peek()
                logger.debug(f"Ending block {old_block}")
                new_block_name = new_block.name if isinstance(new_block, p.BlockNode) else None
                self.context.tags[SystemTagName.BLOCK].set_value(new_block_name, self._tick_number)
                self.context.emitter.emit_on_block_end(old_block.name, new_block_name or "", self._tick_number)
                old_block.children_complete = True
                old_block.completed = True
                self._add_record_state_complete(node)
                self._add_record_state_complete(old_block)
                self._abort_block_interrupts(old_block)
            node.completed = True
        yield NodeAction(node, end_blocks)

    def visit_InterpreterCommandNode(self, node: p.InterpreterCommandNode) -> NodeGenerator:  # noqa C901
        # TODO node.completed
        def InterpreterCommandNode_start(node):
            self._add_record_state_started(node)
        yield NodeAction(node, InterpreterCommandNode_start)

        if node.instruction_name == InterpreterCommandEnum.BASE:
            def base(node):
                assert isinstance(node, p.InterpreterCommandNode)
                valid_units = self.context.base_unit_provider.get_units()
                if node.arguments is None or node.arguments not in valid_units:
                    self._add_record_state_failed(node)
                    raise NodeInterpretationError(node, f"Base instruction has invalid argument '{node.arguments}'. \
                        Value must be one of {', '.join(valid_units)}")
                self.context.tags[SystemTagName.BASE].set_value(node.arguments, self._tick_time)
            yield NodeAction(node, base)

        elif node.instruction_name == InterpreterCommandEnum.INCREMENT_RUN_COUNTER:
            def increment_run_counter(node):
                run_counter = self.context.tags[SystemTagName.RUN_COUNTER]
                rc_value = run_counter.as_number() + 1
                logger.debug(f"Run Counter incremented from {rc_value - 1} to {rc_value}")
                run_counter.set_value(rc_value, self._tick_time)
            yield NodeAction(node, increment_run_counter)

        elif node.instruction_name == InterpreterCommandEnum.RUN_COUNTER:
            def run_counter(node):
                try:
                    new_value = int(node.arguments)
                    logger.debug(f"Run Counter set to {new_value}")
                    self.context.tags[SystemTagName.RUN_COUNTER].set_value(new_value, self._tick_time)
                except ValueError:
                    raise NodeInterpretationError(node, f"Invalid argument '{node.arguments}'. Argument must be an integer")
            yield NodeAction(node, run_counter)

        elif node.instruction_name == InterpreterCommandEnum.WAIT:
            # use persisted start time to avoid resetting the wait on edit
            if node.wait_start_time is None:
                node.wait_start_time = self._tick_time

            # possibly just import cmd registry
            arg_spec = ArgSpec.Regex(regex=REGEX_DURATION)
            groupdict = arg_spec.validate_w_groups(argument=node.arguments)
            if groupdict is None:
                raise NodeInterpretationError(node, f"Invalid argument '{node.arguments}'. Argument must be a duration")

            time = float(groupdict["number"])
            unit = groupdict["number_unit"]
            duration_end_time = get_duration_end(node.wait_start_time, time, unit)
            duration_end_time -= 0.1  # account for the final yield
            duration = duration_end_time - node.wait_start_time
            if duration < 0:
                logger.debug("Skipping Wait with duration shorter than a tick")
                return
            logger.debug(f"Start Wait with duration: {duration}")

            while self._tick_time < duration_end_time and not node.forced:
                if duration > 0:
                    progress = (self._tick_time - node.wait_start_time) / duration
                    record = self.runtimeinfo.get_last_node_record(node)
                    record.progress = progress
                yield

        else:  # unknown InterpreterCommandNode instruction
            self._add_record_state_failed(node)
            raise NodeInterpretationError(node, f"Interpreter command '{node.instruction_name}' is not supported")

        def complete(node):
            logger.debug(f"Interpreter command Node {node} complete")
            self._add_record_state_complete(node)

        yield NodeAction(node, complete)

    def visit_NotifyNode(self, node: p.NotifyNode):
        def do(node):
            self.context.emitter.emit_on_notify_command(node.arguments)

            self._add_record_state_started(node)
            self._add_record_state_complete(node)
            node.completed = True
        yield NodeAction(node, do)

    def visit_EngineCommandNode(self, node: p.EngineCommandNode) -> NodeGenerator:
        # TODO node.completed
        def schedule(node):
            assert isinstance(node, p.EngineCommandNode)
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
                self._add_record_state_failed(node)
                if isinstance(ex, EngineError):
                    raise
                else:
                    raise NodeInterpretationError(node, "Failed to pass engine command to engine") from ex

        yield NodeAction(node, schedule)


    def visit_UodCommandNode(self, node: p.UodCommandNode) -> NodeGenerator:
        # TODO node-completed

        def schedule(node):
            assert isinstance(node, p.UodCommandNode)
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
                self._add_record_state_failed(node)
                if isinstance(ex, EngineError):
                    raise
                else:
                    raise NodeInterpretationError(node, "Failed to pass uod command to engine") from ex

        yield NodeAction(node, schedule)


    def visit_WatchNode(self, node: p.WatchNode) -> NodeGenerator:
        logger.debug(f"visit_WatchNode {node} method start")

        def register_interrupt(node):
            assert isinstance(node, p.WatchNode)
            self.context.emitter.emit_on_scope_start(node.id, "Watch", node.arguments)
            self._register_interrupt(node, self.visit_WatchNode(node))
            node.interrupt_registered = True
            self._add_record_state_awaiting_interrupt(node)

        if not node.interrupt_registered:
            yield NodeAction(node, register_interrupt, tick_break=True)
            return

        # running from interrupt
        if not node.activated:
            yield NodeAction(node, self._add_record_state_awaiting_condition)

        def start(node):
            self.context.emitter.emit_on_scope_activate(node.id, "Watch", node.arguments)
            logger.debug(f"{str(node)} executing")
            self._add_record_state_started(node)

        while not node.activated:
            if node.cancelled:
                self._add_record_state_cancelled(node)
                self.context.emitter.emit_on_scope_end(node.id, "Watch", node.arguments)
                logger.info(f"Instruction {node} cancelled")
                node.completed = True
                return
            self._try_activate_node(node)
            if node.activated:
                yield NodeAction(node, start)
            else:
                yield

        # was activated
        yield from self._visit_children(node)


        def complete(node):
            assert isinstance(node, p.WatchNode)
            logger.debug(f"Watch {node} complete")
            self.context.emitter.emit_on_scope_end(node.id, "Watch", node.arguments)
            self._add_record_state_complete(node)
            #self._unregister_interrupt(node) # we need to keep the interrupt handler active - but this conflicts with using emit_on_scope_end???
            node.completed = True
        if not node.completed:
            yield NodeAction(node, complete)

        logger.debug(f"visit_WatchNode {node} method end")
        
        # now idle until a possible method edit which may append child nodes to the Watch


    def visit_AlarmNode(self, node: p.AlarmNode) -> NodeGenerator:
        logger.debug(f"visit_AlarmNode {node} method start")

        def register_alarm_interrupt(node):
            assert isinstance(node, p.AlarmNode)
            self.context.emitter.emit_on_scope_start(node.id, "Alarm", node.arguments)
            self._register_interrupt(node, self.visit_AlarmNode(node))
            node.interrupt_registered = True
            self._add_record_state_awaiting_interrupt(node)

        if not node.interrupt_registered:
            yield NodeAction(node, register_alarm_interrupt)
            logger.debug("Return after register")
            return

        # running from interrupt
        if not node.activated:
            yield NodeAction(node, self._add_record_state_awaiting_condition)

        def start(node):
            self.context.emitter.emit_on_scope_activate(node.id, "Alarm", node.arguments)
            logger.debug(f"{str(node)} executing")
            self._add_record_state_started(node)

        while not node.activated:
            if node.cancelled:
                self._add_record_state_cancelled(node)
                self.context.emitter.emit_on_scope_end(node.id, "Alarm", node.arguments)
                logger.info(f"Instruction {node} cancelled")
                node.completed = True
                return
            self._try_activate_node(node)
            if node.activated:
                yield NodeAction(node, start)
            else:
                yield

        # was activated
        yield from self._visit_children(node)

        def complete(node):
            assert isinstance(node, p.AlarmNode)
            logger.debug(f"Alarm {node} complete")
            self.context.emitter.emit_on_scope_end(node.id, "Alarm", node.arguments)
            self._add_record_state_complete(node)
        yield NodeAction(node, complete)

        logger.debug(f"visit_AlarmNode {node} method end")

        # now idle which will make the interrupt runner recreate the interrupt

    def _re_register_alarm_interrupt(self, node: p.AlarmNode):
        self._unregister_interrupt(node)
        node.reset_runtime_state(recursive=True)
        try:
            x = next(self.visit_AlarmNode(node))  # because node was reset this runs just the registration part
            assert isinstance(x, NodeAction) and x.action_name == "register_alarm_interrupt"
            x.execute()
        except Exception:
            logger.error("Failed to run alarm interrupt registration", exc_info=True)
            raise

    def visit_InjectedNode(self, node: p.InjectedNode) -> NodeGenerator:
        def start(node):
            self._add_record_state_started(node)
        yield NodeAction(node, start)
        yield from self._visit_children(node)
        yield NodeAction(node, self._add_record_state_complete)
        node.completed = True


    def visit_CommentNode(self, node: p.CommentNode) -> NodeGenerator:
        # avoid advancing generator into whitespace-only code lines
        while node.has_only_trailing_whitespace:
            node.started = False
            yield

        node.completed = True


    def visit_ErrorInstructionNode(self, node: p.ErrorInstructionNode) -> NodeGenerator:
        if __debug__:
            # enable the Noop (no operation) instruction used in tests
            if node.instruction_name == "Noop":
                def noop(node):
                    self._add_record_state_started(node)
                    self._add_record_state_complete(node)
                yield NodeAction(node, noop)
                return

        logger.error(f"Invalid instruction: {str(node)}:\n{node.line}")            
        self._add_record_state_started(node)
        self._add_record_state_failed(node)
        raise NodeInterpretationError(node, f"Invalid instruction '{node.name}'")

    # def helper methods for node manipulation

    def _try_activate_node(self, node: p.NodeWithCondition):
        assert isinstance(node, p.NodeWithCondition)
        condition_result = False
        if node.cancelled:
            raise TypeError("Cancel must be handled before _try_active_node")
        elif node.forced:
            self._add_record_state_forced(node)
            logger.info(f"Instruction {node} forced")
            condition_result = True
        else:
            try:
                condition_result = self._evaluate_condition(node)
            except AssertionError:
                raise
            except Exception as ex:
                raise NodeInterpretationError(node, "Error evaluating condition: " + str(ex))
            logger.debug(f"Condition for node {node} evaluated: {condition_result}")
        if condition_result:
            node.activated = True


    def _abort_block_interrupts(self, block: p.BlockNode):
        logger.debug(f"Cancelling interrupts for block {block}")
        descendants = block.get_child_nodes(recursive=True)
        interrupts = list(self._interrupts_map.values())
        for interrupt in interrupts:
            for child in descendants:
                if child.id == interrupt.node.id:
                    logger.debug(f"Cancelling interrupt for {child} in block")
                    interrupt.node.children_complete = True
                    self._unregister_interrupt(interrupt.node)

    # helper methods for recording node states

    def _add_record_state_awaiting_interrupt(self, node: p.Node):
        record = self.runtimeinfo.get_last_node_record(node)
        record.add_state_awaiting_interrupt(self._tick_time, self._tick_number, self.context.tags.as_readonly())

    def _add_record_state_awaiting_condition(self, node: p.Node):
        record = self.runtimeinfo.get_last_node_record(node)
        record.add_state_awaiting_condition(self._tick_time, self._tick_number, self.context.tags.as_readonly())

    def _add_record_state_awaiting_threshold(self, node: p.Node):
        record = self.runtimeinfo.get_last_node_record(node)
        record.add_state_awaiting_threshold(self._tick_time, self._tick_number, self.context.tags.as_readonly())

    def _add_record_state_started(self, node):
        record = self.runtimeinfo.get_last_node_record(node)
        record.add_state_started(self._tick_time, self._tick_number, self.context.tags.as_readonly())

    def _add_record_state_failed(self, node):
        record = self.runtimeinfo.get_last_node_record(node)
        record.add_state_failed(self._tick_time, self._tick_number, self.context.tags.as_readonly())

    def _add_record_state_complete(self, node):
        record = self.runtimeinfo.get_last_node_record(node)
        record.add_state_completed(self._tick_time, self._tick_number, self.context.tags.as_readonly())

    def _add_record_state_cancelled(self, node):
        record = self.runtimeinfo.get_last_node_record(node)
        record.add_state_cancelled(self._tick_time, self._tick_number, self.context.tags.as_readonly())

    def _add_record_state_forced(self, node):
        record = self.runtimeinfo.get_last_node_record(node)
        record.add_state_forced(self._tick_time, self._tick_number, self.context.tags.as_readonly())
