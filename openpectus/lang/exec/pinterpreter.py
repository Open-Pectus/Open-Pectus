from __future__ import annotations

import logging
import uuid

from openpectus.engine.commands import EngineCommand
from openpectus.engine.models import EngineCommandEnum
from openpectus.lang.exec.argument_specification import ArgSpec
from openpectus.lang.exec.events import EventEmitter
from openpectus.lang.exec.regex import REGEX_DURATION, get_duration_end
import openpectus.lang.exec.units as units
from openpectus.lang.exec.base_unit import BaseUnitProvider
from openpectus.lang.exec.commands import InterpreterCommandEnum, CommandRequest
from openpectus.lang.exec.errors import (
    EngineError, InterpretationError, InterpretationInternalError, MethodEditError, NodeInterpretationError
)
from openpectus.lang.exec.runlog import RunLog, RuntimeInfo, RuntimeRecord, RuntimeRecordStateEnum
from openpectus.lang.exec.tags import (
    TagCollection, SystemTagName, TagValueCollection,
)
from openpectus.lang.exec.visitor import (
    NodeGenerator, NodeVisitor, NodeAction, prepend, run_ffw_tick, run_tick
)
import openpectus.lang.model.ast as p
from typing_extensions import override

logger = logging.getLogger(__name__)

term_uod = "Unit Operation Definition file."
FFW_TICK_LIMIT = 1000  # Default limit for how many ticks are allowed during the fast-forward phase of a method edit.


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

    def with_edited_program(self, program: p.ProgramNode) -> CallStack:
        instance = CallStack()
        for node in self._records:
            new_node = program.get_child_by_id(node.id, include_self=True)
            if new_node is None:
                raise ValueError(f"Failed to clone node: {node}")
            assert isinstance(new_node, (p.BlockNode, p.ProgramNode))
            instance.push(new_node)
        return instance


class InterpreterContext():
    """ Defines the context of program interpretation"""

    @property
    def tags(self) -> TagCollection:
        raise NotImplementedError()

    def schedule_execution(self, name: str, arguments: str, instance_id: str):
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

        self.start_time: float = 0
        self._tick_time: float = 0
        self._tick_number: int = -1

        self._generator: NodeGenerator | None = None
        self._ffw = False
        self._in_interrupt = False

        self.runtimeinfo: RuntimeInfo = RuntimeInfo()
        self.tracking: Tracking = Tracking(self)

        self.ffw_tick_limit = FFW_TICK_LIMIT
        """ instructions pending following a ffw run """

        logger.debug("Interpreter initialized")

    def with_edited_program(self, new_program: p.ProgramNode) -> PInterpreter:
        """ Returns a new interpreter instance with program modified and in the state it would have been in if the updated
        program had been run from the beginning for the same number of ticks.

        Either succeeds and returns the updated interpreter instance or fails with EditError.
        The source interpreter and its entire state is unmodified, so the method edit is transactional. """

        # Use same context. We have to trust that e.g. tags will not be updated or events emitted until ffw is complete
        # Note: We could possibly verify this by adding some safeguards, seems to work fine though
        instance = PInterpreter(new_program, self.context)
        instance.runtimeinfo = self.runtimeinfo.with_edited_program(new_program)
        instance.stack = self.stack.with_edited_program(new_program)

        assert self._program.active_node is not None, "Active node is None. This should not occur during method merge"
        assert not isinstance(self._program.active_node, p.ProgramNode)
        target_node_id: str = self._program.active_node.id

        # modify new nodes corresponding to old nodes with registered interrupts, so the new nodes can re-register during ffw
        for key in self._interrupts_map.keys():
            node = new_program.get_child_by_id(key)
            if node is None:
                logger.warning(f"Failed to find and reset interrupt node id {key}")
                continue
            logger.debug(f"Resetting interrupt state for node {node}")
            assert isinstance(node, p.NodeWithChildren)
            node.interrupt_registered = False

        # modify new macro nodes corresponding to registered macros, so the new nodes can register new macros during ffw
        for macro_node in self._program.macros.values():
            node = new_program.get_child_by_id(macro_node.id)
            if node is None:
                logger.warning(f"Failed to find and reset macro node: {macro_node}")
                continue
            logger.debug(f"Resetting macro state for node {node}")
            assert isinstance(node, p.MacroNode)
            node.is_registered = False

        instance._generator = instance.visit_ProgramNode(new_program)
        instance._run_ffw(target_node_id)

        logger.info(f"Interpreter for revision {instance._program.revision} is ready")
        return instance

    def _run_ffw(self, target_node_id: str):  # noqa C901
        """ Fast-forward iteration over both the main generator and any interrupt generators without executing the nodes'
        functionality, until the actions produced are no longer present in the nodes' history.

        The purpose is to prepare all the generators to the state just after the last action in their respective nodes'
        history.

        Notes:
        - active_node: The node that is currently being visited, both during normal and ffw processing
        - target_node: The node in the new program with the same id as active_node in the old program at the time
            ffw starts. When ffw is complete, this should be the same as active_node in the new program (or possibly
            the following node, in case active node is completed)
        """
        assert self._generator is not None

        main_complete = False  # whether the main generator is 'complete'
        active_interrupt_keys = list(self._interrupts_map.keys())
        ffw_tick = 0  # number of ticks we spent in the ffw loop
        last_work_tick = 0  # tick number of the last tick we noticed progress
        self._ffw = True
        completed_interrupt_keys = []
        has_reached_target_node = False
        target_node: p.Node | None = self._program.get_child_by_id(target_node_id)
        assert target_node is not None  # is checked by method_manager

        while True:
            ffw_tick += 1

            if not main_complete:
                try:
                    logger.debug(f"Run main ffw tick {ffw_tick}")
                    x = run_ffw_tick(self._generator)
                    if isinstance(x, NodeAction):
                        last_work_tick = ffw_tick
                        main_complete = True
                        if x.node.id == target_node_id:
                            has_reached_target_node = True
                        logger.debug(f"Scheduling {x.action_name}, {x.node} for execution in main right after ffw")
                        self._generator = prepend(x, self._generator)
                        last_work_tick = ffw_tick
                        main_complete = True
                    elif x:
                        last_work_tick = ffw_tick
                        main_complete = True
                    else:
                        pass  # None was yielded, just continue, we can't know for sure whether any work was done or not
                    logger.debug(f"Main ffw tick {ffw_tick} complete")
                except Exception:
                    logger.error("Exception during FFW main handler", exc_info=True)
                    raise

            active_interrupt_keys = list(self._interrupts_map.keys())
            for key in active_interrupt_keys:
                if key in completed_interrupt_keys:  # skip interrupts we know are 'complete'
                    continue
                interrupt = self._interrupts_map[key]
                try:
                    logger.debug(f"Run interrupt {key} ffw tick {ffw_tick}")
                    self._in_interrupt = True
                    x = run_ffw_tick(interrupt.actions)
                    self._in_interrupt = False
                    if isinstance(x, NodeAction):
                        last_work_tick = ffw_tick
                        if x.node.id == target_node_id:
                            has_reached_target_node = True
                        logger.debug(f"Scheduling {x.action_name}, {x.node} for execution in interrupt {key} right after ffw")
                        interrupt.actions = prepend(x, interrupt.actions)
                        last_work_tick = ffw_tick
                        completed_interrupt_keys.append(key)
                    elif x:
                        last_work_tick = ffw_tick
                        completed_interrupt_keys.append(key)
                    else:
                        pass  # None was yielded, just continue, we can't know for sure whether any work was done or not
                    logger.debug(f"Interrupt {key} ffw tick {ffw_tick} complete")
                except Exception:
                    logger.error("Exception during FFW interrupt handler", exc_info=True)
                    raise

            # FFW termination is tricky because we need to synchronize the last outcomes of the main and interrupt actions.
            # If a generator is exhausted we know its done. We also may not iterate it again because its prepared state will
            # change
            if has_reached_target_node:
                logger.debug("FFW termination because target node was reached")
                break
            if last_work_tick + 10 < ffw_tick:
                # we'll assume nothing more will happen after 10 idle ticks
                logger.debug("FFW termination because loop was idle")
                if self._program.active_node is not None and self._program.active_node.id != target_node_id:
                    # It would be great if we could always ensure a complete match between
                    # active_node and target_node - but we allow this slight difference - the
                    # test suite passes this whereas the strict comparison breaks quite a few tests

                    # count distances
                    all_nodes = self._program.get_all_nodes()
                    target_index = all_nodes.index(target_node)
                    active_index = all_nodes.index(self._program.active_node)
                    err = f"FFW loop was idle but active node {self._program.active_node} is not the target: " +\
                          f"{target_node} | {active_index=}, {target_index=}"                    
                    if target_node.completed and active_index == target_index + 1:
                        # if the target node is completed, it's ok if active_node is just one step later
                        logger.debug(err + " - but close enough")
                    else:
                        logger.error(err)
                        raise MethodEditError(err)
                break
            if ffw_tick > self.ffw_tick_limit:
                logger.error(f"FFW failed to complete. Aborted after {ffw_tick} iterations.")
                raise MethodEditError(message=f"Internal error. FFW failed to complete. Aborted after {ffw_tick} iterations")

        self._ffw = False
        logger.info("FFW complete")

    def get_marks(self) -> list[str]:
        records: list[tuple[str, int]] = []
        for r in self.runtimeinfo.records:
            if p.MarkNode.is_class_of_name(r.node_class_name):
                completed_states = [st for st in r.states if st.state_name == RuntimeRecordStateEnum.Completed]
                for completed_state in completed_states:
                    end_tick = completed_state.state_tick
                    records.append((completed_state.arguments, end_tick))

        def sort_fn(t: tuple[str, int]) -> int:
            return t[1]

        records.sort(key=sort_fn)
        return [t[0] for t in records]

    def get_node_by_id(self, node_id: str) -> p.Node | None:
        return self._program.get_child_by_id(node_id, include_self=True)

    def inject_node(self, injected_program: p.ProgramNode):
        """ Inject the child nodes of program into the running program in the current scope
        to be executed as the next instruction. """
        node = p.InjectedNode(id=str(uuid.uuid4()))        
        for n in injected_program.children:
            node.append_child(n)
        self._register_interrupt(node)

        # because neither InjectedNode or any of its child nodes are inserted into 
        # the program (yet?), we create a custom null node and record for it
        self.tracking.create_injected_node_records(node)

    def _register_interrupt(self, node: p.NodeWithChildren):
        handler = self._create_interrupt_handler(node)
        assert hasattr(handler, "__name__"), f"Handler {str(handler)} has no name"
        handler_name = getattr(handler, "__name__")
        # Note: we may have to allow overwriting the handler because Watch-in-Alarm cases require it.
        if node.interrupt_registered:
            logger.warning(f"The state for node {node} indicates that it already has a registered interrupt")

        logger.debug(f"Interrupt registered for {node}, handler: {handler_name}")
        self._interrupts_map[node.id] = Interrupt(node, handler)
        node.interrupt_registered = True

        if isinstance(node, p.WatchNode):
            self.context.emitter.emit_on_scope_start(node.id, "Watch", node.arguments)
        if isinstance(node, p.AlarmNode):
            self.context.emitter.emit_on_scope_start(node.id, "Alarm", node.arguments)

    def _create_interrupt_handler(self, node: p.Node) -> NodeGenerator:
        assert isinstance(node, p.SupportsInterrupt), \
            f"Cannot create interrupt for non-interrupt node type {type(node).__name__}"
        if isinstance(node, p.WatchNode):
            return self.visit_WatchNode(node)
        elif isinstance(node, p.AlarmNode):
            return self.visit_AlarmNode(node)
        elif isinstance(node, p.InjectedNode):
            return self.visit(node)
        err = f"Failed to create interrupt handler for node type {type(node).__name__}"
        logger.error(err)
        raise NotImplementedError(err)

    def _unregister_interrupt(self, node: p.Node):
        if not isinstance(node, p.SupportsInterrupt):
            logger.error(f"Node {node} does not support interrupts")
            raise Exception(f"Node {node} does not support interrupts")
        if not isinstance(node, p.NodeWithChildren):
            raise TypeError(f"Node {node} implements SupportsInterrupt but not NodeWithChildren")
        assert isinstance(node, p.Node)
        if node.id in self._interrupts_map.keys():
            del self._interrupts_map[node.id]
            node.interrupt_registered = False
            logger.debug(f"Interrupt handler unregistered for {node}")
        else:
            logger.warning(f"No interrupt for node id {node.id} was found to unregister")

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
        except NodeInterpretationError as ex:
            self.tracking.mark_failed(ex.node)
            raise
        except AssertionError as ae:
            if self._program.active_node is not None:
                self._program.active_node.failed = True
                self.tracking.mark_failed(self._program.active_node)
                raise NodeInterpretationError(self._program.active_node, message=str(ae)) from ae
            raise InterpretationError(message=str(ae)) from ae
        except InterpretationInternalError:
            raise
        except InterpretationError:
            # TODO should we have this? are there node-non-specific general errors? so that we can not try
            # fixing them with an edit? If it is that bad, why isn't it an internal error then?
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
                self._in_interrupt = True
                run_tick(interrupt.actions)
            except StopIteration:
                logger.debug(f"Interrupt generator {interrupt.node} exhausted")
                if isinstance(interrupt.node, p.AlarmNode):
                    logger.debug(f"Restarting completed Alarm {interrupt.node}")
                    interrupt.node.run_count += 1
                    self._unregister_interrupt(interrupt.node)
                    interrupt.node.reset_runtime_state(recursive=True)
                    self._register_interrupt(interrupt.node)
            except NodeInterpretationError as ex:
                ex.node.failed = True
                self.tracking.mark_failed(ex.node)
                raise
            except AssertionError as ae:
                if self._program.active_node is not None:
                    self._program.active_node.failed = True
                    self.tracking.mark_failed(self._program.active_node)
                    raise NodeInterpretationError(self._program.active_node, message=str(ae))
                raise InterpretationError(message=str(ae)) from ae
            except (InterpretationInternalError, InterpretationError):
                logger.error("Interpreter error in interrupt handler", exc_info=True)
                raise
            except Exception as ex:
                logger.error("Unhandled interpretation error in interrupt handler", exc_info=True)
                raise InterpretationError("Interpreter error") from ex
            finally:
                self._in_interrupt = False

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
            time_value_formatted = time_value if len(time_value) < 5 else time_value[0:5]

            try:
                # calculate result of 'value < threshold'
                result = units.compare_values(
                    '<', time_value, time_unit,
                    threshold_value, threshold_unit)
                if result:
                    logger.debug(
                        f"Node {node} is awaiting threshold: {time_value_formatted} of {threshold_value}, " +
                        f"base unit: '{base_unit}'")
                    return True

                logger.debug(
                    f"Node {node} is done awaiting threshold {time_value_formatted} of {threshold_value}, " +
                    f"base unit: '{base_unit}'")
            except Exception as ex:
                raise NodeInterpretationError(
                    node,
                    "Threshold comparison error. Failed to compare " +
                    f"value '{time_value}' to threshold '{threshold_value}'") from ex
        return False

    def _evaluate_condition(self, node: p.NodeWithCondition) -> bool:
        c = node.tag_operator_value
        assert c is not None, "Error in condition"
        assert not c.error, f"Error parsing condition '{node.tag_operator_value_part}'"
        assert c.tag_name, "Error in condition tag"
        assert c.tag_value, "Error in condition value"
        assert self.context.tags.has(c.tag_name), f"Unknown tag '{c.tag_name}' in condition '{node.tag_operator_value_part}'"
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
        # Node iterators must be prepared using visit_ProgramNode(), not visit().
        # This means ProgramNode won't appear here.
        assert not isinstance(node, p.ProgramNode)

        self._program.active_node = node

        def start(node):
            # interrupts are visited multiple times and we only create a new record on the first visit
            record = self.runtimeinfo.get_record_by_node(node)
            if record is None:
                record = self.runtimeinfo.begin_visit(
                    node,
                    self._tick_time, self._tick_number,
                    self.context.tags.as_readonly())
        # use custom name to avoid action name collision with actions in the visit_* methods
        yield NodeAction(node, start, name="visit_start")

        # log all visits
        logger.debug(f"Visiting {node} | {self._in_interrupt=} | {self._ffw=} | {self._tick_time=}")

        # possibly wait for node threshold to expire
        if not node.started and not node.completed:
            if self._is_awaiting_threshold(node):
                self.tracking.mark_awaiting_threshold(node)                

            while self._is_awaiting_threshold(node):
                yield

        # threshold has passed
        node.started = True

        # delegate to concrete visitor method via base method
        yield from super().visit(node)

        def end(node: p.Node):
            record = self.runtimeinfo.get_record_by_node(node.id)
            assert record is not None
            record.set_end_visit(
                self._tick_time, self._tick_number,
                self.context.tags.as_readonly())

        # use custom name to avoid action name collision with actions in the visit_* methods
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
        # avoid advancing into whitespace that is followed by only more whitespace. This improves editability/appendability
        # of sibling nodes, i.e. it remains possible to append lines at the end of the method because the whitespace will
        # remain non-started
        while node.has_only_trailing_whitespace:
            node.started = False
            yield
        node.completed = True


    def visit_MarkNode(self, node: p.MarkNode) -> NodeGenerator:
        def do(node: p.MarkNode):
            logger.info(f"Mark {node.name} running")
            try:
                mark_tag = self.context.tags.get("Mark")
                mark_tag.set_value(node.name, self._tick_time)
            except ValueError:
                logger.error(f"Failed to get Mark tag {node}")

            self.tracking.mark_started(node)
            self.tracking.mark_completed(node)
            node.completed = True
        yield NodeAction(node, do)


    def visit_BatchNode(self, node: p.BatchNode) -> NodeGenerator:
        logger.info(f"Batch {str(node)}")

        def do(node: p.BatchNode):
            try:
                batch_tag = self.context.tags.get("Batch Name")
                batch_tag.set_value(node.name, self._tick_time)
            except ValueError:
                logger.error("Failed to get Batch Name tag")
            self.tracking.mark_started(node)
            self.tracking.mark_completed(node)
            node.completed = True
        yield NodeAction(node, do)


    def visit_MacroNode(self, node: p.MacroNode) -> NodeGenerator:

        def init_define_macro(node: p.MacroNode):
            self.tracking.mark_started(node)
            logger.debug(f"Defining macro '{node}'")
        yield NodeAction(node, init_define_macro)

        # Don't check macro self reference here because
        # - that is an analyzer responsibility
        # - it will be checked before the macro is executed by visit_CallMacroNode

        if not node.is_registered:
            program_node = node.root
            if node.name in program_node.macros.keys():
                logger.warning(f"Re-defining macro '{node.name}'")
            program_node.macros[node.name] = node
            logger.debug(f"Macro '{node}' registered")
            self.tracking.mark_completed(node)
            node.is_registered = True


    def visit_CallMacroNode(self, node: p.CallMacroNode) -> NodeGenerator:

        def call_macro_init(node: p.CallMacroNode):
            self.tracking.mark_started(node)
        yield NodeAction(node, call_macro_init)

        def call_macro_check(node: p.CallMacroNode):
            program_node = node.root
            macro_node = node.root.macros.get(node.name)
            if macro_node is None:
                logger.warning(f'No macro defined with name "{node.name}"')
                available_macros = "None"
                if len(program_node.macros.keys()):
                    available_macros = ", ".join(f'"{macro}"' for macro in program_node.macros.keys())
                self.tracking.mark_failed(node)
                raise NodeInterpretationError(
                    node,
                    f'No macro defined with name "{node.name}". Available macros: {available_macros}.')

            # Check if calling the macro will call the macro.
            # This would incur a cascade of macros which
            # is probably not intended.
            # Make a temporary dict of macros to which
            # this macro is added. This dict is only used
            # to try to determine if the macro will at some
            # point try to call itself.
            temporary_macros = program_node.macros.copy()
            temporary_macros[node.name] = macro_node
            cascade = macro_node.macro_calling_macro(temporary_macros)
            if cascade and node.name in cascade:
                self.tracking.mark_cancelled(node)
                if len(cascade) == 1:
                    logger.warning(f'Macro "{node.name}" calls itself. This is not allowed.')
                    raise NodeInterpretationError(node, f'Macro "{node.name}" calls itself. ' +
                                                        'Unfortunately, this is not allowed.')
                else:
                    path = " which calls ".join(f'macro "{link}"' for link in cascade)
                    logger.warning(f'Macro "{node.name}" calls itself by calling {path}. This is not allowed.')
                    raise NodeInterpretationError(node, f'Macro "{node.name}" calls itself by calling {path}. ' +
                                                        'Unfortunately, this is not allowed.')
        yield NodeAction(node, call_macro_check)

        def increment_start_count(node: p.CallMacroNode):
            macro_node = node.root.macros[node.name]
            macro_node.run_started_count += 1
        yield NodeAction(node, increment_start_count)

        # call the macro by visiting the macro's child nodes
        if not node.activated:
            macro_node = node.root.macros[node.name]
            macro_node.prepare_for_call()
            node.activated = True
            yield from self._visit_children(macro_node)
            macro_node.completed = True

        def call_macro_complete(node: p.CallMacroNode):
            self.tracking.mark_completed(node)
            node.completed = True
        yield NodeAction(node, call_macro_complete)


    def visit_BlockNode(self, node: p.BlockNode) -> NodeGenerator:

        def try_aquire_block_lock(node: p.BlockNode):
            scope = self.stack.peek()
            if isinstance(scope, p.ProgramNode) or scope == node.parent:
                logger.debug(f"Block lock for {node} aquired")
                node.lock_aquired = True

        if not node.lock_aquired:
            while not node.lock_aquired:
                logger.debug(f"Waiting to aquire block lock for {node}")
                try_aquire_block_lock(node)
                if node.lock_aquired:
                    break
                yield

        def push_to_stack(node: p.BlockNode):
            node.lock_aquired = True
            self.stack.push(node)
            self.context.tags[SystemTagName.BLOCK].set_value(node.name, self._tick_number)
            self.context.emitter.emit_on_block_start(node.name, self._tick_number)
            self.context.emitter.emit_on_scope_start(node.id, "Block", node.arguments)
            logger.debug(f"Block Tag set to {node.name}")
        yield NodeAction(node, push_to_stack)

        def emit_scope_activated(node: p.BlockNode):
            self.context.emitter.emit_on_scope_activate(node.id, "Block", node.arguments)
            self.tracking.mark_started(node)
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
        def end_block(node: p.EndBlockNode):
            self.tracking.mark_started(node)
            if not isinstance(self.stack.peek(), p.BlockNode):
                logger.debug(f"No blocks to end for node {node}")
                self.tracking.mark_cancelled(node, update_node=False)
                return
            old_block = self.stack.pop()
            new_block = self.stack.peek()
            logger.debug(f"Ending block {old_block}")
            new_block_name = new_block.name if isinstance(new_block, p.BlockNode) else None
            self.context.tags[SystemTagName.BLOCK].set_value(new_block_name, self._tick_number)
            self.context.emitter.emit_on_block_end(old_block.name, new_block_name or "", self._tick_number)
            old_block.children_complete = True
            old_block.completed = True
            self.tracking.mark_completed(node)
            self.tracking.mark_completed(old_block)
            self._abort_block_interrupts(old_block)
            node.completed = True
        yield NodeAction(node, end_block)


    def visit_EndBlocksNode(self, node: p.EndBlocksNode) -> NodeGenerator:
        def end_blocks(node: p.EndBlocksNode):
            self.tracking.mark_started(node)
            if not isinstance(self.stack.peek(), p.BlockNode):
                logger.debug(f"No blocks to end for node {node}")
                self.tracking.mark_cancelled(node)
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
                self.tracking.mark_completed(old_block)
                self._abort_block_interrupts(old_block)
            node.completed = True
            self.tracking.mark_completed(node)
        yield NodeAction(node, end_blocks)


    def visit_InterpreterCommandNode(self, node: p.InterpreterCommandNode) -> NodeGenerator:  # noqa C901

        def InterpreterCommandNode_start(node):
            self.tracking.mark_started(node)
        yield NodeAction(node, InterpreterCommandNode_start)

        if node.instruction_name == InterpreterCommandEnum.BASE:
            def base(node: p.InterpreterCommandNode):
                valid_units = self.context.base_unit_provider.get_units()
                if node.arguments is None or node.arguments not in valid_units:
                    self.tracking.mark_failed(node)
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
            def run_counter(node: p.InterpreterCommandNode):
                try:
                    new_value = int(node.arguments)
                    logger.debug(f"Run Counter set to {new_value}")
                    self.context.tags[SystemTagName.RUN_COUNTER].set_value(new_value, self._tick_time)
                except ValueError:
                    raise NodeInterpretationError(node, f"Invalid argument '{node.arguments}'. Argument must be an integer")
            yield NodeAction(node, run_counter)

        elif node.instruction_name == InterpreterCommandEnum.WAIT:

            if node.completed:
                if __debug__:
                    assert self._ffw
                return

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
                    record = self.runtimeinfo.get_record_by_node(node.id)
                    assert record is not None
                    record.progress = progress
                yield

        else:  # unknown InterpreterCommandNode instruction
            self.tracking.mark_failed(node)
            raise NodeInterpretationError(node, f"Interpreter command '{node.instruction_name}' is not supported")

        def complete(node: p.InterpreterCommandNode):
            logger.debug(f"Interpreter command Node {node} complete")
            self.tracking.mark_completed(node)
            node.completed = True

        yield NodeAction(node, complete)


    def visit_NotifyNode(self, node: p.NotifyNode):
        def do(node: p.NotifyNode):
            self.context.emitter.emit_on_notify_command(node.arguments)
            self.tracking.mark_started(node)
            self.tracking.mark_completed(node)
            node.completed = True
        yield NodeAction(node, do)


    def visit_EngineCommandNode(self, node: p.EngineCommandNode) -> NodeGenerator:

        def schedule(node: p.EngineCommandNode):
            instance_id = self.tracking.create_node_instance_id(node)

            # Note: Commands can be resident and last multiple ticks.
            # The context (Engine) keeps track of this and we just
            # move on to the next instruction when tick() is invoked.
            # We do, however, provide the instance_id to the context
            # so that it can update the runtime record and node appropriately.
            try:
                logger.debug(f"Executing command '{node}' via engine")
                self.context.schedule_execution(
                    name=node.instruction_name,
                    arguments=node.arguments,
                    instance_id=instance_id)
            except Exception as ex:
                self.tracking.mark_failed(node)
                if isinstance(ex, EngineError):
                    raise
                else:
                    raise NodeInterpretationError(node, "Failed to pass engine command to engine") from ex

        yield NodeAction(node, schedule)


    def visit_SimulateNode(self, node: p.SimulateNode) -> NodeGenerator:

        def simulate_on(node: p.SimulateNode):
            assert node.tag_operator_value
            assert node.tag_operator_value.tag_name
            if node.tag_operator_value.tag_value_numeric and node.tag_operator_value.tag_unit:
                self.context.tags.get(node.tag_operator_value.tag_name).simulate_value_and_unit(
                    node.tag_operator_value.tag_value_numeric,
                    node.tag_operator_value.tag_unit,
                    self._tick_time
                )
            elif node.tag_operator_value.tag_value:
                self.context.tags.get(node.tag_operator_value.tag_name).simulate_value(
                    node.tag_operator_value.tag_value_numeric if node.tag_operator_value.tag_value_numeric else node.tag_operator_value.tag_value,
                    self._tick_number
                )
            else:
                logger.error(f"Unable to simulate {str(node)}")
            self.tracking.mark_started(node)
            self.tracking.mark_completed(node)
            node.completed = True

        yield NodeAction(node, simulate_on)


    def visit_SimulateOffNode(self, node: p.SimulateOffNode) -> NodeGenerator:

        def simulate_off(node: p.SimulateOffNode):
            self.context.tags.get(node.arguments).stop_simulation()
            self.tracking.mark_started(node)
            self.tracking.mark_completed(node)
            node.completed = True

        yield NodeAction(node, simulate_off)


    def visit_UodCommandNode(self, node: p.UodCommandNode) -> NodeGenerator:

        def schedule(node: p.UodCommandNode):
            instance_id = self.tracking.create_node_instance_id(node)

            # Note: Uod Commands can be resident and last multiple ticks just like Engine Commands.
            try:
                logger.debug(f"Executing uod command '{node}' with '{instance_id=}' via engine")
                self.context.schedule_execution(
                    name=node.instruction_name,
                    arguments=node.arguments,
                    instance_id=instance_id)
            except Exception as ex:
                self.tracking.mark_failed(node)
                if isinstance(ex, EngineError):
                    raise
                else:
                    raise NodeInterpretationError(node, "Failed to pass uod command to engine") from ex

        yield NodeAction(node, schedule)


    def visit_WatchNode(self, node: p.WatchNode) -> NodeGenerator:
        return self.visit_WatchOrAlarm(node)


    def visit_AlarmNode(self, node: p.AlarmNode) -> NodeGenerator:
        return self.visit_WatchOrAlarm(node)


    def visit_WatchOrAlarm(self, node: p.WatchNode | p.AlarmNode) -> NodeGenerator:

        if not node.interrupt_registered:
            # Note self._in_interrupt == True is uncommon but valid if watch/alarm is nested inside a watch/alarm
            self._register_interrupt(node)
            yield
            return

        # running from interrupt
        assert self._in_interrupt, "Running visit_WatchOrAlarm body must always occur in an interrupt context"

        def await_condition(node: p.WatchNode | p.AlarmNode):
            # create new instance_id here to allow multiple alarm runs
            self.tracking.create_node_instance_id(node)
            self.tracking.mark_awaiting_condition(node)
            node.awaiting_condition = True

        if not node.awaiting_condition:
            yield NodeAction(node, await_condition)

        def start(node: p.WatchNode | p.AlarmNode):
            scope_type = "Watch" if isinstance(node, p.WatchNode) else "Alarm"
            self.context.emitter.emit_on_scope_activate(node.id, scope_type, node.arguments)
            self.tracking.mark_started(node)


        while not node.activated:
            if node.cancelled:
                # TODO cancel causes emit_on_scope_end to fail, see test_runlog_cancel_watch()
                # self.tracking.mark_cancelled(node)
                # scope_type = "Watch" if isinstance(node, p.WatchNode) else "Alarm"
                # self.context.emitter.emit_on_scope_end(node.id, scope_type, node.arguments)
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

        def complete(node: p.WatchNode | p.AlarmNode):
            self.tracking.mark_completed(node)
            scope_type = "Watch" if isinstance(node, p.WatchNode) else "Alarm"
            self.context.emitter.emit_on_scope_end(node.id, scope_type, node.arguments)
            node.completed = True
        if not node.completed:
            yield NodeAction(node, complete)

        # now idle until a possible method edit which may append child nodes to the Watch


    def visit_InjectedNode(self, node: p.InjectedNode) -> NodeGenerator:
        yield NodeAction(node, self.tracking.mark_started)
        yield from self._visit_children(node)
        yield NodeAction(node, self.tracking.mark_completed)
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
                    self.tracking.mark_started(node)
                    self.tracking.mark_completed(node)
                yield NodeAction(node, noop)
                return

        logger.error(f"Invalid instruction: {str(node)}:\n{node.line}")
        self.tracking.mark_started(node)
        self.tracking.mark_failed(node)
        raise NodeInterpretationError(node, f"Invalid instruction '{node.name}'")

    # def helper methods for node manipulation

    def _try_activate_node(self, node: p.NodeWithCondition):
        assert isinstance(node, p.NodeWithCondition)
        condition_result = False
        if node.cancelled:
            logger.error("Cancel must be handled before _try_active_node")
            return
        elif node.forced:
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


class Tracking():
    """ Manages tracking . API replaces the runtimeinfo API """
    def __init__(self, interpreter: PInterpreter):
        self.interpreter = interpreter
        self.enabled = False
        logger.info(f"Tracking instance {id(self)} created")

    @property
    def runtimeinfo(self) -> RuntimeInfo:
        return self.interpreter.runtimeinfo

    def tags(self) -> TagValueCollection:
        return self.interpreter.context.tags.as_readonly()

    def enable(self):
        logger.info("Tracking enabled")
        self.enabled = True

    def disable(self):
        logger.info("Tracking disabled")
        self.enabled = False

    @property
    def records(self):
        return self.interpreter.runtimeinfo.records_filtered

    def get_runlog(self) -> RunLog:
        return self.interpreter.runtimeinfo.get_runlog()

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
            return self.interpreter.get_node_by_id(node_id)

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
        # Start and Restart operate too early and late for the mark_* methods to work. But it
        # is safe to just skip them as these records are not used later.
        skip_command_names = [EngineCommandEnum.START, EngineCommandEnum.RESTART]
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
            state_values = self.tags()
        else:
            state_values = None
        record._add_state(instance_id, state, self.interpreter._tick_time, self.interpreter._tick_number,
                          state_values=state_values, node=node, command=command)
        info = self.runtimeinfo
        if instance_id not in info._instance_record_map.keys():
            index = info._node_record_map[record.node_id]
            info._instance_record_map[instance_id] = index
