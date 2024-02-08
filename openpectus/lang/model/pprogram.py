from __future__ import annotations
from typing import Callable, List
from uuid import UUID, uuid4


class PNode():
    """ Represents an AST node in an openpectus runtime model object tree. """

    def __init__(self, parent: PNode | None) -> None:
        """ Create new node with specified parent or None for the root node. If parent is given,
            the created node is added as child of the parent.
        """
        self.parent = parent
        """ The parent node or None for the root node. """

        self.children: List[PNode] | None = None
        """ The child nodes of the node, if any. None if the node cannot have child nodes. """

        self._id: UUID = uuid4()
        """ Node id, assigned randomly during initialization. Can be changed for the sole
        purpose of merging two parse trees. """

        self.is_root: bool = False
        """ Set to true for the root node. False for all other nodes in a tree. """

        self.indent: int | None = None
        """ The indentation for the line, expressed in number of spaces. A multiple of 
        pprogrambuilder.INDENTATION_SPACES. """

        self.line: int | None = None
        """ The line number, starting from 1. All instructions have unique line numbers,
        except PProgram which shares line number with its first child instruction.
        """

        self.errors: List[PError] | None = None
        """ Errors encountered during parsing. """

        if self.parent is not None and self.parent.children is not None:
            self.parent.children.append(self)

    @property
    def id(self) -> UUID:
        return self._id

    def update_id(self, new_id: UUID):
        self._id = new_id

    @property
    def runlog_name(self) -> str | None:
        """ Name to show in runlog. Return None to skip in runlog. """
        return None

    @property
    def depth(self):
        if self.parent is None:
            return 0
        return self.parent.depth + 1

    def __str__(self) -> str:
        return type(self).__name__

    def __eq__(self, other) -> bool:
        # TODO: Here be dragons. See issue https://github.com/Open-Pectus/Open-Pectus/issues/22 regarding
        # identity vs value equality, performance and caching.
        # See also note in next_following() below.
        # Current implementation may cause RecursionError
        if not isinstance(other, PNode):
            return False
        return self.id == other.id
        # if self.depth != other.depth:
        #     return False
        # return self.__dict__ == other.__dict__

    def get_child_nodes(self, recursive: bool = False) -> List[PNode]:
        children: List[PNode] = []
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

    def reset_state(self):
        """ Override to clear node runtime state. """
        pass


class PProgram(PNode):
    """ Represents a complete pectus program. """
    def __init__(self) -> None:
        super().__init__(None)
        self.children = []
        self.is_root = True
        self.line = 1

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

    def reset_state(self):
        """ Reset all runtime state from the program """
        def reset(node: PNode):
            if node != self:
                node.reset_state()
        self.iterate(reset)


class PInjectedNode(PNode):
    """ Represents a subtree of injected code """
    def __init__(self, parent: PNode | None) -> None:
        super().__init__(parent)
        self.children = []


class PInstruction(PNode):
    """ Represents a generic instruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.time: float | None = None
        """ The delay threshold specified for the instruction. """

        self.comment: str = ''


class PBlock(PInstruction):
    """ Represents a Block intruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.children = []
        self.name: str = ''

    def __str__(self) -> str:
        return super().__str__() + ": " + self.name

    @property
    def runlog_name(self) -> str | None:
        return "Block: " + self.name


class PEndBlock(PInstruction):
    """ Represents an End Block intruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)


class PEndBlocks(PInstruction):
    """ Represents an End Blocks intruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)


class PWatch(PInstruction):
    """ Represents a Watch instruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.children = []
        self.condition: PCondition | None = None
        self.activated: bool = False

    @property
    def condition_str(self) -> str:
        return self.condition.condition_str if self.condition is not None else ""

    def __str__(self) -> str:
        return super().__str__() + f": {self.condition_str} | line: {self.line}"

    @property
    def runlog_name(self) -> str | None:
        return "Watch: " + self.condition_str

    def reset_state(self):
        self.activated = False


class PAlarm(PInstruction):
    """ Represents an Alarm instruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.children = []
        self.condition: PCondition | None = None

    @property
    def condition_str(self) -> str:
        return self.condition.condition_str if self.condition is not None else ""

    def __str__(self) -> str:
        cnd = self.condition.condition_str if self.condition is not None else ""
        return super().__str__() + f": {cnd} | line: {self.line}"

    @property
    def runlog_name(self) -> str | None:
        return "Alarm: " + self.condition_str


class PMark(PInstruction):
    """ Represents an Mark instruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.children = []
        self.name: str = ''

    def __str__(self) -> str:
        return super().__str__() + ": " + self.name

    @property
    def runlog_name(self) -> str | None:
        return "Mark: " + self.name


class PCommand(PInstruction):
    """ Represents a Command instruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        # self.children = [] possibly?
        self.name: str = ''
        self.args: str = ''

    def __str__(self) -> str:
        return super().__str__() + ": " + self.name

    @property
    def runlog_name(self) -> str | None:
        return self.name


class PBlank(PInstruction):
    """ Represents an all-whitespace pcode line. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)


class PComment(PInstruction):
    """ Represents a comment instruction. """
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
    """ Represents an error in an instruction. """
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
