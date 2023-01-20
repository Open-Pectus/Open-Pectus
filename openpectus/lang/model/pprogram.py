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


class PNode():
    """ Represents a node in a pectus runtime model object tree. """
    def __init__(self, parent: PNode | None) -> None:
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


class PProgram(PNode):
    """ Represents a complete pectus program. """
    def __init__(self) -> None:
        super().__init__(None)
        self.children = list()
        self.is_root = True

    def get_instructions(self) -> List[PInstruction]:
        return self.children  # type: ignore TODO test this


class PInstruction(PNode):
    """ Represents a generic instruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.time: TimeExp = TimeExp.Empty()


class PBlock(PInstruction):
    """ Represents a Block intruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.name: str = ''


class PCommand(PInstruction):
    """ Represents a Command instruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.name: str = ''
        self.args: str = ''
