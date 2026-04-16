from __future__ import annotations

import logging
from typing import Iterable, Sequence
import uuid
from typing_extensions import override

from openpectus.lang.exec.argument_specification import ArgSpec
from openpectus.lang.exec.events import EventEmitter
from openpectus.lang.exec.regex import REGEX_DURATION, get_duration_end
from openpectus.lang.exec.tracking import Tracking
import openpectus.lang.exec.units as units
from openpectus.lang.exec.base_unit import BaseUnitProvider
from openpectus.lang.exec.commands import InterpreterCommandEnum
from openpectus.lang.exec.errors import (
    EngineError, InterpretationError, InterpretationInternalError, MethodEditError, NodeInterpretationError
)
from openpectus.lang.exec.runlog import RuntimeInfo, RuntimeRecordStateEnum
from openpectus.lang.exec.tags import TagCollection, SystemTagName
from openpectus.lang.exec.visitor import NodeGenerator, NodeVisitor, VisitResult
import openpectus.lang.model.ast as p
from openpectus.lang.exec.interpreter_models import (
    SePath, InterpreterState,
    Interrupt, InterruptState,
)

logger = logging.getLogger(__name__)

term_uod = "Unit Operation Definition file."


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


class PInterpreter(NodeVisitor):
    def __init__(self, program: p.ProgramNode, context: InterpreterContext, runtimeinfo: RuntimeInfo,
                 tracking_enabled: bool = False) -> None:
        self._program = program
        self.context = context
        self._interrupts_map: dict[str, Interrupt] = {}

        self.start_time: float = 0
        self._tick_time: float = 0
        self._tick_number: int = -1

        self._generator: NodeGenerator | None = None
        self._in_interrupt = False

        self.runtimeinfo: RuntimeInfo = runtimeinfo
        self.tracking: Tracking = Tracking(
            self.runtimeinfo, self.context.tags.as_readonly(), self.get_node_by_id, tracking_enabled)

        self.main_sep: SePath = SePath()
        self._sep: SePath = self.main_sep

        logger.debug("Interpreter initialized")


    @property
    def sep(self) -> SePath:
        """ A reference to the current path, main or interrupt. """
        return self._sep

    def has_path(self, path: str):
        """ Returns True if the main visitor or one of the interrupt visitors match the path.

        Note: The check is made against the current program state. """
        if self.main_sep.matches(path):
            return True
        for interrupt in self._interrupts_map.values():
            if interrupt.sep.matches(path):
                return True
        return False

# region Creation and state

    # these are all in MethodManager
    
# endregion Creation Creation and state

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


    def stop(self):
        self._program.reset_runtime_state(recursive=True)
    

# region Tick

    def tick(self, tick_time: float, tick_number: int):

        # this runs the tick with subticks in proper order
        for _ in self.tick_iterate_subticks(tick_time, tick_number):
            pass

    def tick_iterate_subticks(self, tick_time: float, tick_number: int) -> Iterable[SePath]:
        self._tick_time = tick_time
        self._tick_number = tick_number

        if self._generator is None:
            # logger.debug("Creating generator")
            assert self._program is not None
            self._generator = self.visit(self._program)

        # Run 1 tick worth of sub-ticks of main generator and each interrupt generator. This means make as many next()
        # calls as it takes for each generator to return VisitResult.EndTick or VisitResult.IteratorExhausted. This        
        # enables each tick to function as synchronization point between main and interrupt generators. Additionally it
        # makes it safe concurrency-wise, to perform live-edit at any time, except during a tick.

        # The purpose of sub-ticks is
        # 1. To let visit methods specify when ticks occur. This is necessary because the ticks control the timing of interpretation
        # 2. Allow tests to inspect path with sub-tick granularity and assert conditions based on it.

        while True:
            try:
                main_result = next(self._generator)
                if main_result == VisitResult.ContinueTick:
                    yield self.main_sep
                else:
                    yield self.main_sep
                    break
            except StopIteration:
                logger.debug("Main generator is exhausted")
                break
            # yield

        for interrupt in self.interrupts:  # iterate on the property copy because executing may mutate self._interrupts_map
            while True:
                try:
                    self._in_interrupt = True
                    self._sep = interrupt.sep
                    result = next(interrupt.actions)
                    if result == VisitResult.ContinueTick:
                        yield interrupt.sep
                    else:
                        yield interrupt.sep
                        break
                except StopIteration:
                    break
                except Exception:
                    logger.error(f"An exception occurred in interrupt sub_tick {interrupt}", exc_info=True)
                    # TODO should store exception and let the tick complete before raising it
                    raise
                finally:
                    self._in_interrupt = False
                    self._sep = self.main_sep

            yield self.main_sep        

# endregion Tick

    def old_tick(self, tick_time: float, tick_number: int):  # noqa C901
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

# region General visit

    @override
    def visit(self, node: p.Node) -> NodeGenerator:
        if node.completed:
            logger.debug(f"Visit node: {node}, in_interrupt: {self._in_interrupt} skipped, node is complete")
            yield VisitResult.ContinueTick
            return

        record = self.runtimeinfo.get_record_by_node(node.id)
        if record is None:
            record = self.runtimeinfo.begin_visit(
                node,
                self._tick_time, self._tick_number,
                self.context.tags.as_readonly())
        # possibly wait for node threshold to expire
        if not node.started and not node.completed:
            if self._is_awaiting_threshold(node):
                self.tracking.mark_awaiting_threshold(node)

            while self._is_awaiting_threshold(node):
                yield VisitResult.EndTick

        # threshold has passed
        node.started = True
        self.sep.push(node)
        #logger.debug(f"Enter node: {node}, in_interrupt: {self._in_interrupt}")
        
        result = super().visit(node)
        yield from result

        #logger.debug(f"Leave node: {node}, in_interrupt: {self._in_interrupt}")
        self.sep.pop()

        record = self.runtimeinfo.get_record_by_node(node.id)
        assert record is not None
        record.set_end_visit(  # why this and not tracking?
            self._tick_time, self._tick_number,
            self.context.tags.as_readonly())

    @override
    def visit_ProgramNode(self, node: p.ProgramNode) -> NodeGenerator:
        if node.completed:
            # current tests do not care which - return or yield
            logger.debug(f"Visit ProgramNode: {node} skipped, interrupt: {self._in_interrupt}, node is complete")
            yield VisitResult.ContinueTick
            return

        self.context.emitter.emit_on_scope_start(node.id, "Program", "")
        self.context.emitter.emit_on_scope_activate(node.id, "Program", "")

        yield from self._visit_children(node)

        # Note: This event means that the last line of the method is complete.
        # The method may change later by an edit, so it doesn't necessarily mean
        # that the method has ended.
        self.context.emitter.emit_on_method_end()
        logger.debug("ProgramNode now idle")

        if self.main_sep.path != "root":
            logger.error(f"Main path expected to contain only 'root' - was {self.main_sep}")
            raise Exception(f"Main path expected to contain only 'root' - was {self.main_sep}")

        # Never return from the visit of ProgramNode. This makes it possible to inject or edit code at the bottom of 
        # the method which will then be added as new child nodes of the ProgramNode.
        # There may also be commands that still run, in particular Alarm which runs indefinitely.
        # In particular, we don emit scope end for the root scope
        while True:
            yield VisitResult.EndTick

    @override
    def _visit_children(self, node: p.NodeWithChildren) -> NodeGenerator:
        if node.completed:
            logger.debug(f"Visit children of node: {node} skipped, interrupt: {self._in_interrupt}, node is complete")
            yield VisitResult.ContinueTick
            return
        if node.children_complete:
            logger.debug(f"Visit children of node: {node} skipped, interrupt: {self._in_interrupt}, children_complete is True")
            yield VisitResult.ContinueTick
            return

        for inx, child in enumerate(node.children):
            if node.children_complete or node.completed:
                logger.debug(f"Breaking child visit loop for node {node.key} before visit | {node.children_complete=} | {node.completed=}")
                break
            if inx < node.child_index:
                logger.debug(f"Child node loop for {node.key} skipping {child.key=} because {inx=} < {node.child_index=}")
                continue

            if isinstance(node, p.BlockNode) and node.block_ended:
                logger.debug(f"Breaking child visit loop for block {node.key} that has ended. {node.child_index=}")
                break

            child_result = self.visit(child)
            self.sep.push(node, f"child.{node.child_index}")
            yield from child_result
            self.sep.pop()
            node.child_index += 1

        node.children_complete = True
    
# endregion General visit


# region Concrete visits

    def visit_BlankNode(self, node: p.BlankNode) -> NodeGenerator:
        # avoid advancing into whitespace that is followed by only more whitespace. This improves editability/appendability
        # of sibling nodes, i.e. it remains possible to append lines at the end of the method because the whitespace will
        # remain non-started
        if node.has_only_trailing_whitespace:
            node.started = False
            self.sep.push(node, "idle")

        while node.has_only_trailing_whitespace:            
            yield VisitResult.EndTick
        
        node.started = True
        self.sep.pop()
        yield VisitResult.ContinueTick

        node.completed = True
        yield VisitResult.ContinueTick


    def visit_MarkNode(self, node: p.MarkNode) -> NodeGenerator:
        assert not node.completed, f"In concrete visitor method for node {node.key}, node.complete was set. This is unexpected"

        logger.info(f"Mark {node.name} running")
        try:
            mark_tag = self.context.tags.get("Mark")
            mark_tag.set_value(node.name, self._tick_time)
        except ValueError:
            logger.error(f"Failed to get Mark tag {node}")

        self.tracking.mark_started(node)
        yield VisitResult.ContinueTick

        self.tracking.mark_completed(node)
        node.completed = True
        yield VisitResult.EndTick


    def visit_BatchNode(self, node: p.BatchNode) -> NodeGenerator:
        logger.info(f"Batch {str(node)}")

        try:
            batch_tag = self.context.tags.get("Batch Name")
            batch_tag.set_value(node.name, self._tick_time)
        except ValueError:
            logger.error("Failed to get Batch Name tag")
        
        self.tracking.mark_started(node)
        yield VisitResult.ContinueTick

        self.tracking.mark_completed(node)
        node.completed = True
        yield VisitResult.EndTick


    def visit_MacroNode(self, node: p.MacroNode) -> NodeGenerator:
        if not node.is_registered:
            self._register_macro(node)

        self.tracking.mark_started(node)
        yield VisitResult.ContinueTick

        self.tracking.mark_completed(node)
        node.completed = True
        yield VisitResult.EndTick


    def visit_CallMacroNode(self, node: p.CallMacroNode) -> NodeGenerator:
        program_node = self._program
        macro_name = node.macro_name
        macro_node = program_node.macros.get(macro_name)        
        if macro_node is None:
            logger.warning(f"Macro '{macro_name}' not found")
            self.tracking.mark_failed(node)
            available_macros = ", ".join(f'"{macro}"' for macro in program_node.macros.keys())
            raise NodeInterpretationError(
                node,
                f'No macro defined with name "{macro_name}". Available macros: {available_macros}.')

        # Check if calling the macro will call the macro.
        # This would incur a cascade of macros which is probably not intended.
        # Make a temporary dict of macros to which this macro is added. This dict is only used
        # to determine if the macro will at some point try to call itself.
        temporary_macros = program_node.macros.copy()
        temporary_macros[macro_name] = macro_node
        cascade = macro_node.macro_calling_macro(temporary_macros)
        if cascade and macro_name in cascade:
            #self.tracking.mark_cancelled(node) # need to be consistent with the above - either cancel or fail
            self.tracking.mark_failed(node)
            if len(cascade) == 1:
                logger.warning(f'Macro "{macro_name}" calls itself. This is not allowed.')
                raise NodeInterpretationError(node, f'Macro "{macro_name}" calls itself. ' +
                                                    'Unfortunately, this is not allowed.')
            else:
                path = " which calls ".join(f'macro "{link}"' for link in cascade)
                logger.warning(f'Macro "{macro_name}" calls itself by calling {path}. This is not allowed.')
                raise NodeInterpretationError(node, f'Macro "{macro_name}" calls itself by calling {path}. ' +
                                                    'Unfortunately, this is not allowed.')

        # prepare invoke
        if macro_node.run_started_count <= macro_node.run_completed_count:
            macro_node.reset_runtime_state(recursive=True)
            macro_node.run_started_count += 1
            self.tracking.mark_started(node)
        else:
            pass  # complete a started macro call

        # invoke macro by visiting the macro node's children
        self.sep.push(macro_node, f"invocation.{macro_node.run_started_count - 1}")
        yield from self._visit_children(macro_node)
        macro_node.run_completed_count += 1
        self.sep.pop()

        self.tracking.mark_completed(node)
        # TODO also track macro_node as completed?
        macro_node.completed = True
        node.completed = True
        yield VisitResult.EndTick


    def visit_BlockNode(self, node: p.BlockNode) -> NodeGenerator:
        def try_acquire_lock():
            if node.lock_acquired:
                return
            # We can take the lock iff
            # 1) There are no locked blocks or 2) all locked blocks are ancestors of node
            ancestors = node.parents
            for block in self._program.get_locked_blocks():
                if block not in ancestors:
                    logger.debug(f"Block {node.key} could not acquire lock, {block.key} holds it")
                    return
            node.lock_acquired = True

        if node.completed:
            logger.warning(f"Block {node.key} already completed")
            return

        if not node.block_ended:
            if not node.lock_acquired:
                self.sep.push(node, "acquire_lock")
                yield VisitResult.ContinueTick                
            
            while not node.lock_acquired:
                try_acquire_lock()
                
                if node.lock_acquired:
                    self.sep.pop()
                    self.context.tags[SystemTagName.BLOCK].set_value(node.name, self._tick_number)
                    self.context.emitter.emit_on_block_start(node.name, self._tick_number)
                    self.context.emitter.emit_on_scope_start(node.id, "Block", node.arguments)
                    logger.debug(f"Block Tag set to {node.name}")

                    yield VisitResult.ContinueTick
                    logger.debug(f"{node.key} acquired block lock")

                    self.context.emitter.emit_on_scope_activate(node.id, "Block", node.arguments)
                    self.tracking.mark_started(node)
                    break
                else:
                    yield VisitResult.EndTick

            yield from self._visit_children(node)

            # await visit_EndBlockNode or visit_EndBlockNodes to set block_ended
            while not node.block_ended:
                # waiting for block_ended signal which is set by End block(s)
                yield VisitResult.EndTick

        # release lock
        node.lock_acquired = False

        # TODO check whether this is necessary
        # allow possible interrrupts time to acquire the block lock before the node's following-siblings are executed
        #yield VisitResult.EndTick

        # clean up state
        # TODO Note - previously this was done in End block(s) - may need to move a few things between here and End block(s)
        node.children_complete = True
        node.child_index = len(node.children)
        node.completed = True
        self.tracking.mark_completed(node)
        self.context.emitter.emit_on_scope_end(node.id, "Block", node.arguments)


    def visit_EndBlockNode(self, node: p.EndBlockNode) -> NodeGenerator:
        # Find the block to end. If node has a Block ancestor, that is the one to end. If not,
        # there may be locked blocks in interrupts/main other that the current interrupt/main.
        # Lookup locked blocks and find the innermost Block node which is the first to end.

        old_block: p.BlockNode | None = None
        new_block: p.BlockNode | None = None

        locked_blocks = self._program.get_locked_blocks()
        locked_block_keys = [b.key for b in locked_blocks]
        logger.debug("Locked blocks: " + '\n'.join(locked_block_keys))
        if len(locked_blocks) == 0:
            pass
        elif len(locked_blocks) == 1:
            old_block = locked_blocks[0]
        else:
            # There are multiple locked blocks. This can only occur if they are contained in each other so the
            # innermost block is the first to be unlocked. When sorted by key_path, the innermost block is the last
            locked_blocks.sort(key=lambda node: node.key_path)
            old_block = locked_blocks[-1]
            new_block = locked_blocks[-2]

            if __debug__:
                # Lets verify that
                last_block_ancestors = old_block.parents
                for i in range(0, len(locked_blocks) - 1):
                    assert locked_blocks[i] in last_block_ancestors

        self.tracking.mark_started(node)

        if old_block is None:
            logger.warning("EndBlock found no block to end")
            self.tracking.mark_cancelled(node, update_node=False) # TODO: was done previously - should we still do this?
        else:
            new_block_name = new_block.name if new_block is not None else None
            self.context.tags[SystemTagName.BLOCK].set_value(new_block_name, self._tick_number)
            self.context.emitter.emit_on_block_end(old_block.name, new_block_name or "", self._tick_number)

            old_block.block_ended = True
            self._abort_block_interrupts(old_block)
            logger.debug(f"EndBlockNode {node.key} has ended block {old_block.key}")
            logger.debug(f"New active block is: {new_block.key if new_block is not None else "No active block"}")
            # NOTE: block change may not be complete until the old block visit completes ... 
            # maybe move something around - before visit_EndBlock did all the clean up
            # old_block.children_complete = True
            # old_block.completed = True
            # self.tracking.mark_completed(old_block)

        self.tracking.mark_completed(node)
        node.completed = True
        yield VisitResult.EndTick


    def visit_EndBlocksNode(self, node: p.EndBlocksNode) -> NodeGenerator:
        raise NotImplementedError("TODO implement visit_EndBlocksNode")
    
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
        self.tracking.mark_started(node)

        if node.instruction_name == InterpreterCommandEnum.BASE:
            valid_units = self.context.base_unit_provider.get_units()
            if node.arguments is None or node.arguments not in valid_units:
                self.tracking.mark_failed(node)
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
            self.sep.push(node, "waiting")
            while self._tick_time < duration_end_time and not node.forced:
                if duration > 0:
                    progress = (self._tick_time - node.wait_start_time) / duration
                    record = self.runtimeinfo.get_record_by_node(node.id)
                    assert record is not None
                    record.progress = progress
                yield VisitResult.EndTick
            self._sep.pop()            

        else:  # unknown InterpreterCommandNode instruction
            self.tracking.mark_failed(node)
            raise NodeInterpretationError(node, f"Interpreter command '{node.instruction_name}' is not supported")

        logger.debug(f"Interpreter command Node {node} complete")
        self.tracking.mark_completed(node)
        node.completed = True
        yield VisitResult.EndTick


    def visit_NotifyNode(self, node: p.NotifyNode) -> NodeGenerator:
        self.context.emitter.emit_on_notify_command(node.arguments)
        self.tracking.mark_started(node)
        self.tracking.mark_completed(node)
        node.completed = True
        yield VisitResult.EndTick


    def visit_EngineCommandNode(self, node: p.EngineCommandNode) -> NodeGenerator:
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

        yield VisitResult.EndTick


    def visit_SimulateNode(self, node: p.SimulateNode) -> NodeGenerator:
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
        yield VisitResult.EndTick


    def visit_SimulateOffNode(self, node: p.SimulateOffNode) -> NodeGenerator:
        self.context.tags.get(node.arguments).stop_simulation()
        self.tracking.mark_started(node)
        self.tracking.mark_completed(node)
        node.completed = True
        yield VisitResult.EndTick


    def visit_UodCommandNode(self, node: p.UodCommandNode) -> NodeGenerator:
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

        yield VisitResult.EndTick


    def visit_WatchNode(self, node: p.WatchNode) -> NodeGenerator:
        if not node.interrupt_registered:
            self._register_interrupt(node)
            yield VisitResult.EndTick
            return

        # Now running in interrupt
        if not self._in_interrupt:  # during cold-state run, we can end up here - maybe could fix that with another flag, ???
            logger.warning("Entered interrupt part of visit_WatchNode without being in interrupt")
            yield VisitResult.EndTick
            return

        assert self._in_interrupt

        if not node.activated:
            self.tracking.create_node_instance_id(node)
            self.tracking.mark_awaiting_condition(node)
            self.sep.push(node, "await_activation")
            while not node.activated:
                self._try_activate_node(node)
                yield VisitResult.EndTick
            self.sep.pop()

        self.sep.push(node, "invocation")
        yield VisitResult.ContinueTick  # allows waiting for invocation path        
        self.context.emitter.emit_on_scope_activate(node.id, "Watch", node.arguments)
        self.tracking.mark_started(node)
        yield from self._visit_children(node)
        self.sep.pop()

        self.tracking.mark_completed(node)        
        self.context.emitter.emit_on_scope_end(node.id, "Watch", node.arguments)
        node.completed = True
        yield VisitResult.ContinueTick


    def visit_AlarmNode(self, node: p.AlarmNode) -> NodeGenerator:
        if not node.interrupt_registered:
            # Note self._in_interrupt == True is uncommon but valid if watch/alarm is nested inside a watch/alarm
            self._register_interrupt(node)
            yield VisitResult.EndTick
            return

        # Now running in interrupt
        if not self._in_interrupt:  # during cold-state run, we can end up here - maybe could fix that with another flag, ???
            logger.warning("Entered interrupt part of visit_WatchOrAlarm without being in interrupt")
            yield VisitResult.EndTick
            return

        assert self._in_interrupt

        # not sure how to even use awaiting_condition
        # if not node.awaiting_condition:
        #     self.tracking.create_node_instance_id(node)
        #     self.tracking.mark_awaiting_condition(node)
        #     node.awaiting_condition = True

        if not node.activated:
            self.tracking.create_node_instance_id(node)
            self.tracking.mark_awaiting_condition(node)
            self.sep.push(node, "await_activation")
            while not node.activated:
                self._try_activate_node(node)
                yield VisitResult.EndTick
            self.sep.pop()

        self.sep.push(node, f"invocation.{node.run_count}")        
        self.context.emitter.emit_on_scope_activate(node.id, "Alarm", node.arguments)
        self.tracking.mark_started(node)
        yield VisitResult.ContinueTick  # allows waiting for invocation path

        yield from self._visit_children(node)
        self.sep.pop()
        #node.completed = True
        
        yield VisitResult.ContinueTick


        self.tracking.mark_completed(node)
        self.context.emitter.emit_on_scope_end(node.id, "Alarm", node.arguments)

        logger.debug(f"Re-register interrupt for completed Alarm {node.key}")
        node.run_count += 1
        self._unregister_interrupt(node)
        node.reset_runtime_state(recursive=True)
        self._register_interrupt(node)

        # if this is set, alarm body will not execute in interrupt - but it is never set then? guess that is ok
        # what does that mean for runlog?
        # node.completed = True

        yield VisitResult.EndTick


    def visit_InjectedNode(self, node: p.InjectedNode) -> NodeGenerator:
        self.tracking.mark_started(node)
        
        yield from self._visit_children(node)
        
        self.tracking.mark_completed(node)
        node.completed = True
        yield VisitResult.EndTick


    def visit_CommentNode(self, node: p.CommentNode) -> NodeGenerator:
        # avoid advancing generator into whitespace-only code lines
        if node.has_only_trailing_whitespace:
            node.started = False
            self.sep.push(node, "idle")

        while node.has_only_trailing_whitespace:            
            yield VisitResult.EndTick
        
        node.started = True
        self.sep.pop()
        yield VisitResult.ContinueTick

        node.completed = True
        yield VisitResult.ContinueTick


    def visit_ErrorInstructionNode(self, node: p.ErrorInstructionNode) -> NodeGenerator:
        if __debug__:
            # enable the Noop (no operation) instruction used in tests
            if node.instruction_name == "Noop":
                self.tracking.mark_started(node)
                yield VisitResult.ContinueTick
                self.tracking.mark_completed(node)
                yield VisitResult.EndTick
                return

        logger.error(f"Invalid instruction: {str(node)}:\n{node.line}")
        self.tracking.mark_started(node)
        self.tracking.mark_failed(node)
        raise NodeInterpretationError(node, f"Invalid instruction '{node.name}'")

# endregion Concrete visits


# region Interrupts

    @property
    def interrupts(self) -> Sequence[Interrupt]:
        return list(self._interrupts_map.values())


    def _register_interrupt(self, node: p.NodeWithChildren, warn_if_exists=True):
        handler = self.visit(node)
        assert hasattr(handler, "__name__"), f"Handler {str(handler)} has no name"
        handler_name = getattr(handler, "__name__")
        # Note: we may have to allow overwriting the handler because Watch-in-Alarm cases require it.
        if node.interrupt_registered and warn_if_exists:
            logger.warning(f"The state for node {node} indicates that it already has a registered interrupt")
        if node.id in (i.node.id for i in self._interrupts_map.values()):
            logger.warning(f"Overwriting existing interrupt for node {node}")

        logger.debug(f"Interrupt registered for {node}, handler: {handler_name}")
        self._interrupts_map[node.id] = Interrupt(node, handler)
        node.interrupt_registered = True

        # TODO: Do we need this?!
        if isinstance(node, p.WatchNode):
            self.context.emitter.emit_on_scope_start(node.id, "Watch", node.arguments)
        if isinstance(node, p.AlarmNode):
            self.context.emitter.emit_on_scope_start(node.id, "Alarm", node.arguments)


    def _unregister_interrupt(self, node: p.NodeWithChildren, warn_on_no_registration=True):
        node.interrupt_registered = False
        if node.id in self._interrupts_map.keys():
            del self._interrupts_map[node.id]            
            logger.debug(f"Interrupt handler unregistered for {node}")
        else:
            if warn_on_no_registration:
                logger.warning(f"No interrupt for node id {node.id} was found to unregister")


    def _abort_block_interrupts(self, block: p.BlockNode):
        logger.debug(f"Cancelling any interrupts for nodes in block '{block}'")
        descendants = block.get_child_nodes(recursive=True)
        for interrupt in self.interrupts:
            for child in descendants:
                if child.id == interrupt.node.id:
                    logger.debug(f"Cancelling interrupt for {child} in block")
                    interrupt.node.children_complete = True
                    self._unregister_interrupt(interrupt.node)

# endregion Interrupts

    def _register_macro(self, node: p.MacroNode, warn_if_exists=True):
        if node.is_registered and warn_if_exists:
            logger.warning(f"Macro node {node.key} is marked as already registered")
        program_node = self._program
        macro_name = node.macro_name
        if macro_name in program_node.macros.keys():
            existing_key = program_node.macros[macro_name].key
            logger.info(f"Re-defining macro '{macro_name}' from {existing_key} to {node.key}")
        program_node.macros[macro_name] = node
        logger.debug(f"Macro '{node.macro_name}' registered to {node.key}")
        node.is_registered = True


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
