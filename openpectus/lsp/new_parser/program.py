from __future__ import annotations
from typing import Sequence, Type, TypeVar

from openpectus.lang.exec.argument_specification import ArgSpec

class CommandBase:
    arg_spec: ArgSpec
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


Position.empty = Position(line=-1, character=-1)


class Range:
    empty: Range

    def __init__(self, start: Position, end: Position):
        self.start = start
        self.end = end

    def is_empty(self) -> bool:
        return self == Range.empty


Range.empty = Range(start=Position.empty, end=Position.empty)



class Node:
    instruction_name: str = ""
    """ Defines the instruction name for the node. """

    def __init__(self, position=Position.empty):
        self.parent : NodeWithChildren | None = None
        self.position: Position = position
        self.name_part: str = ""
        self.threshold_part: str = ""
        self.arguments_part: str = ""
        self.comment_part: str = ""

        self.threshold: float | None = None
        self.indent_error: bool = False

        self.errors: list[Error] = []
#    command_cls: type[CommandBase]

    def has_children(self) -> bool:
        return False

    def has_error(self) -> bool:
        return self.indent_error or len(self.errors) > 0

    def append_error(self, error: Error):
        self.errors.append(error)

    def __str__(self):
        indent_spaces = "".join(" " for _ in range(self.position.character))
        args = "" if self.arguments_part == "" else ": " + self.arguments_part
        return f"{indent_spaces}{self.name_part}{args}"

    def __repr__(self):
        return self.__str__()


TNode = TypeVar("TNode", bound=Node)


class NodeWithChildren(Node):
    def __init__(self, position=Position.empty):
        super().__init__(position)
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

    def __str__(self):
        indent_spaces = "".join(" " for _ in range(self.position.character))
        args = "" if self.arguments_part == "" else ": " + self.arguments_part
        return f"{indent_spaces}{self.name_part}{args}\n" + \
            "\n".join(str(child) for child in self.children)


class ProgramNode(NodeWithChildren):

    def get_instructions(self, include_blanks: bool = False) -> list[Node]:
        """ Return list of all program instructions, recursively, depth first. """
        children: list[Node] = self.get_child_nodes(recursive=True)
        if not include_blanks:
            return [n for n in children if not isinstance(n, BlankNode)]
        return children


class MarkNode(Node):
    instruction_name = "Mark"


class BlockNode(NodeWithChildren):
    instruction_name = "Block"


class EndBlockNode(NodeWithChildren):
    instruction_name = "End block"

    def __str__(self):
        return super().__str__()

class EndBlocksNode(NodeWithChildren):
    instruction_name = "End blocks"


class NodeWithCondition(NodeWithChildren):
    def __init__(self, position=Position.empty):
        super().__init__(position)

    # def x__init__(self, condition_part: str):
    #     super().__init__()
    #     self.condition_part: str
    #     self.condition: Condition | None


class Condition:
    def __init__(self, lhs: str, op: str, rhs: str, position: Position):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs
        self.position = position


class Comment:
    def __init__(self, comment: str, position: Position):
        self.comment = comment
        self.position = position


class Error:
    def __init__(self, message: str | None = None) -> None:
        self.message: str | None = message


class BlankNode(Node):
    """ Represents a blank line"""


class ErrorInstructionNode(Node):
    """ Represents non-parsable instruction line"""
        
