from __future__ import annotations
from typing import Callable, List


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

    def is_empty(self):
        return self.val is None

    def get_value(self):
        return self.val


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
        self.indent: int | None = None
        self.line: int | None = None
        self.errors: List[PError] | None = None

        if self.parent is not None and self.parent.children is not None:
            self.parent.children.append(self)

    @property
    def depth(self):
        if self.parent is None:
            return 0
        return self.parent.depth + 1

    def __str__(self) -> str:
        return type(self).__name__

    def __eq__(self, other):
        # TODO: Here be dragons. See issue https://github.com/Open-Pectus/Open-Pectus/issues/22 regarding
        # identity vs value equality, performance and caching.
        # See also note in next_following() below.
        # Current implementation may cause RecursionError
        if not isinstance(other, PNode):
            return False
        if self.depth != other.depth:
            return False
        return self.__dict__ == other.__dict__

    def get_child_nodes(self, recursive: bool = False) -> List[PNode]:
        children = []
        if self.children is None:
            return children
        for child in self.children:
            children.append(child)
            if recursive:
                children.extend(child.get_child_nodes(recursive))
        return children

    def add_error(self, error: PError | str):
        if self.errors is None:
            self.errors = []
        if isinstance(error , PError):
            self.errors.append(error)
        else:
            self.errors.append(PError(error))

    def has_error(self, recursive: bool = False):
        if not recursive:
            if self.errors is None or len(self.errors) == 0:
                return False
            return True
        else:
            for c in self.get_child_nodes(True):
                if c.has_error():
                    return True
            return False

    def next_following(self) -> PNode | None:
        """ Return the next following node in the tree (in XPath axis terminology) """
        def following(node: PNode, parent: PNode | None):
            if parent is None:
                return None
            assert parent.children is not None, "We navigate upwards so children cannot be None (or empty)"

            inx = -1
            for i, child in enumerate(parent.children):
                # TODO currently using "is" check rather than value equality
                # because __eq__ sometimes fails. See Note in __eq__.
                if child is node:
                    inx = i
                    break
            assert inx != -1, "Child index not found"
            if inx + 1 < len(parent.children):
                next_sibling = parent.children[inx+1]
                return next_sibling
            else:
                return following(node=parent, parent=parent.parent)

        return following(node=self, parent=self.parent)

    def next_descendant(self) -> PNode | None:
        """ Return the next descendant node in the tree (in XPath axis terminology) """

        if self.children is None or len(self.children) == 0:
            return None
        if len(self.children) > 0:
            return self.children[0]

    def iterate(self, fn: Callable[[PNode], None]):
        fn(self)
        if self.children is not None:
            for child in self.children:
                child.iterate(fn)

    def has_ancestor(self, ancestor_candidate: PNode):
        parent = self.parent
        while parent is not None:
            if parent == ancestor_candidate:
                return True
            parent = parent.parent


class PProgram(PNode):
    """ Represents a complete pectus program. """
    def __init__(self) -> None:
        super().__init__(None)
        self.children = []
        self.is_root = True

    def get_instructions(self, include_blanks: bool = False) -> List[PInstruction]:
        """ Return list of all program instructions, recursively, depth first. """
        children: List[PInstruction] = self.get_child_nodes(recursive=True)  # type: ignore
        if not include_blanks:
            return [n for n in children if not isinstance(n, PBlank)]
        return children

    def get_commands(self) -> List[PCommand]:
        return [c for c in self.get_instructions() if isinstance(c, PCommand)]

    def get_condition_nodes(self) -> List[PAlarm | PWatch]:
        return [c for c in self.get_instructions() if isinstance(c, PAlarm) or isinstance(c, PWatch)]


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

    def __str__(self) -> str:
        return super().__str__() + ": " + self.name


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
        self.condition: PCondition | None = None
        self.activated: bool = False

    def __str__(self) -> str:
        cnd = self.condition.condition_str if self.condition is not None else ""
        return super().__str__() + f": {cnd} | line: {self.line}"


class PAlarm(PInstruction):
    """ Represents an Alarm intruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.children = []
        self.condition: PCondition | None = None

    def __str__(self) -> str:
        cnd = self.condition.condition_str if self.condition is not None else ""
        return super().__str__() + f": {cnd} | line: {self.line}"


class PMark(PInstruction):
    """ Represents an Mark intruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.children = []
        self.name: str = ''

    def __str__(self) -> str:
        return super().__str__() + ": " + self.name


class PCommand(PInstruction):
    """ Represents a Command instruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        # self.children = [] possibly?
        self.name: str = ''
        self.args: str = ''

    def __str__(self) -> str:
        return super().__str__() + ": " + self.name


class PBlank(PInstruction):
    """ Represents an all-whitespace pcode line. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)


class PErrorInstruction(PInstruction):
    """ Represents a non-parsable instruction pcode line """
    def __init__(self, parent: PNode, code: str) -> None:
        super().__init__(parent)
        self.children = []
        self.code: str = code

    def __str__(self) -> str:
        return super().__str__() + ": Code: " + self.code


# --- Non-nodes ---

class PError:
    """ Represents an instruction that contains errors. """
    def __init__(self, message: str | None = None) -> None:
        self.message: str | None = message


class PCondition:
    """ Represents a condition expression for alarms and watches. """
    def __init__(self, condition_str: str) -> None:
        self.condition_str = condition_str
        self.op = ""
        self.tag_name = ""
        self.tag_value = ""
        self.tag_unit: str | None = None
        self.error: bool = False

    @property
    def tag_value_numeric(self) -> float:
        return float(self.tag_value)

    def evaluate(self, tags) -> bool:  # should possibly take a "context" with more info than just the tags
        raise NotImplementedError()
