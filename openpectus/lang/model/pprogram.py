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

        self._inst_error: PInstError | None = None
        """ Partial parse error. Is set by parser. Must be processed into one or more elements in self.errors
        for general consumption
         """

        self._cancellable: bool = False
        """ Whether node is statically cancellable, i.e. supports the cancel operation at all. """

        self._cancelled: bool = False
        self._forcible: bool = False
        """ Whether node is statically forcible, i.e. supports the force operation at all. """

        self._forced: bool = False

        if self.parent is not None and self.parent.children is not None:
            self.parent.children.append(self)

    @property
    def id(self) -> UUID:
        return self._id

    def update_id(self, new_id: UUID):
        self._id = new_id

    @property
    def display_name(self) -> str:
        """ The name of the instruction for general display"""
        if hasattr(self, "name"):
            return getattr(self, "name")
        return str(self)

    @property
    def runlog_name(self) -> str | None:
        """ Name to show in runlog. Return None to skip in runlog. """
        return None

    @property
    def instruction_name(self) -> str | None:
        """ Name to query for in tests. Return None to not support querying.

        Should not include arguments because their formatting may not be predictable. """
        return None

    @property
    def depth(self):
        if self.parent is None:
            return 0
        return self.parent.depth + 1

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

    def collect_errors(self):
        """ Populate the errors collection from node state that indicates parse errors. """
        if self._inst_error is not None:
            self.add_error("Syntax error")
        for child in self.get_child_nodes(recursive=True):
            child.collect_errors()

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
        return False

    def reset_runtime_state(self, recursive: bool = False):
        """ Override to clear node runtime state. """
        if recursive:
            def reset(node: PNode):
                if node != self:
                    node.reset_runtime_state(False)
            self.iterate(reset)


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
        """ The delay threshold specified for the instruction measured in the Base unit. """

        self.comment: str = ''
        self._forcible = True

    @property
    def forcible(self) -> bool:
        return super().forcible and self.time is not None

    def reset_runtime_state(self, recursive: bool = False):
        self._forced = False
        super().reset_runtime_state(recursive=recursive)


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

    @property
    def instruction_name(self) -> str | None:
        return "Block"


class PEndBlock(PInstruction):
    """ Represents an End block intruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

    @property
    def runlog_name(self) -> str | None:
        return "End block"

    @property
    def instruction_name(self) -> str | None:
        return "End block"


class PEndBlocks(PInstruction):
    """ Represents an End blocks intruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

    @property
    def runlog_name(self) -> str | None:
        return "End blocks"

    @property
    def instruction_name(self) -> str | None:
        return "End blocks"


class PWatch(PInstruction):
    """ Represents a Watch instruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.children = []
        self.condition: PCondition | None = None
        self.activated: bool = False

    # override cancellable and forcible to be disabled once activated
    @property
    def cancellable(self) -> bool:
        return not self.cancelled and not self.forced and not self.activated

    @property
    def forcible(self) -> bool:
        return not self.cancelled and not self.forced and not self.activated

    @property
    def condition_str(self) -> str:
        return self.condition.condition_str if self.condition is not None else ""

    def __str__(self) -> str:
        return super().__str__() + f": {self.condition_str} | line: {self.line}"

    @property
    def runlog_name(self) -> str | None:
        return "Watch: " + self.condition_str

    @property
    def instruction_name(self) -> str | None:
        return "Watch"

    def collect_errors(self):
        super().collect_errors()
        if self.condition is None:
            self.add_error(PError("Missing condition"))

    def reset_runtime_state(self, recursive: bool = False):
        self.activated = False
        self._cancelled = False
        self._forced = False
        super().reset_runtime_state(recursive=recursive)


class PAlarm(PInstruction):
    """ Represents an Alarm instruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.children = []
        self.condition: PCondition | None = None
        self.activated: bool = False

    # override cancellable and forcible to be disabled once activated
    @property
    def cancellable(self) -> bool:
        return not self.cancelled and not self.activated

    @property
    def forcible(self) -> bool:
        return not self.forced and not self.activated

    @property
    def condition_str(self) -> str:
        return self.condition.condition_str if self.condition is not None else ""

    def __str__(self) -> str:
        cnd = self.condition.condition_str if self.condition is not None else ""
        return super().__str__() + f": {cnd} | line: {self.line}"

    @property
    def runlog_name(self) -> str | None:
        return "Alarm: " + self.condition_str

    @property
    def instruction_name(self) -> str | None:
        return "Alarm"

    def collect_errors(self):
        super().collect_errors()
        if self.condition is None:
            self.add_error(PError("Missing condition"))

    def reset_runtime_state(self, recursive: bool = False):
        self.activated = False
        self._cancelled = False
        self._forced = False
        super().reset_runtime_state(recursive=recursive)


class PMacro(PInstruction):
    """ Represents a Macro instruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.children = []
        self.name: str = ''
        self.activated: bool = False
        self._cancellable = False
        self._forcible = False

    def __str__(self) -> str:
        return super().__str__() + ": " + self.name

    @property
    def runlog_name(self) -> str | None:
        return "Macro: " + self.name

    @property
    def instruction_name(self) -> str | None:
        return "Macro"


class PCallMacro(PInstruction):
    """ Represents a Call macro instruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.children = []
        self.name: str = ''
        self._cancellable = False
        self._forcible = False

    def __str__(self) -> str:
        return super().__str__() + ": " + self.name

    @property
    def runlog_name(self) -> str | None:
        return "Call macro: " + self.name

    @property
    def instruction_name(self) -> str | None:
        return "Call macro"


class PMark(PInstruction):
    """ Represents an Mark instruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.children = []
        self.name: str = ''
        self._forcible = False

    def __str__(self) -> str:
        return super().__str__() + ": " + self.name

    @property
    def runlog_name(self) -> str | None:
        return "Mark: " + self.name

    @property
    def instruction_name(self) -> str | None:
        return "Mark"


class PBatch(PInstruction):
    """ Represents a Batch name instruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.children = []
        self.name: str = ''
        self._forcible = False

    def __str__(self) -> str:
        return super().__str__() + ": " + self.name

    @property
    def runlog_name(self) -> str | None:
        return "Batch: " + self.name

    @property
    def instruction_name(self) -> str | None:
        return "Batch"


class PCommand(PInstruction):
    """ Represents a Command instruction (Start, Stop, Restart, ...) as well as uod commands.

    Note: The cancellable property is not set for uod commands because the node does not know
    about the command. Runlog must set this property.
    """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.name: str = ''
        self.args: str = ''

    def __str__(self) -> str:
        return super().__str__() + ": " + self.name

    def cancel(self):
        # skip the cancellable check here as noted above
        self._cancelled = True

    @property
    def runlog_name(self) -> str | None:
        args = "" if self.args == "" else f": {self.args}"
        return self.name + args

    @property
    def instruction_name(self) -> str | None:
        return self.name

class PCommandWithDuration(PInstruction):
    """ Represents a Command instruction with a possible duration (Pause, Hold and Wait). """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)

        self.name: str = ''
        """ Command name """
        self.duration: PDuration | None = None
        """ Unresolved duration expression """

    @property
    def cancellable(self) -> bool:
        return False

    @property
    def forcible(self) -> bool:
        if self.name == "Wait" and not self._forced:
            return True
        return False

    def __str__(self) -> str:
        duration = "" if self.duration is None else ", duration: " + str(self.duration)
        return super().__str__() + ": " + self.name + duration

    @property
    def runlog_name(self) -> str | None:
        runlog_argument = "" if self.duration is None else ": " + self.duration.runlog_argument
        return self.name + runlog_argument

    @property
    def instruction_name(self) -> str | None:
        return self.name

    def collect_errors(self):
        super().collect_errors()
        if self.name == "Pause":
            if self.duration is not None and self.duration.error:
                self.add_error(PError("Invalid Pause arguments. Specify either no duration arguments or both time and unit"))
        elif self.name == "Hold":
            if self.duration is not None and self.duration.error:
                self.add_error(PError("Invalid Hold arguments. Specify either no duration arguments or both time and unit"))
        elif self.name == "Wait":
            if self.duration is None or self.duration.error:
                self.add_error(PError("Wait requires a time and unit"))


class PBlank(PInstruction):
    """ Represents an all-whitespace pcode line. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)


class PComment(PInstruction):
    """ Represents a comment instruction. """
    def __init__(self, parent: PNode) -> None:
        super().__init__(parent)


class PErrorInstruction(PInstruction):
    """ Represents a non-parsable instruction pcode line. """
    def __init__(self, parent: PNode, code: str) -> None:
        super().__init__(parent)
        self.children = []
        if self.errors is None or len(self.errors) == 0:
            self.errors = [PError("Parse error")]
        self.code: str = code

    def has_error(self, recursive: bool = False):
        return True

    def __str__(self) -> str:
        return super().__str__() + ": Code: " + self.code


class PInstError:
    """ Represents the error part of a parsed instruction. This differs from PErrorInstruction by being
    partly parsed. This allows better language assistance than PErrorInstruction. """
    def __init__(self, message: str | None = None) -> None:
        self.message: str | None = message


# --- Non-nodes ---

class PError:
    """ Represents an error in an instruction. """
    def __init__(self, message: str | None = None) -> None:
        self.message: str | None = message


class PCondition:
    """ Represents a condition expression for Alarm and Watch instructions.

    The condition is resolved by ConditionEnrichAnalyzer.
    """
    def __init__(self, condition_str: str, start_column: int, end_column: int) -> None:
        self.condition_str = condition_str
        """ Original condition string expression """
        self.start_column = start_column
        self.end_column = end_column

        self.op = ""
        """ Unresolved condition operator """
        self.lhs = ""
        """ Unresolved condition left-hand-side expression """
        self.rhs = ""
        """ Unresolved condition right-hand-side expression """

        # Note: error is True by default and only modified by the analyzer
        self.error : bool = True
        self.tag_name: str | None = None
        self.tag_value: str | None = None
        self.tag_unit: str | None = None
        self.tag_value_numeric: int | float | None = None

        self.lhs_start: int = 0
        self.lhs_end: int = 0
        self.op_start: int = 0
        self.op_end: int = 0
        self.rhs_start: int = 0
        self.rhs_end: int = 0


class PDuration:
    """ Represents a duration for PCommandWithDuration (Pause, Hold and Wait) instructions.

    The duration string is resolved by DurationEnrichAnalyzer.
    """

    def __init__(self, duration_str: str) -> None:
        self.duration_str: str = duration_str

        # Note: error is True by default and only modified by the analyzer
        self.error : bool = True
        self.time: float | None = None
        self.unit: str | None = None

    def __str__(self) -> str:
        return f"Duration {self.time} {self.unit}"

    @property
    def runlog_argument(self):
        if self.error:
            return "(error)"
        else:
            if self.time is None:
                return ""
            elif self.unit is None:
                return f"{self.time}"
            else:
                return f"{self.time}{self.unit}"
