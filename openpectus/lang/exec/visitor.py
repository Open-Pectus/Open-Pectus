
import inspect
from typing import Any, Generator
import openpectus.lang.model.ast as p


class NodeVisitorGeneric:
    def visit(self, node):
        self.visit_Node(node)
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        result = visitor(node)

        if __debug__:
            if not inspect.isgenerator(result):
                raise TypeError("Visitor methods must be generators")

        yield from result

    def generic_visit(self, node):
        raise TypeError('No visit_{} method'.format(type(node).__name__))

    def visit_Node(self, node: p.Node):
        ...


NodeGenerator = Generator[None, Any, Any]
""" The generator return type for visitor methods. """


class NodeVisitor(NodeVisitorGeneric):
    def visit_ProgramNode(self, node: p.ProgramNode) -> NodeGenerator:
        yield from self._visit_children(node)

    def _visit_children(self, node: p.NodeWithChildren) -> NodeGenerator:
        for child in node.children:
            yield from self.visit(child)

    def visit_BlankNode(self, node: p.BlankNode) -> NodeGenerator:
        yield from ()

    def visit_CommentNode(self, node: p.CommentNode) -> NodeGenerator:
        yield from ()

    def visit_MarkNode(self, node: p.MarkNode) -> NodeGenerator:
        yield

    def visit_BlockNode(self, node: p.BlockNode) -> NodeGenerator:
        yield from self._visit_children(node)

    def visit_EndBlockNode(self, node: p.EndBlockNode) -> NodeGenerator:
        yield

    def visit_EndBlocksNode(self, node: p.EndBlocksNode) -> NodeGenerator:
        yield

    def visit_BatchNode(self, node: p.BatchNode) -> NodeGenerator:
        yield

    def visit_WatchNode(self, node: p.WatchNode) -> NodeGenerator:
        yield from self._visit_children(node)

    def visit_AlarmNode(self, node: p.AlarmNode) -> NodeGenerator:
        yield from self._visit_children(node)

    def visit_MacroNode(self, node: p.MacroNode) -> NodeGenerator:
        yield from self._visit_children(node)

    def visit_CallMacroNode(self, node: p.CallMacroNode) -> NodeGenerator:
        yield

    def visit_InterpreterCommandNode(self, node: p.InterpreterCommandNode) -> NodeGenerator:
        yield

    def visit_EngineCommandNode(self, node: p.EngineCommandNode) -> NodeGenerator:
        yield

    def visit_UodCommandNode(self, node: p.UodCommandNode) -> NodeGenerator:
        yield

    def visit_ErrorInstructionNode(self, node: p.ErrorInstructionNode) -> NodeGenerator:
        yield
