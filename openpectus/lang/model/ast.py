from __future__ import annotations
from typing import Any, Self, Type, TypeVar


class Position:
    empty: Position

    def __init__(self, line: int, character: int):
        self.line: int = line   # todo define 0-1 based. should probably change from before to just match lsp
        self.character: int = character  # start index = indentation

    def is_empty(self) -> bool:
        return self == Position.empty

    def __eq__(self, value):
        if value is None or not isinstance(value, Position):
            return False
        return self.line == value.line and self.character == value.character

    def with_character(self, character: int) -> Position:
        return Position(line=self.line, character=character)

    def __str__(self):
        return f"Position(line: {self.line}, char: {self.character})"


Position.empty = Position(line=-1, character=-1)


class Range:
    empty: Range

    def __init__(self, start: Position, end: Position):
        self.start = start
        self.end = end

    def is_empty(self) -> bool:
        return self == Range.empty

    def with_end(self, position: Position) -> Range:
        return Range(
            start=self.start,
            end=position)

    def __str__(self):
        return f"{self.start} - {self.end}"


Range.empty = Range(start=Position.empty, end=Position.empty)


class NodeIdGenerator:
    def create_id(self, node: Node) -> str:
        ...


# Impl note: using dict because it is json serializable. TypedDict also works
class NodeState(dict[str, Any]):
    id: str
    class_name: str
    name: str
    started: bool
    completed: bool


TNode = TypeVar("TNode", bound="Node")


class SupportCancelForce:
    """ Defines data for cancel and force operations that control interpretation behavior. """
    def __init__(self):
        self._cancellable: bool = False
        self._cancelled: bool = False
        self._forcible: bool = True
        self._forced: bool = False

    @property
    def cancellable(self) -> bool:
        """ Whether the node is cancellable in its current state. Virtual property. """
        return self._cancellable and not self._cancelled and not self._forced

    @property
    def cancelled(self) -> bool:
        """ Whether the node has been cancelled. Virtual property. """
        return self._cancelled

    def cancel(self):
        if self.cancellable:
            self._cancelled = True

    @property
    def forcible(self) -> bool:
        """ Whether the node is forcible in its current state. Virtual property. """
        return self._forcible and not self._forced and not self._cancelled

    @property
    def forced(self) -> bool:
        """ Whether the node has been forced. Virtual property. """
        return self._forced

    def force(self):
        if self.forcible:
            self._forced = True


class Node(SupportCancelForce):
    instruction_names: list[str] = []
    """ Specifies which node the parser should instantiate for a given instruction name(s) """

    def __init__(self, position=Position.empty, id=""):
        super().__init__()

        self.parent: NodeWithChildren | None = None
        self.id: str = id
        self.position: Position = position
        self.instruction_part: str = ""
        self.threshold_part: str = ""
        self.arguments_part: str = ""
        self.arguments: str = ""
        self.arguments_range: Range = Range.empty
        self.comment_part: str = ""

        self.threshold: float | None = None
        self.indent_error: bool = False

        self.errors: list[Error] = []

        # interpretation state
        self.started: bool = False
        self.completed: bool = False

    @property
    def name(self) -> str:
        return self.arguments

    @property
    def instruction_name(self) -> str:
        return self.instruction_part.strip()

    @property
    def runlog_name(self) -> str | None:
        return self.display_name

    @property
    def display_name(self) -> str:
        args = ": " + self.arguments if len(self.arguments) > 0 else ""
        return self.instruction_name + args

    def has_children(self) -> bool:
        return False

    def get_child_by_id(self, id: str) -> Node | None:
        if self.has_children():
            assert isinstance(self, NodeWithChildren)
            for child in self.children:
                match = child.get_child_by_id(id)
                if match is not None:
                    return match

    def can_load_state(self, state: NodeState) -> bool:
        """ Determine whether state is valid for this kind of node """
        return state.class_name == self.__class__.__name__

    def apply_state(self, state: NodeState):
        if not self.can_load_state(state):
            raise ValueError(f"Cannot load state from {state.class_name} into {self.__class__}")
        self.started = state.started
        self.completed = state.completed

    def extract_state(self) -> NodeState:
        return NodeState(
            id=self.id,
            class_name=self.__class__.__name__,
            name=self.name,
            started=self.started,
            completed=self.completed,
        )

    def with_id(self, gen: NodeIdGenerator) -> Self:
        self.id = gen.create_id(self)
        return self

    def has_error(self) -> bool:
        return self.indent_error or len(self.errors) > 0

    def append_error(self, error: Error):
        self.errors.append(error)

    def __str__(self):
        return f"{self.__class__.__name__}(inst: {self.instruction_name}, args: {self.arguments}, id: {self.id})"
    # def __str__(self):
    #     indent_spaces = "".join(" " for _ in range(self.position.character))
    #     args = "" if self.arguments_part == "" else ": " + self.arguments_part
    #     return f"{indent_spaces}{self.name_part}{args} | id={self.id}"

    def __repr__(self):
        return self.__str__()

    def as_tree(self) -> str:
        indent_spaces = "".join(" " for _ in range(self.position.character))
        args = "" if self.arguments_part == "" else ": " + self.arguments_part
        return f"{indent_spaces}{self.instruction_part}{args} | id={self.id}"

    def reset_runtime_state(self, recursive: bool):
        # TODO implement, possily by just applying an empty state dict
        # known state to reset: activated for condition nodes
        # state = self.extract_state()
        # state.started = False
        # state.completed = False
        # self.apply_state(state)

        self._forced = False

        self.started = False
        self.completed = False

        if recursive:
            if isinstance(self, NodeWithChildren):
                for child in self.children:
                    child.reset_runtime_state(True)


class NodeWithChildren(Node):
    def __init__(self, position=Position.empty, id=""):
        super().__init__(position, id)
        self._children: list[Node] = []

    @property
    def children(self) -> list[Node]:
        return self._children

    def append_child(self, child: Node):
        child.parent = self
        self._children.append(child)

    def has_children(self):
        return len(self._children) > 0

    def get_child_nodes(self, recursive: bool = False) -> list[Node]:
        children: list[Node] = []
        for child in self._children:
            children.append(child)
            if recursive and isinstance(child, NodeWithChildren):
                children.extend(child.get_child_nodes(recursive))
        return children

    # backport for python 3.11
    def get_first_child(self, node_type: Type[TNode]) -> TNode | None:
        #    def get_first_child[T: Node](self, node_type: Type[T]) -> T | None:
        """ Return the first child node of the specified type, recursively, depth first"""
        for child in self._children:
            if isinstance(child, node_type):
                return child
            if isinstance(child, NodeWithChildren):
                match = child.get_first_child(node_type)
                if match:
                    return match
        return None

    # def __str__(self):
    #     args = "" if self.arguments_part == "" else ": " + self.arguments_part
    #     children = [c.name_part for c in self.children]
    #     return f"{self.name_part}{args} | children: {", ".join(children)} "

    def as_tree(self) -> str:
        """ Return the node and its subtree as a string mimicing the source pcode """
        indent_spaces = "".join(" " for _ in range(self.position.character))
        args = "" if self.arguments_part == "" else ": " + self.arguments_part
        return f"{indent_spaces}{self.instruction_part}{args}\n" + \
            "\n".join(child.as_tree() for child in self.children)


class ProgramNode(NodeWithChildren):
    def __init__(self, position=Position.empty, id=""):
        super().__init__(position, id)
        self.active_instruction: Node | None = None

    def get_instructions(self, include_blanks: bool = False) -> list[Node]:
        """ Return list of all program instructions, recursively, depth first. """
        children: list[Node] = self.get_child_nodes(recursive=True)
        if not include_blanks:
            return [n for n in children if not isinstance(n, BlankNode)]
        return children

    def get_all_nodes(self) -> list[Node]:
        """ Return all nodes, depth first, as a flat list"""
        def add_child_nodes(node, nodes: list[Node]):
            nodes.append(node)
            if isinstance(node, NodeWithChildren):
                for child in node.children:
                    add_child_nodes(child, nodes)
        nodes = []
        add_child_nodes(self, nodes)
        return nodes

    def extract_tree_state(self) -> dict[str, NodeState]:
        """ Return map of all nodes keyed by their node id """
        result: dict[str, NodeState] = {}

        def extract_child_state(node: Node, result: dict[str, NodeState]):
            result[node.id] = node.extract_state()

            if isinstance(node, NodeWithChildren):
                for child in node.children:
                    extract_child_state(child, result)

        extract_child_state(self, result)
        return result

    def apply_tree_state(self, state: dict[str, NodeState]):
        def apply_child_state(node: Node):
            node_state = state.get(node.id, None)
            if node_state is not None:
                node.apply_state(node_state)
            if isinstance(node, NodeWithChildren):
                for child in node.children:
                    apply_child_state(child)
        apply_child_state(self)

    @staticmethod
    def empty() -> ProgramNode:
        return ProgramNode()


class MarkNode(Node):
    instruction_names = ["Mark"]

    def __init__(self, position=Position.empty, id=""):
        super().__init__(position, id)
        self._forcible = False


class BlockNode(NodeWithChildren):
    instruction_names = ["Block"]


class EndBlockNode(Node):
    instruction_names = ["End block"]


class EndBlocksNode(Node):
    instruction_names = ["End blocks"]

class BatchNode(Node):
    instruction_names = ["Batch"]


class NodeWithCondition(NodeWithChildren):
    def __init__(self, position=Position.empty, id=""):
        super().__init__(position, id)
        self.condition_part: str
        self.condition: Condition | None
        self.activated: bool = False

    def apply_state(self, state):
        super().apply_state(state)
        if "activated" not in state.keys():
            raise ValueError("Missing state key 'activated'")
        self.activated = bool(state["activated"])

    def extract_state(self) -> NodeState:
        state = super().extract_state()
        state["activated"] = self.activated
        return state

    def reset_runtime_state(self, recursive):
        self.activated = False
        self._cancelled = False
        self._forced = False
        super().reset_runtime_state(recursive)

    @property
    def cancellable(self) -> bool:
        return not self.cancelled and not self.forced and not self.activated

    @property
    def forcible(self) -> bool:
        return not self.cancelled and not self.forced and not self.activated


class WatchNode(NodeWithCondition):
    instruction_names = ["Watch"]


class AlarmNode(NodeWithCondition):
    instruction_names = ["Alarm"]


class Condition:
    def __init__(self):
        self.error = True
        self.lhs = ""
        self.op = ""
        self.rhs = ""
        self.range: Range = Range.empty

        self.tag_name: str | None = None
        self.tag_value: str | None = None
        self.tag_unit: str | None = None
        self.tag_value_numeric: int | float | None = None

        # these ranges are problematic. we somehow want to exclude whitespace
        # for the LSP purpose of underlining lsh/op/rhs but this conflicts
        # with the calculation of later ones based on the first ones.

        self.lhs_range = Range.empty
        self.op_range = Range.empty
        self.rhs_range = Range.empty


class CommentNode(Node):
    """ Represents a line with only a comment. """
    def __init__(self, position=Position.empty, id=""):
        super().__init__(position, id)
        self.line: str = ""

    def with_line(self, line: str):
        self.line = line
        return self


class InjectedNode(NodeWithChildren):
    pass


class MacroNode(NodeWithChildren):
    instruction_names = ["Macro"]

    def __init__(self, position=Position.empty, id=""):
        super().__init__(position, id)
        self.activated: bool = False
        self._cancellable = False
        self._forcible = False


class CallMacroNode(Node):
    instruction_names = ["Call macro"]

    def __init__(self, position=Position.empty, id=""):
        super().__init__(position, id)
        self._cancellable = False
        self._forcible = False


class CommandBaseNode(Node):
    pass


class InterpreterCommandNode(CommandBaseNode):
    """ Represents commands that are directly executable by the interpreter. """
    instruction_names = ["Base", "Increment run counter", "Run counter", "Wait"]


class EngineCommandNode(CommandBaseNode):
    """ Represents internal engine commands that have a command class subclassing InternalEngineCommand. """
    instruction_names = ["Stop", "Pause", "Unpause", "Hold", "Unhold", "Restart",
                         "Info", "Warning", "Error"]


class UodCommandNode(CommandBaseNode):
    """ Represents a uod command, subclassing UodCommand. """


class Comment:
    def __init__(self, comment: str, position: Position):
        self.comment = comment
        self.position = position


class Error:
    def __init__(self, message: str | None = None) -> None:
        self.message: str | None = message


class BlankNode(Node):
    """ Represents a line that contains only whitespace. """


class ErrorInstructionNode(Node):
    """ Represents non-parsable instruction line. """

    def __init__(self, position=Position.empty, id=""):
        super().__init__(position, id)
        self.line: str = ""

    def with_line(self, line: str):
        self.line = line
        return self
