from enum import Enum
from typing import Callable, Iterator, TypeVar
import logging

import openpectus.lang.model.ast as p

logger = logging.getLogger(__name__)

TNode = TypeVar("TNode", bound=p.Node)


class VisitResult(Enum):
    """ The result of an iteration step i.e. visit_*(node) """
    EndTick = 0
    """ Means the tick should end, i.e. the current visit has completed its work for this tick and will continue on the next tick """
    ContinueTick = 1
    """ The visit has completed its work and more work can start immidiately in the same tick. Continue iteration of the generator until EndTick is encountered """
    IteratorExhausted = 2
    """ Iterator is exhausted and cannot currently iterate any further. This may change if a live-edit occurs """


NodeGenerator = Iterator[VisitResult]
""" The generator return type for visitor methods. """


class NodeVisitorGeneric:
    def visit(self, node) -> NodeGenerator:
        yield from self.visit_Node(node)
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        result = visitor(node)

        if __debug__:
            import inspect
            if not inspect.isgenerator(result):
                raise TypeError("Visitor methods must return NodeGenerator")

        yield from result

    def generic_visit(self, node):
        raise TypeError('No visit_{} method'.format(type(node).__name__))

    def visit_Node(self, node: p.Node) -> NodeGenerator:
        yield VisitResult.EndTick


class NodeVisitor(NodeVisitorGeneric):
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

    def visit_BatchNode(self, node: p.BatchNode) -> NodeGenerator:
        yield VisitResult.EndTick

    def visit_WatchNode(self, node: p.WatchNode) -> NodeGenerator:
        yield from self._visit_children(node)

    def visit_AlarmNode(self, node: p.AlarmNode) -> NodeGenerator:
        yield from self._visit_children(node)

    def visit_MacroNode(self, node: p.MacroNode) -> NodeGenerator:
        yield from self._visit_children(node)

    def visit_CallMacroNode(self, node: p.CallMacroNode) -> NodeGenerator:
        yield VisitResult.EndTick

    def visit_InterpreterCommandNode(self, node: p.InterpreterCommandNode) -> NodeGenerator:
        yield VisitResult.EndTick

    def visit_NotifyNode(self, node: p.NotifyNode) -> NodeGenerator:
        yield VisitResult.EndTick

    def visit_EngineCommandNode(self, node: p.EngineCommandNode) -> NodeGenerator:
        yield VisitResult.EndTick

    def visit_UodCommandNode(self, node: p.UodCommandNode) -> NodeGenerator:
        yield VisitResult.EndTick

    def visit_ErrorInstructionNode(self, node: p.ErrorInstructionNode) -> NodeGenerator:
        yield VisitResult.EndTick

    def visit_SimulateNode(self, node: p.SimulateNode) -> NodeGenerator:
        yield VisitResult.EndTick

    def visit_SimulateOffNode(self, node: p.SimulateOffNode) -> NodeGenerator:
        yield VisitResult.EndTick
