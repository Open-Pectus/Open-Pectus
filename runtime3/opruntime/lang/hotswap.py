from dataclasses import dataclass, field
import logging

from opruntime.lang import program as p
from opruntime.lang.models import InterpreterState, InterruptState, SePath
from opruntime.lang.visitor import NodeGenerator, NodeVisitor

logger = logging.getLogger(__name__)

@dataclass
class MethodState():
    started_line_ids: list[str] = field(default_factory=list)
    executed_line_ids: list[str] = field(default_factory=list)
    # injected_line_ids: list[str] = field(default_factory=list)
    # failed_line_ids: list[str] = field(default_factory=list)


class MethodEditError(Exception):
    ...


@dataclass
class SomeInterpreterState:
    """ A subset of InterpreterState """
    tree_state: dict[str, p.NodeState] = field(default_factory=dict)
    main_sep: SePath = field(default_factory=SePath)
    macros_registered: list[str] = field(default_factory=list)
    interrupt_states: list[InterruptState] = field(default_factory=list)

class HotSwapVisitor(NodeVisitor):
    """ A visitor that produces the tree_state that matches a method merge.

    Notes: The visitor does not mutate either of the programs or the old state.
    It merely collects the state to apply in self.new_state.tree_state. It can
    then be applied afterwards to finalize the merge (by Interpreter.from_state())
    """
    def __init__(self, old_program: p.ProgramNode, old_state: InterpreterState):
        super().__init__()
        self.old_program: p.ProgramNode = old_program
        self.old_state: InterpreterState = old_state
        self.new_state: SomeInterpreterState = SomeInterpreterState()
        self.new_state.macros_registered = old_state.macros_registered
        self.new_state.interrupt_states = old_state.interrupt_states

    def run(self, program: p.ProgramNode) -> NodeGenerator:
        return self.visit(program)

    def visit(self, node) -> NodeGenerator:
        logger.debug(f"Visit node {node}")

        old_node = self.old_program.get_child_by_id(node.id)
        if old_node is None:
            logger.debug(f"Node {node.key} is added and thus has no state from old program")
            return

        old_node_is_whitespace = old_node.__class__ in [p.BlankNode, p.CommentNode]
        same_class = old_node.__class__.__name__ == node.__class__.__name__
        if not same_class and old_node.started:
            logger.error(f"Merge failed for Node {node.key}." +
                         f"Old node was started but its class {old_node.__class__.__name__} " +
                         f"does not match new node class {node.__class__.__name__}")
            raise MethodEditError(f"Node {old_node} was edited to be {node} of a different class. " +
                                  "This is not a supported kind of edit")
        else:
            should_apply_state = True
            if not same_class:  # corner case regarding idle/whitespace
                if old_node_is_whitespace:
                    should_apply_state = False
                else:
                    raise MethodEditError(
                        f"Node class mismatch, old class: {old_node.__class__}, new class: {node.__class__}")

            if should_apply_state:
                old_node_state = self.old_state.tree_state.get(node.id)
                if old_node_state is not None:
                    logger.debug(f"Applying old state to node {node}")
                    # save state to tree state so it can be applied leter
                    if not node.can_load_state(old_node_state):
                        logger.error(f"Cannot load state from {old_node_state["class_name"]} into {node.__class__}")
                        raise MethodEditError("State error")
                    self.new_state.tree_state[node.id] = old_node_state
                else:
                    # is this supposed to happen?
                    logger.warning(f"No old state found to apply to node {node}")
            else:
                logger.debug(f"No state applied to node {node}")

        # call concrete node type visitor method
        result = super().visit(node)
        yield from result


    def _visit_children(self, node: p.NodeWithChildren) -> NodeGenerator:
        if node.completed:
            raise Exception("Unexpected call to _visit_children when node is completed")

        old_node = self.old_program.get_child_by_id(node.id)
        if old_node is not None:
            # in the case that child nodes have been added, we need to clear 'children_complete' in the new state
            # so the new nodes are not skipped
            assert isinstance(old_node, p.NodeWithChildren)
            if old_node.children_complete:
                if len(node.children) > len(old_node.children):
                    self.new_state.tree_state[node.id]["children_complete"] = False  # type: ignore

        for child in node.children:
            yield from self.visit(child)
