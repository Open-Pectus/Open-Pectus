from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Callable, Iterable, Sequence

from opruntime.lang import program as p
from opruntime.lang.models import InterpreterState, InterruptState, SePath
from opruntime.lang.parser import Method, create_method_parser
from opruntime.lang.visitor import NodeGenerator, NodeVisitor, VisitResult
from opruntime.lang.hotswap import HotSwapVisitor, MethodState, MethodEditError

logger = logging.getLogger(__name__)


class Interrupt:
    def __init__(self, node: p.NodeWithChildren, actions: NodeGenerator):
        self.node = node
        self.actions = actions
        self.sep = SePath()
        self.sep.push(node, "interrupt")

    def __str__(self):
        return f"Interrupt(node={self.node})"

    # possibly add sep (structural execution path)

class Interpreter(NodeVisitor):
    def __init__(self):
        self._tick_time = -1
        self._tick_number = -1
        self.method: Method | None = None
        self.program: p.ProgramNode | None = None
        self.generator: NodeGenerator | None = None
        self._interrupts_map: dict[str, Interrupt] = {}
        self._in_interrupt = False
        self.marks: list[str] = []
        self.main_sep: SePath = SePath()
        self._sep: SePath = self.main_sep
        """ The structural execution path of the interpreter's active instruction """
        self.on_visit_start: Callable[[p.Node], None] = lambda node: None

    @property
    def interrupts(self) -> Sequence[Interrupt]:
        return list(self._interrupts_map.values())

    @property
    def sep(self) -> SePath:
        """ A reference to the current sep, main or interrupt. """
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


    def set_method(self, method: Method):
        self.method = method
        parser = create_method_parser(method)
        self.program = parser.parse_method(method)
        self.main_sep = SePath()
        self._sep: SePath = self.main_sep

    def get_cold_state(self) -> InterpreterState:
        if self.program is None:
            raise ValueError("Program has not been set")
        if self.method is None:
            raise ValueError("Program has not been set")
        return InterpreterState(
            export_date=datetime.now(timezone.utc),
            method=self.method.clone(),
            tree_state=self.program.extract_tree_state(),
            main_sep=self.sep.clone(),
            interrupt_states=[InterruptState(intr.node.id) for intr in self._interrupts_map.values()],
            macros_registered=[node.id for node in self.program.macros.values()]
        )

    def from_merge(self, new_method: Method) -> "Interpreter":
        assert self.method is not None
        assert self.program is not None
        new_state = self.create_merge_state(new_method)         # create state that represents the merge - does not apply it
        return Interpreter.from_cold_state(new_state)   # here the state is applied to the program

    def create_merge_state(self, new_method: Method) -> InterpreterState:
        assert self.method is not None
        assert self.program is not None
        method = self.method
        program = self.program
        state = self.get_cold_state()

        # ideally, we shouldn't use an interpreter instance for this ...
        instance = Interpreter()
        instance.set_method(new_method)
        assert instance.program is not None
        new_program = instance.program

        if new_program.revision == 0:
            new_program.revision = program.revision + 1
            logger.debug(f"New method has no version specified, using {new_program.revision} " +
                         "which is the old version incremented by 1")

        if new_program.has_error(recursive=True):
            logger.warning("Target merge method has parse errors")

        # check method state preconditions: started or completed lines may not be edited
        # possibly add idle status here
        method_state = Interpreter._get_method_state(program)
        for new_line in new_method.lines:
            if new_line.id in method_state.executed_line_ids or new_line.id in method_state.started_line_ids:
                cur_line = next((line for line in method.lines if line.id == new_line.id), None)
                if cur_line is not None and cur_line.content != new_line.content:
                    raise MethodEditError(f"""
Line with id '{new_line.id}' may not be edited, because it has already started
Original line: '{cur_line.content}'
Edited line:   '{new_line.content}'
""")

        logger.debug("Applying hotswap visitor to create merged state")
        swapper = HotSwapVisitor(old_program=program, old_state=state)
        main_generator = swapper.run(new_program)
        while True:
            try:
                main_result = next(main_generator)
                if main_result == VisitResult.IteratorExhausted:
                    break
            except StopIteration:
                # logger.debug("Main generator is exhausted")
                break

        # stich the new state together from values we know and values swapper knows
        new_state = InterpreterState(
            export_date=datetime.now(timezone.utc),
            method=new_method,
            tree_state=swapper.new_state.tree_state,
            main_sep=swapper.new_state.main_sep,
            interrupt_states=swapper.new_state.interrupt_states,
            macros_registered=swapper.new_state.macros_registered,
        )

        return new_state

    @staticmethod
    def from_cold_state(cold_state: InterpreterState) -> "Interpreter":
        logger.debug(f"Creating new interpreter from cold state, method version: {cold_state.method.version}")
        instance = Interpreter()
        if instance.method is not None:
            raise AssertionError("Should only apply cold state to a fresh interpreter with no existing method")

        instance.set_method(cold_state.method)
        assert instance.program is not None

        # Apply the state to all nodes. In case of merge, the state has been 
        # patched by the hotswap visitor.
        logger.debug("Applying program state")
        try:
            instance.program.apply_tree_state(cold_state.tree_state)
        except ValueError as ex:
            logger.error(f"Failed to apply state to nodes. This indicates an error in cold_state.tree_state. Ex:{ex}")
            raise

        # apply interpreter state - plain application of explicit state, nothing magical here
        logger.debug("Applying interpreter state")

        logger.debug(f"Applying interrupt state ({len(cold_state.interrupt_states)})")
        for interrupt_state in cold_state.interrupt_states:
            node = instance.program.get_child_by_id(interrupt_state.node_id)
            if node is None:
                logger.error(f"Interrupt for node_id {interrupt_state.node_id} cannot be recreated. Node was not found")
                continue
            # interrupt_state.sep - what to do?
            if not isinstance(node, p.NodeWithChildren):
                logger.error(f"Interrupt for node_id {interrupt_state.node_id} cannot be recreated." +
                             f" Node has invalid type: {type(node)}")
                continue
            instance._register_interrupt(node, warn_if_exists=False)

        logger.debug(f"Applying macro state ({len(cold_state.macros_registered)})")
        for node_id in cold_state.macros_registered:
            node = instance.program.get_child_by_id(node_id)
            if node is None:
                logger.error(f"Macro for node_id {node_id} cannot be registered. Node was not found")
                continue
            if not isinstance(node, p.MacroNode):
                logger.error(f"Macro with node_id {node_id} cannot be registered." +
                             f" Node has invalid type: {type(node)}")
                continue
            instance._register_macro(node, warn_if_exists=False)

        logger.debug("Completed applying state")
        return instance

    @staticmethod
    def _get_method_state(program: p.ProgramNode) -> MethodState:
        all_nodes = program.get_all_nodes()
        method_state = MethodState()
        for node in all_nodes:
            if node.completed:
                method_state.executed_line_ids.append(node.id)
            elif node.started:
                method_state.started_line_ids.append(node.id)
            # # injected node ids are created as negative integers
            # id_int = as_int(node.id)
            # if id_int is not None and id_int < 0:
            #     method_state.injected_line_ids.append(node.id)
        return method_state

# region Tick

    def tick(self, tick_time: float, tick_number: int):

        # this runs the tick with subticks in proper order
        for _ in self.tick_iterate_subticks(tick_time, tick_number):
            pass

        # Below is the previous implementation - with incorrect sub tick order across main/interrupt iterators

        # self._tick_time = tick_time
        # self._tick_number = tick_number

        # if self.generator is None:
        #     logger.debug("Creating generator")
        #     self.generator = self.create_generator()

        # logger.debug(f"Run tick {tick_number}, main")
        # self._run_generator_tick(self.generator)

        # interrupts = list(self._interrupts_map.values())
        # logger.debug(f"Run tick {tick_number}, interrupt nodes: {' | '.join((i.node.name for i in interrupts))}")

        # for interrupt in interrupts:  # iterate on a copy because executing may mutate self._interrupts_map
        #     try:
        #         self._in_interrupt = True
        #         logger.debug(f"Run tick {tick_number}, interrupt node: {interrupt.node}")
        #         self._run_generator_tick(interrupt.actions)
        #     finally:
        #         self._in_interrupt = False

    def _run_generator_tick(self, generator: NodeGenerator):
        # NOTE: The sub-tick order here differs from that of tick_iterate_subticks.
        # This just runs subticks of the given generator out of sequence of any other generators
        try:
            while True:
                result = next(generator)
                if result == VisitResult.EndTick or result == VisitResult.IteratorExhausted:
                    return

            # result = next(generator)
            # Need this loop to ffw - but then it would require syncronization, right?            
            # If we skipped the loop it would just take a little longer to ffw but it would still work, no?
            # while result == VisitResult.ContinueTick:
            #     result = next(generator)
        except StopIteration:
            pass

    def tick_iterate_subticks(self, tick_time: float, tick_number: int) -> Iterable[SePath]:
        self._tick_time = tick_time
        self._tick_number = tick_number

        if self.generator is None:
            # logger.debug("Creating generator")
            assert self.program is not None
            self.generator = self.visit(self.program)

        # Run 1 tick worth of sub-ticks of main generator and each interrupt generator. This means make as many next()
        # calls as it takes for each generator to return VisitResult.EndTick or VisitResult.IteratorExhausted. This        
        # enables each tick to function as synchronization point between main and interrupt generators.

        # The purpose of sub-ticks is
        # 1. To specify when ticks occur. This is necessary because the ticks control the timing of interpretation
        # 2. Allow tests to have sub-tick granularity to inspect and assert conditions

        while True:
            try:
                main_result = next(self.generator)
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
                    raise
                finally:
                    self._in_interrupt = False
                    self._sep = self.main_sep

            yield self.main_sep

# endregion

# region General visit

# (spacer line for nested region below)
# (spacer line for nested region below)
# region > Foo
# endregion

    def visit(self, node: p.Node) -> NodeGenerator:
        if node.completed:
            logger.debug(f"Visit node: {node}, in_interrupt: {self._in_interrupt} skipped, node is complete")
            yield VisitResult.ContinueTick
            return

        self.on_visit_start(node)

        self.sep.push(node)
        #logger.debug(f"Enter node: {node}, in_interrupt: {self._in_interrupt}")
        assert self.program is not None

        node.started = True
        result = super().visit(node)
        yield from result

        #logger.debug(f"Leave node: {node}, in_interrupt: {self._in_interrupt}")
        self.sep.pop()


    def visit_ProgramNode(self, node: p.ProgramNode) -> NodeGenerator:
        if node.completed:
            # current tests do not care which - return or yield
            logger.debug(f"Visit ProgramNode: {node} skipped, interrupt: {self._in_interrupt}, node is complete")
            yield VisitResult.ContinueTick
            return
        else:
            yield from self._visit_children(node)

        logger.debug("ProgramNode now idle")
        if self.main_sep.path != "root":
            logger.error(f"Main path expected to contain only 'root' - was {self.main_sep}")
            raise Exception(f"Main path expected to contain only 'root' - was {self.main_sep}")

        while True:
            yield VisitResult.EndTick


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

# endregion

# region Concrete visits

    def visit_BlankNode(self, node: p.BlankNode) -> NodeGenerator:
        if node.test_has_only_trailing_whitespace:
            # node is idle. started is back to False so _get_method_state
            # doesn't block editing the line, see #
            # a better option might be to set idle and make that info available when
            # validating edit and not depend on whitespace for editing idle instructions
            node.started = False
            logger.debug(f"{node} is now idle")

        while node.test_has_only_trailing_whitespace:
            yield VisitResult.EndTick

        node.started = True
        yield VisitResult.ContinueTick

        node.completed = True
        yield VisitResult.ContinueTick

    def visit_AbcNode(self, node: p.AbcNode) -> NodeGenerator:
        while not node.completed:
            if node.abc_state == "":
                logger.debug("Abc -> A")
                node.abc_state = "A"
                yield VisitResult.EndTick
            elif node.abc_state == "A":
                logger.debug("Abc -> B")
                node.abc_state = "B"
                yield VisitResult.EndTick
            elif node.abc_state == "B":
                logger.debug("Abc -> C")
                node.abc_state = "C"
                yield VisitResult.EndTick
            elif node.abc_state == "C":
                logger.debug("Abc -> Done")
                node.completed = True
                yield VisitResult.ContinueTick

    def visit_MarkNode(self, node: p.MarkNode) -> NodeGenerator:
        if node.completed:
            raise Exception(f"We should not be called when completed is set, node: {node}")

        self.marks.append(node.arguments)
        node.completed = True
        yield VisitResult.EndTick

    def visit_BlockNode(self, node: p.BlockNode) -> NodeGenerator:

        def try_acquire_lock():
            if node.lock_acquired:
                return
            assert self.program is not None
            # We can take the lock iff
            # 1) There are no locked blocks or 2) all locked blocks are ancesters of node
            parents = node.parents
            for block in self.program.get_locked_blocks():
                if block not in parents:
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
                pass
            while not node.lock_acquired:
                try_acquire_lock()
                if node.lock_acquired:
                    self.sep.pop()
                    yield VisitResult.ContinueTick
                    logger.debug(f"{node.key} acquired block lock")
                    break
                else:
                    yield VisitResult.EndTick

            yield from self._visit_children(node)

            # await visit_EndBlockNode or visit_EndBlockNodes to set block_ended
            while not node.block_ended:
                #logger.debug(f"node {node} waiting to be marked with block_ended")
                yield VisitResult.EndTick

        # release lock
        node.lock_acquired = False
        # clean up state
        node.children_complete = True
        node.child_index = len(node.children)
        node.completed = True

    def visit_EndBlockNode(self, node: p.EndBlockNode) -> NodeGenerator:
        # Find the block to end. If node has a Block ancestor, that is the one to end. If not,
        # there may be locked blocks in interrupts/main other that the current interrupt/main.
        # Lookup locked blocks and find the innermost Block node which is the first to end.

        old_block: p.BlockNode | None = None
        new_block: p.BlockNode | None = None

        assert self.program is not None
        locked_blocks = self.program.get_locked_blocks()
        locked_block_keys = [b.key for b in locked_blocks]
        logger.warning("Locked blocks: " + '\n'.join(locked_block_keys))
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

        if old_block is None:
            logger.warning("EndBlock found no block to end")
        else:
            old_block.block_ended = True
            self._abort_block_interrupts(old_block)
            logger.debug(f"EndBlockNode {node.key} has ended block {old_block.key}")
            logger.debug(f"New active block is: {new_block.key if new_block is not None else "No active block"}")

        node.completed = True
        yield VisitResult.EndTick

    def visit_WatchNode(self, node: p.WatchNode) -> NodeGenerator:
        if not node.interrupt_registered:
            self._register_interrupt(node)
            yield VisitResult.EndTick
            return

        # Now running in interrupt
        if not self._in_interrupt:  # during cold-state run, we can end up here - maybe could fix that with another flag, ???
            logger.debug("Entered interrupt part of visit_WatchNode without being in interrupt")
            yield VisitResult.EndTick
            return

        assert self._in_interrupt

        self.sep.push(node, "await_activation")
        while not node.activated:
            self._try_activate_node(node)
            yield VisitResult.EndTick
        self.sep.pop()

        self.sep.push(node, "invocation")
        yield VisitResult.ContinueTick  # allows run_until_path with invocation part
        yield from self._visit_children(node)
        self.sep.pop()
        node.completed = True
        yield VisitResult.ContinueTick

        # if self._in_interrupt:
        #     node.completed = True  # why is this necessary, again? - TODO no test coverage. if it is necessary, cover it
        
        # Note this special case of interrupt_registered not registered while called from an interrupt
        #if not node.interrupt_registered:
            # Note self._in_interrupt == True is uncommon but valid if watch/alarm is nested inside a watch/alarm
            # ...

        # consider this instead
        # if not node.interrupt_registered:
        #     self._register_interrupt(node)
        #     raise StopIteration  # or not? hmm, tricky... we still want to continue processing sibling/following nodes
        # else:
        #     yield from self.visit_WatchOrAlarm(node)
        #     node.completed = True

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

        self.sep.push(node, "await_activation")
        while not node.activated:
            self._try_activate_node(node)
            yield VisitResult.EndTick
        self.sep.pop()

        self.sep.push(node, f"invocation.{node.run_count}")
        yield VisitResult.ContinueTick  # allows run_until_path with invocation part
        yield from self._visit_children(node)
        self.sep.pop()
        node.completed = True
        yield VisitResult.ContinueTick

        logger.debug(f"Restarting completed Alarm {node}")
        node.run_count += 1
        self._unregister_interrupt(node)
        # TODO reset_runtime_state is very generic. Maybe prepare_new_run()
        # Is used for this case and in interpreter.stop. In the stop case we might want to do more,
        # like resetting 
        # TODO not yet figured out
        node.reset_runtime_state(recursive=True)
        self._register_interrupt(node)

        # if this is set, alarm body will not execute in interrupt - but it is never set then? guess that is ok
        # what does that mean for runlog?
        # node.completed = True


    def visit_MacroNode(self, node: p.MacroNode) -> NodeGenerator:
        if not node.is_registered:
            self._register_macro(node)
        node.completed = True
        yield VisitResult.EndTick

    def visit_CallMacroNode(self, node: p.CallMacroNode) -> NodeGenerator:
        macro_node = node.root.macros.get(node.macro_name)
        if macro_node is None:
            logger.error(f"Macro '{node.macro_name}' not found")
            raise Exception(f"Macro '{node.macro_name}' not found")

        if macro_node.run_started_count <= macro_node.run_completed_count:
            macro_node.reset_runtime_state(recursive=True)
            macro_node.run_started_count += 1
        else:
            pass  # complete a started macro call

        self.sep.push(macro_node, f"invocation.{macro_node.run_started_count - 1}")
        yield from self._visit_children(macro_node)
        macro_node.run_completed_count += 1
        self.sep.pop()

        macro_node.completed = True
        node.completed = True

        yield VisitResult.EndTick

    def visit_ErrorInstructionNode(self, node: p.ErrorInstructionNode) -> NodeGenerator:
        # enable the Noop (no operation) instruction used in tests
        # logger.debug("ErrorInstructionNode: " + str(node))
        if node.name == "Noop":
            try:
                count = int(node.arguments or "1")
            except Exception:
                logger.warning(f"Noop argument '{node.arguments}' is not a number. Defaulting to count=1")
                count = 1
            logger.debug(f"Noop: Initialized to a total of {count} ticks")
            for index in range(count):
                # Note: iteration state is non-persistent because it does not use node state,
                # unlike child iteration which uses child_index. This just means that in live-edit,
                # iteration just continues because interpreter maintains the iterator state, whereas
                # when starting from persisted state, it starts over.
                logger.debug(f"Noop: Executing tick {index} of {count}")
                yield VisitResult.EndTick
            logger.debug(f"Noop: completed {count} ticks")
            return

        logger.error(f"Invalid instruction: {str(node)}:\n{node.line}")
        raise Exception(node, f"Invalid instruction '{node.name}'")
# endregion

# region Interrupts

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

    def _unregister_interrupt(self, node: p.NodeWithChildren, warn_on_no_registration=True):
        node.interrupt_registered = False
        if node.id in self._interrupts_map.keys():
            del self._interrupts_map[node.id]
            logger.debug(f"Interrupt handler unregistered for {node}")
        else:
            if warn_on_no_registration:
                logger.warning(f"No interrupt for node id {node.id} was found to unregister")

    def _register_macro(self, node: p.MacroNode, warn_if_exists=True):
        if node.is_registered and warn_if_exists:
            logger.warning(f"Macro node {node.key} is marked as already registered")
        program_node = node.root
        macro_name = node.macro_name
        if macro_name in program_node.macros.keys():
            existing_key = program_node.macros[macro_name].key
            logger.info(f"Re-defining macro '{macro_name}' from {existing_key} to {node.key}")
        program_node.macros[macro_name] = node
        logger.debug(f"Macro '{node.macro_name}' registered to {node.key}")
        node.is_registered = True

    def _abort_block_interrupts(self, block: p.BlockNode):
        logger.debug(f"Cancelling any interrupts for nodes in block '{block}'")
        descendants = block.get_child_nodes(recursive=True)
        for interrupt in self.interrupts:
            for child in descendants:
                if child.id == interrupt.node.id:
                    logger.debug(f"Cancelling interrupt for {child} in block")
                    interrupt.node.children_complete = True
                    self._unregister_interrupt(interrupt.node)

# endregion

    def _try_activate_node(self, node: p.NodeWithCondition):
        assert isinstance(node, p.NodeWithCondition)
        condition_result = False
        # if node.cancelled:
        #     logger.error("Cancel must be handled before _try_active_node")
        #     return
        # elif node.forced:
        #     logger.info(f"Instruction {node} forced")
        #     condition_result = True
        if False:
            pass
        else:
            try:
                condition_result = self._evaluate_condition(node)
            except AssertionError:
                raise
            except Exception as ex:
                raise ValueError(node, "Error evaluating condition: " + str(ex)) from ex
            logger.debug(f"Condition for node {node} evaluated: {condition_result}")
        if condition_result:
            node.activated = True

    def _evaluate_condition(self, node: p.Node) -> bool:
        logger.debug(f"Evaluating conditon, test mode, args: {node.arguments}")
        if isinstance(node, p.AlarmNode):
            # TODO would be better to use something like max_run_count=5 so it can be customized - if we need it
            if "max_run_count_5" in node.arguments.lower() and node.run_count >= 5:
                logger.info(f"Condition evaluation bail for Alarm, {node.run_count=}")
                return False
        if "true" in node.arguments.lower():
            #logger.debug("Condition evaluated to True")
            return True
        else:
            #logger.debug("Condition evaluated to False")
            return False
