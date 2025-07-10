from typing import Any, Callable, Generator, TypeVar
import logging

import openpectus.lang.model.ast as p

logger = logging.getLogger(__name__)

TNode = TypeVar("TNode", bound=p.Node)


class NodeAction():
    """ Represents an action (of possibly many) to perform when interpreting a node. Allows
    side effect free visits of an ast tree.  """

    def __init__(self, node: TNode, action: Callable[[TNode], None], name: str = "", tick_break: bool = False):
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
            logger.error(f"The action '{self.action_name}' for node {self.node} has already been executed")
            raise ValueError(f"The action '{self.action_name}' for node {self.node} has already been executed")
        logger.debug(f"Executing action '{self.action_name}' for node {self.node}")
        self.action(self.node)
        self.node.action_history.append(self.action_name)


NullableActionResult = NodeAction | None
NodeGenerator = Generator[NullableActionResult, Any, Any]
""" The generator return type for visitor methods. """


class NodeVisitorGeneric:
    def visit(self, node):
        yield from self.visit_Node(node)
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        result = visitor(node)
        yield from result

    def generic_visit(self, node):
        raise TypeError('No visit_{} method'.format(type(node).__name__))

    def visit_Node(self, node: p.Node) -> NodeGenerator:
        yield from ()



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


def run_ffw_tick(gen: NodeGenerator, interrupt_node_callback: Callable[[NodeAction], None]) -> bool | NodeAction:
    """ Advance the generator a single tick while skipping execution.

    Calls interrupt_node_callback if it encounters a node that may require interrupt registration.
    
    Return value:
        - node action
            if the generator has reached an action whose name was not in action history. This
            means that ffw should complete and the action should be executed before resuming
            normal method excution.
        - False
            if tick_break or None was encountered
        - True
            if the generator was exhausted"""
    while True:
        try:
            x = next(gen)
            if isinstance(x, NodeAction):
                if isinstance(x.node, p.SupportsInterrupt):
                    interrupt_node_callback(x)
                if x.action_name not in x.node.action_history:
                    logger.info(f"FFW about to complete, action '{x.action_name}' not in history for node {x.node}")
                    # We got one step too far, x needs to be executed
                    return x
                if x.tick_break:
                    break
            else:
                break
        except StopIteration:
            return True
    return False


TContent = TypeVar('TContent')


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

    def visit_NotifyNode(self, node: p.NotifyNode) -> NodeGenerator:
        yield

    def visit_EngineCommandNode(self, node: p.EngineCommandNode) -> NodeGenerator:
        yield

    def visit_UodCommandNode(self, node: p.UodCommandNode) -> NodeGenerator:
        yield

    def visit_ErrorInstructionNode(self, node: p.ErrorInstructionNode) -> NodeGenerator:
        yield

    def visit_SimulateNode(self, node: p.SimulateNode) -> NodeGenerator:
        yield

    def visit_SimulateOffNode(self, node: p.SimulateOffNode) -> NodeGenerator:
        yield
