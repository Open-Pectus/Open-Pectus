from __future__ import annotations
from typing import Literal, Self, Sequence, Type, TypeVar, TypedDict

#from openpectus.lang.exec.argument_specification import ArgSpec

class CommandBase:
    #  arg_spec: ArgSpec
    """ Defines valid arguments and how to parse them. """

class EngineCommand(CommandBase):
    ...

class InterpreterCommand(CommandBase):
    ...

class UodCommand:
    ...

# should we have lsp_command as well - would only provide data related to lsp. But i guess we already have
# CommandDefinition for that.

# Command concerns
# 1) Registry (provide command identities and instances, dispose command instances), context manager, immutable(?)
# 2) Grammar replacement, define all commands

class Position:
    def __init__(self, line: int, character: int):
        self.line: int = line   # todo define 0-1 based. should probably change from before to just match lsp
        self.character: int = character  # start index = indentation

    @staticmethod
    def empty() -> Position:
        return Position(line=-1, character=-1)

    def __eq__(self, value):
        if value is None or not isinstance(value, Position):
            return False
        return self.line == value.line and self.character == value.character

    def with_character(self, character: int) -> Position:
        return Position(line=self.line, character=character)

    def __str__(self):
        return f"Position(line: {self.line}, char: {self.character})"





class Range:

    def __init__(self, start: Position, end: Position):
        self.start = start
        self.end = end

    @staticmethod
    def empty() -> Range:
        return Range(start=Position.empty(), end=Position.empty())

    def with_end(self, position: Position) -> Range:
        return Range(
            start=self.start,
            end=position)

    def __str__(self):
        return f"{self.start} - {self.end}"



class NodeIdGenerator:
    def create_id(self, node: Node) -> str:
        ...


# Impl note: using dict because it is json serializable. TypedDict also works
class NodeState(TypedDict):
    id: str
    class_name: str
    name: str
    started: bool
    completed: bool
    # revision?
    # threshold?


TNode = TypeVar("TNode", bound="Node")


class Node:
    instruction_names: list[str] = []
    """ Specifies which node to instantiate for a given instruction name(s) """

    def __init__(self, position=Position.empty(), id=""):
        self.parent: NodeWithChildren | None = None
        self.id: str = id
        self.position: Position = position
        self.name_part: str = ""
        self.name: str = ""
        self.threshold_part: str = ""
        self.arguments_part: str = ""
        self.arguments: str = ""
        self.arguments_range: Range = Range.empty()
        self.comment_part: str = ""
        self.revision: int = 0

        self.threshold: float | None = None
        self.indent_error: bool = False

        self.errors: list[Error] = []

        # interpretation state
        self.started: bool = False
        self.completed: bool = False
#    command_cls: type[CommandBase]

    @property
    def key(self) -> str:
        return f"{self.id}.{self.name}"

    @property
    def key_path(self) -> str:
        """ Key path for node. Looks similar to SePath and sometimes is the same.

        But key_path consists only of the node keys from root to the node in the ast whereas
        SePath includes invocation information such as interrupts and macro invocations. In particular,
        a node has one static key_path (when not considering live-editing or the method). But the node
        may occur in multiple SePaths if invoked multiple times.
        """
        keys = [p.key for p in self.parents]
        keys.reverse()
        keys.append(self.key)
        return " > ".join(keys)

    def has_children(self) -> bool:
        return False

    def get_child_by_id(self, id: str) -> Node | None:
        if self.id == id:
            return self
        if self.has_children():
            assert isinstance(self, NodeWithChildren)
            for child in self.children:
                match = child.get_child_by_id(id)
                if match is not None:
                    return match

    def can_load_state(self, state: NodeState) -> bool:
        """ Determine whether state is valid for this kind of node """
        return state["class_name"] == self.__class__.__name__

    def apply_state(self, state: NodeState):
        if not self.can_load_state(state):
            raise ValueError(f"Cannot load state from {state["class_name"]} into {self.__class__}")
        self.started = state["started"]
        self.completed = state["completed"]

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

    def has_error(self, recursive=False) -> bool:

        def has_error_recursive(node: Node) -> bool:
            if node.indent_error or len(node.errors) > 0:
                return True
            if isinstance(node, NodeWithChildren):
                for child in node.children:
                    if has_error_recursive(child):
                        return True
            return False

        if not recursive:
            return self.indent_error or len(self.errors) > 0
        else:
            return has_error_recursive(self)
    
    def collect_tree_errors(self) -> dict[str, list[str]]:
        raise NotImplementedError()
        errors: dict[str, list[str]] = {}
        
        def collect_recursive(node: Node):
            if node.has_error(recursive=True):
                ...

        self.errors[0].message


    def append_error(self, error: Error):
        self.errors.append(error)

    def __str__(self):
        indent_spaces = "".join(" " for _ in range(self.position.character))
        args = "" if self.arguments_part == "" else ": " + self.arguments_part
        return f"{indent_spaces}{self.name_part}{args} | id={self.id}"

    def __repr__(self):
        return self.__str__()

    def as_tree(self) -> str:
        return self.__str__()

    def reset_runtime_state(self, recursive: bool):
        self.started = False
        self.completed = False

    # TODO should rename to ancestors
    @property
    def parents(self) -> list[NodeWithChildren]:
        """ Return ancestor nodes, ordered from node parent to root """
        node = self
        parents: list[NodeWithChildren] = []
        while node.parent is not None:
            parents.append(node.parent)
            node = node.parent
        return parents

    @property
    def root(self) -> ProgramNode:
        if isinstance(self, ProgramNode):
            return self
        root = self.parents[-1]
        assert isinstance(root, ProgramNode)
        return root

class NodeWithChildren(Node):
    def __init__(self, position=Position.empty(), id=""):
        super().__init__(position, id)
        self._children: list[Node] = []

        self.interrupt_registered: bool = False
        """ Whether an interrupt was registered to execute the node.

        During live-edit and cold state merge, it has the slightly different meaning
        that the interrupt must be registered during merge.
        """
        self.children_complete: bool = False
        """ Specifies that execution of child nodes should stop or is completed. """
        self.child_index: int = 0
        # TODO document child_index

    @property
    #def children(self) -> list[Node]:
    def children(self) -> Sequence[Node]:
        return self._children

    def append_child(self, child: Node):
        child.parent = self
        self._children.append(child)

    def replace_child(self, child: Node, new_child: Node):
        if child.parent is None:
            raise ValueError(f"Cannot replace node {child} without parent")
        if child.parent is not self:
            raise ValueError(f"Cannot replace node {child} whose parent {child.parent} is not self")
        if child not in self.children:
            raise ValueError(f"Cannot replace node {child} not in self.children")
        child.parent = None
        new_child.parent = self
        index = self.children.index(child)
        self._children[index] = new_child

    def remove_child(self, child: Node):
        if child.parent is None:
            raise ValueError(f"Cannot replace node {child} without parent")
        if child.parent is not self:
            raise ValueError(f"Cannot replace node {child} whose parent {child.parent} is not self")
        if child not in self.children:
            raise ValueError(f"Cannot replace node {child} not in self.children")
        child.parent = None
        self._children.remove(child)

    def has_children(self):
        return len(self._children) > 0

    def get_child_nodes(self, recursive: bool = False) -> list[Node]:
        if not self.has_children():
            return []
        assert isinstance(self, NodeWithChildren)
        children: list[Node] = []
        for child in self.children:
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

    def get_first_child_or_throw(self, node_type: Type[TNode]) -> TNode:
        value = self.get_first_child(node_type)
        if value is None:
            raise ValueError(f"No node of type {node_type} was found")
        return value

    def __str__(self):
        indent_spaces = "".join(" " for _ in range(self.position.character))
        args = "" if self.arguments_part == "" else ": " + self.arguments_part
        # children = [c.name_part for c in self.children]
        # return f"{indent_spaces}{self.name_part}{args} | children: {", ".join(children)} "
        return f"{indent_spaces}{self.name_part}{args}"

    def as_tree(self) -> str:
        """ Return the node and its subtree as a string mimicing the source pcode.
        Warning: indentation follows the parsed indentation which may differ from
        the position in the tree in case of parse errors """        
        indent_spaces = "".join(" " for _ in range(self.position.character))
        args = "" if self.arguments_part == "" else ": " + self.arguments_part
        return f"{indent_spaces}{self.name_part}{args}\n" + \
            "\n".join(child.as_tree() for child in self.children)

    def extract_state(self) -> NodeState:
        state = super().extract_state()
        state["interrupt_registered"] = self.interrupt_registered  # type: ignore
        state["children_complete"] = self.children_complete  # type: ignore
        state["child_index"] = self.child_index  # type: ignore
        return state

    def apply_state(self, state):
        # Note about interrupt_registered:
        # In principle, interrupt_registered should not be applied because it would not be
        # correct until the new node is actually registered. But in order to know that and
        # actually register, that information must also be present. So, we reuse
        # interrupt_registered for that, and merge processing must know that this means to
        # actually perform interrupt registration.
        self.interrupt_registered = bool(state["interrupt_registered"])  # type: ignore
        self.children_complete = bool(state["children_complete"])  # type: ignore
        self.child_index = int(state["child_index"])  # type: ignore
        super().apply_state(state)

    def reset_runtime_state(self, recursive):
        # TODO should we not clear additional properties:
        # cancelled, failed?
        super().reset_runtime_state(recursive)
        self.interrupt_registered = False
        self.children_complete = False
        self.child_index = 0
        if recursive:
            for child in self.children:
                child.reset_runtime_state(recursive)

class ProgramNode(NodeWithChildren):
    def __init__(self, position=Position.empty(), id=""):
        super().__init__(position, id)
        self.name = "ProgramNode"
        self.macros: dict[str, MacroNode] = {}
        """ Set by register macro during Macro calls """

    @property
    def key(self) -> str:
        """ Overridden, key of ProgramNode is just 'root' rather than the verbose 'root.ProgramNode'"""
        return "root"

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

    def get_locked_blocks(self) -> list[BlockNode]:
        return [n for n in self.get_all_nodes() if isinstance(n, BlockNode) and n.lock_acquired]


    def extract_tree_state(self) -> dict[str, NodeState]:
        """ Return map of all nodes' state keyed by their node id """
        result: dict[str, NodeState] = {}

        def handle_child_state(node: Node, result: dict[str, NodeState]):
            result[node.id] = node.extract_state()

            if isinstance(node, NodeWithChildren):
                for child in node.children:
                    handle_child_state(child, result)

        handle_child_state(self, result)
        return result

    def apply_tree_state(self, state: dict[str, NodeState]):
        """ Apply all state in state into the current program.

        Note: In case of a live-edit merge, apply_child_state is also called but only after HotSwapVisitor
        has modified the state.
        """
        def apply_child_state(node: Node):
            try:
                node_state = state.get(node.id, None)
                if node_state is not None:
                    node.apply_state(node_state)
            except KeyError as ke:
                raise ValueError(f"Failed to apply state {state} to node {node}. Error: {str(ke)}")
            if isinstance(node, NodeWithChildren):
                for child in node.children:
                    apply_child_state(child)
        apply_child_state(self)

    def apply_revision(self, revision: int):
        """ Sets the revision on all tree nodes """
        self.revision = revision
        for child in self.get_all_nodes():
            child.revision = revision

    def reset_runtime_state(self, recursive):
        self.macros.clear()
        return super().reset_runtime_state(recursive)

    def assert_revision(self, expected_revision: int):
        """ Checks that revision is as expected on all tree nodes. Raises AssertException if this is not the case. """
        if self.revision != expected_revision:
            raise AssertionError(f"ProgramNode has revision {self.revision}, expected {expected_revision}")
        for child in self.get_all_nodes():
            if child.revision != expected_revision:
                raise AssertionError(f"Node {child} has revision {child.revision}, expected {expected_revision}")

    def __str__(self):
        # children = [c.name_part for c in self.children]
        # return f"ProgramNode | children: {", ".join(children)} "
        return "ProgramNode"

class AbcNode(Node):
    """ Simple stateful node """
    instruction_names = ["Abc"]

    def __init__(self, position=Position.empty(), id=""):
        super().__init__(position, id)
        self.abc_state: Literal["", "A", "B", "C"] = ""

    def extract_state(self):
        state = super().extract_state()
        state["abc_state"] = self.abc_state  # type: ignore
        return state

    def apply_state(self, state):
        self.abc_state = state["abc_state"]  # type: ignore
        return super().apply_state(state)

class MarkNode(Node):
    instruction_names = ["Mark"]

class FooNode(Node):
    instruction_names = ["Foo"]

class BlockNode(NodeWithChildren):
    instruction_names = ["Block"]

    def __init__(self, position=Position.empty(), id=""):
        super().__init__(position, id)
        self.block_ended: bool = False
        self.lock_acquired: bool = False

    def extract_state(self):
        state = super().extract_state()
        state["block_ended"] = self.block_ended  # type: ignore
        state["lock_acquired"] = self.lock_acquired  # type: ignore
        return state

    def apply_state(self, state):
        self.block_ended = state["block_ended"]
        self.lock_acquired = state["lock_acquired"]
        return super().apply_state(state)

class EndBlockNode(Node):
    instruction_names = ["End block"]


class EndBlocksNode(Node):
    instruction_names = ["End blocks"]


class NodeWithCondition(NodeWithChildren):
    def __init__(self, position=Position.empty(), id=""):
        super().__init__(position, id)
        self.condition_part: str
        self.condition: Condition | None
        self.condition_value: bool | None = None

        self.activated: bool = False

    def extract_state(self) -> NodeState:
        state = super().extract_state()
        state["activated"] = self.activated  # type: ignore
        return state

    def apply_state(self, state):
        self.activated = state["activated"]
        return super().apply_state(state)

    def reset_runtime_state(self, recursive):
        super().reset_runtime_state(recursive)
        self.activated = False
        self.condition_value = None

class WatchNode(NodeWithCondition):
    instruction_names = ["Watch"]


class AlarmNode(NodeWithCondition):
    instruction_names = ["Alarm"]

    def __init__(self, position=Position.empty(), id=""):
        super().__init__(position, id)
        self.run_count: int = 0
        """ The number of times the alarm has completed """

    def extract_state(self) -> NodeState:
        state = super().extract_state()
        state["run_count"] = self.run_count  # type: ignore
        return state

    def apply_state(self, state):
        self.run_count = int(state["run_count"])
        return super().apply_state(state)

class Condition:
    def __init__(self):
        self.error = True
        self.lhs = ""
        self.op = ""
        self.rhs = ""
        self.range: Range = Range.empty()

        self.tag_name: str | None = None
        self.tag_value: str | None = None
        self.tag_unit: str | None = None
        self.tag_value_numeric: int | float | None = None

        # these ranges are problematic. we somehow want to exclude whitespace
        # for the LSP purpose of underlining lsh/op/rhs but this conflicts
        # with the calculation of later ones based on the first ones.

        self.lhs_range = Range.empty()
        self.op_range = Range.empty()
        self.rhs_range = Range.empty()


class CommentNode(Node):
    """ Represents a line with only a comment. """
    def __init__(self, position=Position.empty(), id=""):
        super().__init__(position, id)
        self.line: str = ""

    def with_line(self, line: str):
        self.line = line
        return self


class MacroNode(NodeWithChildren):
    instruction_names = ["Macro"]

    def __init__(self, position=Position.empty(), id=""):
        super().__init__(position, id)
        self.is_registered: bool = False
        """ Whether the macro has been registered in the revision. Lifetime is revision.

        Note: The is_registered property is subject to the same discussion as
        NodeWithChildren.interrupt_registered regarding live-edit/cold start
        """

        self.run_started_count: int = 0
        """ The number of times the macro has started. Life time is the whole run """
        self.run_completed_count: int = 0


    @property
    def macro_name(self) -> str:
        """ Returns the name of the macro """
        return self.arguments

    def reset_runtime_state(self, recursive: bool):
        # Deliberately skipping is_registered
        # Deliberately skipping run_started_count
        return super().reset_runtime_state(recursive)

    def extract_state(self):
        state = super().extract_state()
        state["is_registered"] = self.is_registered  # type:ignore
        state["run_started_count"] = self.run_started_count  # type: ignore
        state["run_completed_count"] = self.run_completed_count  # type: ignore
        return state

    def apply_state(self, state):
        # Note: The is_registered property is subject to the same discussion as
        # NodeWithChildren.interrupt_registered
        self.is_registered = bool(state["is_registered"])
        self.run_started_count = int(state["run_started_count"])
        self.run_completed_count = int(state["run_completed_count"])
        return super().apply_state(state)

class CallMacroNode(Node):
    instruction_names = ["Call macro"]

    @property
    def macro_name(self) -> str:
        """ Name of the macro to call """
        return self.arguments


class CommandBaseNode(Node):
    pass


class EngineCommandNode(CommandBaseNode):
    """ Represents internal engine commands that have a command class subclassing InternalEngineCommand. """
    instruction_names = ["Stop", "Pause", "Unpause", "Hold", "Unhold", "Restart", "Wait"]


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
    def __init__(self, position=Position.empty(), id=""):
        super().__init__(position, id)
        self.test_has_only_trailing_whitespace = False
        """ In prod this value is set by an analyzer. Here we set it manually from tests """


class ErrorInstructionNode(Node):
    """ Represents non-parsable instruction line. """

    def __init__(self, position=Position.empty(), id=""):
        super().__init__(position, id)
        self.line: str = ""

    def with_line(self, line: str):
        self.line = line
        return self
