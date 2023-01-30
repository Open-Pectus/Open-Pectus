from __future__ import annotations
from typing import List


class TimeExp():
    def __init__(self, val: str | None) -> None:
        self.val: str | None = val

    @staticmethod
    def Empty() -> TimeExp:
        """ Return an empty time expression. """
        return TimeExp(None)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __str__(self) -> str:
        return f"TimeExp {{ {self.val} }}"


class PNode():
    """ Represents a node in a pectus runtime model object tree. """
    def __init__(self, parent: PNode | None) -> None:
        """ Create new node with specified parent or None for the root node. If parent is given,
            the created node is added as child of the parent.
        """
        self.parent = parent
        """ The parent node or None for the root node. """
        self.children: List[PNode] | None = None
        """ The child nodes of the node, if any. None if the node cannot have child nodes. """

        self.is_root: bool = False
        self.indent: int = 0
        self.line: int = 1

        if self.parent is not None and self.parent.children is not None:
            self.parent.children.append(self)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def get_child_nodes(self, recursive: bool = False) -> List[PNode]:
        children = []
        if self.children is None:
            return children
        for child in self.children:
            children.append(child)
            if recursive:
                children.extend(child.get_child_nodes(recursive))
        return children


class PProgram(PNode):
    """ Represents a complete pectus program. """
    def __init__(self) -> None:
        super().__init__(None)
        self.children = []
        self.is_root = True

    def get_instructions(self) -> List[PInstruction]:
        return self.get_child_nodes(recursive=True)  # type: ignore


class PInstruction(PNode):
    """ Represents a generic instruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.time: TimeExp = TimeExp.Empty()


class PBlock(PInstruction):
    """ Represents a Block intruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.children = []
        self.name: str = ''


class PEndBlock(PInstruction):
    """ Represents an End Block intruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)


class PEndBlocks(PInstruction):
    """ Represents an End Blocks intruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)


class PWatch(PInstruction):
    """ Represents a Watch intruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.children = []
        self.condition: str = ''


class PAlarm(PInstruction):
    """ Represents an Alarm intruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.children = []
        self.condition: str = ''


class PCommand(PInstruction):
    """ Represents a Command instruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        # self.children = [] possibly?
        self.name: str = ''
        self.args: str = ''


class PError(PInstruction):
    """ Represents an instruction that contains errors. """
    def __init__(self, parent: PNode, replace_node: PNode | None) -> None:
        """ If replace_node is specified, the error node will replace the provided node"""

        if replace_node is not None and parent.children is not None:
            parent.children.remove(replace_node)

        super().__init__(parent)

        self.children = []
        # possibly replace the old node's chilren as well. if there could ever be any??
        # if replace_node is not None and replace_node.children is not None:
        #     self.children = replace_node.children

        self.errors: List[str] = []
