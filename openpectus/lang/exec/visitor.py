
import inspect
from typing import Any, Callable, Generator
import openpectus.lang.model.ast as p


class NodeAction():
    """ Represents an action (of possibly many) to perform when interpreting a node. Allows
    side effect free visits of an ast tree.  """

    def __init__(self, node: p.Node, action: Callable[[p.Node], None], name: str = "", tick_break: bool = False):
        self.node = node
        self.action = action
        self.tick_break = tick_break

        if name == "":
            if action is None:
                raise ValueError("Argument 'action' was None")
            action_name = action.__name__
            if action_name == "<lambda>":
                if name == "":
                    raise ValueError("When passing a lambda as action, the name argument must be provided and be " +
                                     "unique for the calling method")
            self.action_name = action_name
        else:
            self.action_name = name

    def execute(self):
        if self.action_name in self.node.action_history:
            raise ValueError(f"The action '{self.action_name}' for node {self.node} has already been executed")
        self.action(self.node)
        self.node.action_history.append(self.action_name)


NodeGenerator = Generator[NodeAction | None, Any, Any]
""" The generator return type for visitor methods. """


class NodeVisitorGeneric:
    def visit(self, node):
        self.visit_Node(node)
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        result = visitor(node)
        yield from result

    def generic_visit(self, node):
        raise TypeError('No visit_{} method'.format(type(node).__name__))

    def visit_Node(self, node: p.Node):
        ...



def run_tick(gen: NodeGenerator):
    """ Execute one interpretation tick """
    while True:
        x = next(gen)
        if isinstance(x, NodeAction):
            x.execute()
            if x.tick_break:
                break
        else:
            break



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
