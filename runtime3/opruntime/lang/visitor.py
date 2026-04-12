
from enum import Enum
import inspect
from typing import Iterator

import opruntime.lang.program as p


class Foo:
    def __init__(self, node: p.Node):
        self.node = node


class VisitResult(Enum):
    """ The result of an iteration step i.e. visit_*(node) """
    EndTick = 0
    """ Means the tick should end, i.e. the current visit has completed its work for this tick and will continue on the next tick """
    ContinueTick = 1
    """ The visit has completed its work and more work can start immidiately in the same tick. Continue iteration of the generator until EndTick is encountered """
    IteratorExhausted = 2
    """ Iterator is exhausted and cannot currently iterate any further. This may change if a live-edit occurs """
    # This is too complex. Instead require that visit methods set node.completed when they are done. this is just like any
    # other node state they set. Is tricky for alarm+watch
    #NodeCompleted = 3
    #""" The node visit has completed. Signal to set node.completed = True. """

# Note: It is not clear what each step must do:
# - visit
# - concrete visit
# - _visit_children 
# options:
# set node state, e.g. node.started, node.completed
# return EndTick or ContinueTick
# handle EndTick or ContinueTick before returning it
# Doing this systematically is vital for node states to be set properly so that importing tree state will just work (tm)
# This means that visit and _visit_children must make sure to set eg. node.completed and that the iterating code must not be tasked 
# with this ...


#VisitResult = p.Node | None
NodeGenerator = Iterator[VisitResult]
""" None means continue in current tick, else the tick ends"""



class NodeVisitorGeneric:
    def visit(self, node) -> NodeGenerator:
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        result = visitor(node)

        if not inspect.isgenerator(result):
            raise TypeError("Visitor methods must return NodeGenerator")

        yield from result

    def generic_visit(self, node):
        t = type(node)
        raise TypeError(f"No 'visit_{t.__name__}' method for node: {node} of type '{t}'")




# the only purpose we have for generator to yield a node, is the retry command case,
# for which a "this node + the rest" generator can be easily built. But we still need to start over
# which also covers the retry case. So it seams reasonable to skip the node from the generator type.


class NodeVisitor(NodeVisitorGeneric):
    # def create_generator(self, program: p.ProgramNode) -> NodeGenerator:
    #     yield from self.visit_ProgramNode(program)

    def visit(self, node: p.Node) -> NodeGenerator:
        result = super().visit(node)

        if not inspect.isgenerator(result):
            raise TypeError("Visit methods must return NodeGenerator result")
        yield from result

    def visit_ProgramNode(self, node: p.ProgramNode) -> NodeGenerator:
        yield from self._visit_children(node)

    def _visit_children(self, node: p.NodeWithChildren) -> NodeGenerator:
        for child in node.children:
            yield from self.visit(child)

    def visit_BlankNode(self, node: p.BlankNode) -> NodeGenerator:
        yield VisitResult.EndTick

    def visit_CommentNode(self, node: p.CommentNode) -> NodeGenerator:
        yield VisitResult.EndTick

    def visit_MarkNode(self, node: p.MarkNode) -> NodeGenerator:
        yield VisitResult.EndTick

    def visit_BlockNode(self, node: p.BlockNode) -> NodeGenerator:
        yield from self._visit_children(node)

    def visit_EndBlockNode(self, node: p.EndBlockNode) -> NodeGenerator:
        yield VisitResult.EndTick

    def visit_EndBlocksNode(self, node: p.EndBlocksNode) -> NodeGenerator:
        yield VisitResult.EndTick

    def visit_WatchNode(self, node: p.WatchNode) -> NodeGenerator:
        yield from self._visit_children(node)

    def visit_AlarmNode(self, node: p.AlarmNode) -> NodeGenerator:
        yield from self._visit_children(node)

    def visit_MacroNode(self, node: p.MacroNode) -> NodeGenerator:
        yield from self._visit_children(node)

    def visit_CallMacroNode(self, node: p.CallMacroNode) -> NodeGenerator:
        yield VisitResult.EndTick

    def visit_ErrorInstructionNode(self, node: p.ErrorInstructionNode) -> NodeGenerator:
        yield VisitResult.EndTick

    def visit_AbcNode(self, node: p.AbcNode) -> NodeGenerator:
        yield VisitResult.EndTick

def create_generator(visitor: NodeVisitor, program: p.ProgramNode) -> NodeGenerator:
    yield from visitor.visit_ProgramNode(program)


class HotSwapVisitor():
    """ Defines the interface for hot swapping / live editing.

    House keeping tasks:
    - interrupts, registration
    - macro, registration
    - alarm, registration
    - watch
    - block
    When replacing or deleting a node we need to consider the above tasks for that node and for any descendant nodes
    it may have... This may involve walking the trees in unison...

    We need a more solid understanding of nodes with multiple executions, about any global state and what gets reset
    before and additional runs (i.e. what should reset_runtime_state() do and should we have another variant of it).
    And since this is all nodes, we should have instance count on all, not just the ones causing multiple executions,
    like Alarm and Macro
    Macro also has prepare_for_call that calls reset_runtime_state.
    """

    # either this is the entry point or we have a designated hot_swap_ProgramNode - that's probably best

    def hot_swap(self, node: p.Node, new_node: p.Node):
        method_name = 'hot_swap_' + type(node).__name__
        swapper = getattr(self, method_name, self.generic_visit)
        swapper(node, new_node)

    def generic_visit(self, node: p.Node, new_node: p.Node):
        raise TypeError('No hot_swap_{} method'.format(type(node).__name__))

    def hot_swap_active_descendant(self, node: p.Node, new_node: p.Node, active_parents: list[p.NodeWithChildren]):
        ...
    
    def hot_swap_active_path(self, node, new_node, ec):
        # use this name instead of hot_swap_active_descendant
        # generic method that handles most/simple cases
        ...

    def hot_swap_active_path_Macro(self, node, new_node, ec):
        # override for nodes that need special care
        ...

    ...

    def hot_swap_inactive_child(self, node: p.Node, new_node: p.Node, before_active: bool):
        ...

    def hot_swap_delete(self, node: p.Node):
        ...

    def hot_swap_append(self, parent: p.NodeWithChildren, new_child: p.Node):
        ...
