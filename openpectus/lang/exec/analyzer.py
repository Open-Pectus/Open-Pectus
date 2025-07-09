from __future__ import annotations
from enum import Enum
import logging

from Levenshtein import ratio

from openpectus.lang.exec.visitor import NodeGenerator, NodeVisitor
import openpectus.lang.model.ast as p
from openpectus.lang.exec.tags import TagValueCollection
from openpectus.lang.exec.units import are_comparable, get_compatible_unit_names
from openpectus.lang.exec.commands import CommandCollection
from openpectus.lang.exec.argument_specification import ArgSpec


logging.basicConfig(format=' %(name)s :: %(levelname)-8s :: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class AnalyzerItemType(Enum):
    HINT = 'HINT',
    INFO = 'INFO',
    WARNING = 'WARNING',
    ERROR = 'ERROR'


class AnalyzerItem:
    def __init__(self,
                 id: str,
                 message: str,
                 node: p.Node | p.NodeWithChildren | None,
                 type: AnalyzerItemType,
                 description: str = "",
                 start: int | None = None,
                 length: int | None = None,
                 end: int | None = None,
                 data: dict[str, str] | None = None) -> None:
        self.id: str = id
        self.message: str = message
        self.description: str = description
        self.type: AnalyzerItemType = type
        self.node: p.Node | None = node
        self.range: p.Range = p.Range.empty()
        self.data = dict() if data is None else data

        # use node for ranges by default
        if node is not None:
            self.range.start = node.position
            if node.threshold:
                self.range.start.character += len(node.threshold_part) + 1
            # Set the range to end at the end of line denoted by (character=0, line=i+1)
            self.range.end.character = 0
            self.range.end.line = self.range.start.line + 1
            # If the node has children, mark until the end of the last child
            if isinstance(node, p.NodeWithChildren):
                last_line_not_whitespace = self.range.start.line + 1
                for child in reversed(node.children):
                    if not isinstance(child, p.WhitespaceNode):
                        last_line_not_whitespace = child.position.line
                        break
                if len(node.children):
                    self.range.end.line = last_line_not_whitespace + 1

        # if start is given, modify default range start (keep line)
        if start is not None:
            self.range.start.character = start

        if length is not None and end is not None:
            raise ValueError("Specify either length or end, not both")
        # if length or end is given, modify range end (keep line)
        if length is not None:
            self.range.end = p.Position(self.range.start.line, self.range.start.character + length)
        if end is not None:
            self.range.end = p.Position(self.range.start.line, end)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id="{self.id}", message="{self.message}", type={self.type}, node={self.node})'


class AnalyzerVisitorBase(NodeVisitor):
    """ Override by specific feature analyzers. """

    def __init__(self) -> None:
        super().__init__()
        self.items: list[AnalyzerItem] = []

    def __str__(self) -> str:
        items = [str(item) for item in self.items]
        return f'{self.__class__.__name__}(items={items})'

    def add_item(self, item: AnalyzerItem):
        self.items.append(item)

    def analyze(self, n: p.ProgramNode):
        """ Run analysis synchronously. """
        for _ in self.visit(n):
            pass


class UnreachableCodeCheckAnalyzer(AnalyzerVisitorBase):
    """
    Checks:
    * Presence of code in a Block following End block command
    * Presence of code after "Stop" and "Restart" commands
    """

    def __init__(self):
        super().__init__()
        self.method_end: p.EngineCommandNode | None = None
        self.first_command_after_end: p.Node | None = None
        self.last_command_after_end: p.Node | None = None

    def create_item(self, node: p.Node):
        return AnalyzerItem(
            "UnreachableCode",
            "Unreachable code",
            node,
            AnalyzerItemType.WARNING,
            "There is no path to this code.",
        )

    def visit_BlockNode(self, node: p.BlockNode):
        has_end = False
        if node.children is not None:
            for child in node.children:
                if isinstance(child, (p.EndBlockNode, p.EndBlocksNode)):
                    has_end = True
                    continue
                if has_end and not isinstance(child, p.BlankNode):
                    self.add_item(self.create_item(child))
        yield from super().visit_BlockNode(node)

    def visit_EngineCommandNode(self, node: p.EngineCommandNode):
        super().visit_EngineCommandNode(node)
        if not self.method_end and node.instruction_name in ["Stop", "Restart"]:
            self.method_end = node
        yield

    def visit_Node(self, node) -> NodeGenerator:
        yield from ()
        super().visit_Node(node)
        if self.method_end and not self.first_command_after_end:
            self.first_command_after_end = node
        if self.method_end:
            self.last_command_after_end = node

    def analyze(self, n):
        super().analyze(n)
        if self.method_end and self.first_command_after_end and self.last_command_after_end:
            item = AnalyzerItem(
                "UnreachableCode",
                "Unreachable code",
                self.first_command_after_end,
                AnalyzerItemType.WARNING,
                f"There is no path to this code because the method will end at line {self.method_end.position.line+1}.",
            )
            item.range.end.character = 0
            item.range.end.line = self.last_command_after_end.position.line+1
            self.add_item(item)


class InfiniteBlockCheckAnalyzer(AnalyzerVisitorBase):
    """
    Checks:
    * Block *can* potentially finish due to End block or End blocks
    """

    def create_item(self, node: p.Node):
        return AnalyzerItem(
            "InfiniteBlock",
            "Infinite block",
            node,
            AnalyzerItemType.WARNING,
            "This block will run indefinitely, as there are no End block or End blocks to terminate it."
        )

    def __init__(self) -> None:
        super().__init__()
        self.has_global_end = False
        self.requires_global_end: list[p.Node] = []

    def __str__(self) -> str:
        items = [str(item) for item in self.items]
        return f'{self.__class__.__name__}(items={items}, has_global_end={self.has_global_end})'

    def check_global_end_block(self, node: p.EndBlockNode | p.EndBlocksNode | p.EngineCommandNode):
        parent = node.parent
        while parent is not None:
            if isinstance(parent, (p.WatchNode, p.AlarmNode)):
                if isinstance(parent.parent, p.ProgramNode):
                    self.has_global_end = True
                    break
            parent = parent.parent

    def check_local_end_block(self, node: p.BlockNode):
        for child in node.get_child_nodes(recursive=True, exclude_blocks=True):
            if isinstance(child, p.EndBlockNode):
                return True
        for child in node.get_child_nodes(recursive=True):
            if isinstance(child, p.EndBlocksNode):
                return True
            if isinstance(child, p.EngineCommandNode) and child.instruction_name in ["Stop", "Restart"]:
                return True
        return False

    def visit_ProgramNode(self, node: p.ProgramNode):
        yield from super().visit_ProgramNode(node)

        if len(self.requires_global_end) > 0 and not self.has_global_end:
            for n in self.requires_global_end:
                self.add_item(self.create_item(n))

    def visit_BlockNode(self, node: p.BlockNode):
        yield from super().visit_BlockNode(node)

        has_end = self.check_local_end_block(node)
        # has_end = False
        # if node.children is not None:
        #     for child in node.children:
        #         if isinstance(child, (PEndBlock, PEndBlocks)):
        #             has_end = True
        #             break
        if not has_end:
            self.requires_global_end.append(node)

    def visit_EndBlockNode(self, node: p.EndBlockNode):
        self.check_global_end_block(node)
        yield

    def visit_EndBlocksNode(self, node: p.EndBlocksNode):
        self.check_global_end_block(node)
        yield

    def visit_EngineCommandNode(self, node: p.EngineCommandNode):
        super().visit_EngineCommandNode(node)
        if node.instruction_name in ["Stop", "Restart"]:
            self.check_global_end_block(node)
        yield


class IndentationCheckAnalyzer(AnalyzerVisitorBase):
    """
    Checks:
    * Presence of indentation error flag from parser
    """

    def create_item(self, node: p.Node):
        return AnalyzerItem(
            "InvalidIndentation",
            "Invalid indentation",
            node,
            AnalyzerItemType.ERROR,
            "This command cannot execute due to incorrect indentation.",
            start=0,
        )

    def visit_Node(self, node: p.Node) -> NodeGenerator:
        yield from ()
        if node.indent_error and not isinstance(node, p.WhitespaceNode):
            self.add_item(self.create_item(node))


class ThresholdCheckAnalyzer(AnalyzerVisitorBase):
    """
    Checks:
    * Thresholds are ordered from smallest to largest.
    """

    def __init__(self):
        super().__init__()
        # Dictionary holding the node with the numerically largest threshold
        # for a given parent block.
        # The "Base" command has the potential to invalidate numerical comparisons.
        # Take for instance a Base for a block which starts out as a measure of time
        # and is later changed to a measure of volume. In this case, numerical
        # comparison makes little sense.
        # The dictionary is reset whenever a "Base" command is encountered to
        # avoid this issue.
        self.max_threshold_in_parent: dict[p.Node, p.Node] = dict()

    def visit_Node(self, node: p.Node) -> NodeGenerator:
        yield from ()

        if not isinstance(node, p.ProgramNode) and node.parent is not None and node.threshold is not None:
            possibly_limiting_node = self.max_threshold_in_parent.get(node.parent, None)
            if possibly_limiting_node is None or (possibly_limiting_node.threshold and node.threshold > possibly_limiting_node.threshold):
                self.max_threshold_in_parent[node.parent] = node
            elif possibly_limiting_node.threshold and node.threshold < possibly_limiting_node.threshold:
                # Create item for the line which is limiting as well as one for the one which is limited.
                self.add_item(AnalyzerItem(
                    "ThresholdOutOfOrder",
                    "Threshold out of order",
                    node,
                    AnalyzerItemType.WARNING,
                    f"This command will not execute at its threshold because it is limited by a prior threshold (line {possibly_limiting_node.position.line+1}).",
                    start=node.position.character,
                ))
                self.add_item(AnalyzerItem(
                    "ThresholdOutOfOrder",
                    "Threshold out of order",
                    possibly_limiting_node,
                    AnalyzerItemType.INFO,
                    f"This command hinders line {node.position.line+1} from executing at its threshold.",
                    start=possibly_limiting_node.position.character,
                ))
                if node.instruction_name == "Base":
                    del self.max_threshold_in_parent[node.parent]
        if node.instruction_name == "Base" and node.parent is not None:
            self.max_threshold_in_parent = {}


class WhitespaceCheckAnalyzer(AnalyzerVisitorBase):
    """
    Fills in node.has_only_trailing_whitespace for whitespace nodes.
    This allows the interpreter to not advance over only white space/comments.
    This allows the use to edit these lines, e.g. append lines to a method while the
    methods is running.
    """

    def __init__(self) -> None:
        super().__init__()
        self.whitespace_nodes: list[p.BlankNode | p.CommentNode] = []

    def is_whitespace_node(self, node: p.Node):
        return isinstance(node, (p.BlankNode, p.CommentNode))

    def visit_BlankNode(self, node):
        self.whitespace_nodes.append(node)
        yield from ()

    def visit_CommentNode(self, node):
        self.whitespace_nodes.append(node)
        yield from ()

    def visit_AlarmNode(self, node):
        self.visit_NodeWithChildren(node)
        yield from super().visit_AlarmNode(node)

    def visit_BlockNode(self, node):
        self.visit_NodeWithChildren(node)
        yield from super().visit_BlockNode(node)

    def visit_ProgramNode(self, node):
        self.visit_NodeWithChildren(node)
        yield from super().visit_ProgramNode(node)

    def visit_WatchNode(self, node):
        self.visit_NodeWithChildren(node)
        yield from super().visit_WatchNode(node)

    def visit_NodeWithChildren(self, node: p.NodeWithChildren):
        for child in node.children:
            if not self.is_whitespace_node(child):
                node._last_non_ws_line = child.position.line

    def analyze(self, n):
        super().analyze(n)

        for node in self.whitespace_nodes:
            if node.parent is not None and node.position.line > node.parent._last_non_ws_line:
                node.has_only_trailing_whitespace = True


class ConditionCheckAnalyzer(AnalyzerVisitorBase):
    """
    Checks:
    * Condition is present for Watch and Alarm
    * Condition contains tag name
    * Spell check of given tag name
    * Given tag name is defined
    * Unit is not defined for compared tag without unit
    * Unit is defined for compared tag with unit
    * Given unit is defined
    * Given unit is compatible with given tag
    """

    def __init__(self, tags: TagValueCollection) -> None:
        super().__init__()
        self.tags = tags

    def __str__(self) -> str:
        items = [str(item) for item in self.items]
        tags = [str(tag) for tag in self.tags]
        return f'{self.__class__.__name__}(items={items}, tags={tags})'

    def visit_WatchNode(self, node: p.WatchNode):
        self.analyze_condition(node)
        return super().visit_WatchNode(node)

    def visit_AlarmNode(self, node: p.AlarmNode):
        self.analyze_condition(node)
        return super().visit_AlarmNode(node)

    def analyze_condition(self, node: p.NodeWithCondition):
        if node.tag_operator_value is None:
            self.add_item(AnalyzerItem(
                "ConditionMissing",
                "Condition missing",
                node,
                AnalyzerItemType.ERROR,
                "A condition is required",
                start=len(node.instruction_part) + 1,
                end=len(node.instruction_part) + 1000  # Valid way to express the whole line
            ))
            return
        assert node.tag_operator_value is not None
        condition = node.tag_operator_value

        tag_name = condition.tag_name
        if tag_name is None or tag_name.strip() == '':
            self.add_item(AnalyzerItem(
                "MissingTag",
                "Missing tag",
                node,
                AnalyzerItemType.ERROR,
                "A condition must start with a tag name"
            ))
            return

        if not self.tags.has(tag_name):
            if len(tag_name) > 2 and self.tags.names:
                similarity = {tag: ratio(tag_name, tag) for tag in self.tags.names}
                most_similar_tag = max(similarity, key=similarity.get)  # type: ignore
                if similarity[most_similar_tag] > 0.7:
                    self.add_item(AnalyzerItem(
                        "UndefinedTag",
                        "Undefined tag",
                        node,
                        AnalyzerItemType.ERROR,
                        f"Did you mean to type '{most_similar_tag}'?",
                        start=node.tag_operator_value.stripped_lhs_range.start.character,
                        end=node.tag_operator_value.stripped_lhs_range.end.character,
                        data=dict(type="fix-typo", fix=most_similar_tag)
                    ))
                    return
            else:
                self.add_item(AnalyzerItem(
                    "UndefinedTag",
                    "Undefined tag",
                    node,
                    AnalyzerItemType.ERROR,
                    f"The tag name '{tag_name}' is not valid",
                    start=node.tag_operator_value.stripped_lhs_range.start.character,
                    end=node.tag_operator_value.stripped_lhs_range.end.character,
                ))
                return

        if condition.op == "":
            self.add_item(AnalyzerItem(
                "MissingOperator",
                "Missing comparator",
                node,
                AnalyzerItemType.ERROR,
                "The tag name in a condition must be followed by a comparator"
            ))
            return

        if condition.rhs == "" or condition.tag_value == "":
            self.add_item(AnalyzerItem(
                "MissingValue",
                "Missing value",
                node,
                AnalyzerItemType.ERROR,
                "The comparator must be followed by a value"
            ))
            return

        tag = self.tags.get(tag_name)

        if tag.unit is None and condition.tag_unit is not None:
            self.add_item(AnalyzerItem(
                "UnexpectedUnit",
                "Unexpected tag unit",
                node,
                AnalyzerItemType.ERROR,
                f"Unit '{condition.tag_unit}' was specified for a tag with no unit",
                start=node.tag_operator_value.tag_unit_range.start.character,
                end=node.tag_operator_value.tag_unit_range.end.character
            ))
            return

        valid_units = get_compatible_unit_names(tag.unit)
        valid_units_str = ""
        if len(valid_units) > 0:
            valid_units_str = " Suggested units: " + ", ".join(valid_units) + "."

        if tag.unit is not None and condition.rhs and condition.rhs.strip() in valid_units and condition.tag_unit is None:
            self.add_item(AnalyzerItem(
                "MissingValue",
                "Missing value",
                node,
                AnalyzerItemType.ERROR,
                "The tag requires that a value is provided.",
                start=node.tag_operator_value.rhs_range.start.character,
                end=node.tag_operator_value.rhs_range.end.character
            ))
            return


        if tag.unit is not None and condition.tag_unit is None:
            self.add_item(AnalyzerItem(
                "MissingUnit",
                "Missing unit",
                node,
                AnalyzerItemType.ERROR,
                "The tag requires that a unit is provided." + valid_units_str,
                start=node.tag_operator_value.stripped_rhs_range.start.character,
                end=node.tag_operator_value.stripped_rhs_range.end.character
            ))
            return

        if tag.unit is not None:
            assert condition.tag_unit is not None
            try:
                comparable = are_comparable(tag.unit, condition.tag_unit)
            except ValueError as vex:
                self.add_item(AnalyzerItem(
                    "InvalidUnit",
                    "Invalid unit",
                    node,
                    AnalyzerItemType.ERROR,
                    str(vex) + "." + valid_units_str,
                    start=node.tag_operator_value.tag_unit_range.start.character,
                    end=node.tag_operator_value.tag_unit_range.end.character
                ))
                return
            if not comparable:
                self.add_item(AnalyzerItem(
                    "IncompatibleUnits",
                    "Incompatible units",
                    node,
                    AnalyzerItemType.ERROR,
                    f"The tag unit '{tag.unit}' is not compatible with the provided unit '{condition.tag_unit}'." + valid_units_str,
                    start=node.tag_operator_value.stripped_range.start.character,
                    end=node.tag_operator_value.stripped_range.end.character
                ))
                return


class SimulateCheckAnalyzer(AnalyzerVisitorBase):
    """
    Checks same as ConditionCheckAnalyzer
    """

    def __init__(self, tags: TagValueCollection) -> None:
        super().__init__()
        self.tags = tags

    def __str__(self) -> str:
        items = [str(item) for item in self.items]
        tags = [str(tag) for tag in self.tags]
        return f'{self.__class__.__name__}(items={items}, tags={tags})'

    def visit_SimulateOffNode(self, node: p.SimulateOffNode):
        tag_name = node.arguments
        if tag_name is None or tag_name == '':
            self.add_item(AnalyzerItem(
                "MissingTag",
                "Missing tag",
                node,
                AnalyzerItemType.ERROR,
                "Argument must start with a tag name"
            ))
        elif not self.tags.has(tag_name):
            if len(tag_name) > 2 and self.tags.names:
                similarity = {tag: ratio(tag_name, tag) for tag in self.tags.names}
                most_similar_tag = max(similarity, key=similarity.get)  # type: ignore
                if similarity[most_similar_tag] > 0.7:
                    self.add_item(AnalyzerItem(
                        "UndefinedTag",
                        "Undefined tag",
                        node,
                        AnalyzerItemType.ERROR,
                        f"Did you mean to type '{most_similar_tag}'?",
                        start=node.stripped_arguments_range.start.character,
                        end=node.stripped_arguments_range.end.character,
                        data=dict(type="fix-typo", fix=most_similar_tag)
                    ))
            else:
                self.add_item(AnalyzerItem(
                    "UndefinedTag",
                    "Undefined tag",
                    node,
                    AnalyzerItemType.ERROR,
                    f"The tag name '{tag_name}' is not valid",
                    start=node.stripped_arguments_range.start.character,
                    end=node.stripped_arguments_range.end.character,
                ))
        return super().visit_SimulateOffNode(node)

    def visit_SimulateNode(self, node: p.SimulateNode):
        if node.tag_operator_value is None:
            self.add_item(AnalyzerItem(
                "AssignmentMissing",
                "Assignment missing",
                node,
                AnalyzerItemType.ERROR,
                "Assignment of a value to a tag is required",
                start=len(node.instruction_part) + 1,
                end=len(node.instruction_part) + 1000  # Valid way to express the whole line
            ))
            return super().visit_SimulateNode(node)
        assert node.tag_operator_value is not None
        condition = node.tag_operator_value

        tag_name = condition.tag_name
        if tag_name is None or tag_name.strip() == '':
            self.add_item(AnalyzerItem(
                "MissingTag",
                "Missing tag",
                node,
                AnalyzerItemType.ERROR,
                "Argument must start with a tag name"
            ))
            return super().visit_SimulateNode(node)

        if not self.tags.has(tag_name):
            if len(tag_name) > 2 and self.tags.names:
                similarity = {tag: ratio(tag_name, tag) for tag in self.tags.names}
                most_similar_tag = max(similarity, key=similarity.get)  # type: ignore
                if similarity[most_similar_tag] > 0.7:
                    self.add_item(AnalyzerItem(
                        "UndefinedTag",
                        "Undefined tag",
                        node,
                        AnalyzerItemType.ERROR,
                        f"Did you mean to type '{most_similar_tag}'?",
                        start=node.tag_operator_value.stripped_lhs_range.start.character,
                        end=node.tag_operator_value.stripped_lhs_range.end.character,
                        data=dict(type="fix-typo", fix=most_similar_tag)
                    ))
                    return super().visit_SimulateNode(node)
            else:
                self.add_item(AnalyzerItem(
                    "UndefinedTag",
                    "Undefined tag",
                    node,
                    AnalyzerItemType.ERROR,
                    f"The tag name '{tag_name}' is not valid",
                    start=node.tag_operator_value.stripped_lhs_range.start.character,
                    end=node.tag_operator_value.stripped_lhs_range.end.character,
                ))
                return super().visit_SimulateNode(node)

        if condition.op != "=":
            self.add_item(AnalyzerItem(
                "MissingOperator",
                "Missing equals symbol",
                node,
                AnalyzerItemType.ERROR,
                "The tag name must be followed by an equals symbol"
            ))
            return super().visit_SimulateNode(node)

        if condition.rhs == "" or condition.tag_value == "":
            self.add_item(AnalyzerItem(
                "MissingValue",
                "Missing value",
                node,
                AnalyzerItemType.ERROR,
                "Equals symbol (=) must be followed by a value"
            ))
            return super().visit_SimulateNode(node)

        tag = self.tags.get(tag_name)

        if tag.unit is None and condition.tag_unit is not None:
            self.add_item(AnalyzerItem(
                "UnexpectedUnit",
                "Unexpected tag unit",
                node,
                AnalyzerItemType.ERROR,
                f"Unit '{condition.tag_unit}' was specified for a tag with no unit",
                start=node.tag_operator_value.tag_unit_range.start.character,
                end=node.tag_operator_value.tag_unit_range.end.character
            ))
            return super().visit_SimulateNode(node)

        valid_units = get_compatible_unit_names(tag.unit)
        valid_units_str = ""
        if len(valid_units) > 0:
            valid_units_str = " Suggested units: " + ", ".join(valid_units) + "."

        if tag.unit is not None and condition.rhs and condition.rhs.strip() in valid_units and condition.tag_unit is None:
            self.add_item(AnalyzerItem(
                "MissingValue",
                "Missing value",
                node,
                AnalyzerItemType.ERROR,
                "The tag requires that a value is provided.",
                start=node.tag_operator_value.stripped_rhs_range.start.character,
                end=node.tag_operator_value.stripped_rhs_range.end.character
            ))
            return super().visit_SimulateNode(node)


        if tag.unit is not None and condition.tag_unit is None:
            self.add_item(AnalyzerItem(
                "MissingUnit",
                "Missing unit",
                node,
                AnalyzerItemType.ERROR,
                "The tag requires that a unit is provided." + valid_units_str,
                start=node.tag_operator_value.stripped_rhs_range.start.character,
                end=node.tag_operator_value.stripped_rhs_range.end.character
            ))
            return super().visit_SimulateNode(node)

        if tag.unit is not None:
            assert condition.tag_unit is not None
            try:
                comparable = are_comparable(tag.unit, condition.tag_unit)
            except ValueError as vex:
                self.add_item(AnalyzerItem(
                    "InvalidUnit",
                    "Invalid unit",
                    node,
                    AnalyzerItemType.ERROR,
                    str(vex) + "." + valid_units_str,
                    start=node.tag_operator_value.tag_unit_range.start.character,
                    end=node.tag_operator_value.tag_unit_range.end.character
                ))
                return super().visit_SimulateNode(node)
            if not comparable:
                self.add_item(AnalyzerItem(
                    "IncompatibleUnits",
                    "Incompatible units",
                    node,
                    AnalyzerItemType.ERROR,
                    f"The tag unit '{tag.unit}' is not compatible with the provided unit '{condition.tag_unit}'." + valid_units_str,
                    start=node.tag_operator_value.stripped_range.start.character,
                    end=node.tag_operator_value.stripped_range.end.character
                ))
                return super().visit_SimulateNode(node)
        return super().visit_SimulateNode(node)


# Show blue squiggly lines notifying that condition is based on a simulated value.
# Possibly uncomment this code at a later time. Right now it does not work
# because UOD tags and their state are cached.
"""
    def visit_WatchNode(self, node: p.WatchNode):
        if node.tag_operator_value and node.tag_operator_value.tag_name:
            if self.tags.has(node.tag_operator_value.tag_name) and self.tags.get(node.tag_operator_value.tag_name).simulated:
                self.add_item(AnalyzerItem(
                    "SimulatedValue",
                    "Tag has simulated value",
                    node,
                    AnalyzerItemType.INFO,
                    f"The value of tag {node.tag_operator_value.tag_name} is simulated.",
                    start=node.tag_operator_value.stripped_lhs_range.start.character,
                    end=node.tag_operator_value.stripped_lhs_range.end.character
                ))
        return super().visit_WatchNode(node)

    def visit_AlarmNode(self, node: p.AlarmNode):
        if node.tag_operator_value and node.tag_operator_value.tag_name:
            if self.tags.has(node.tag_operator_value.tag_name) and self.tags.get(node.tag_operator_value.tag_name).simulated:
                self.add_item(AnalyzerItem(
                    "SimulatedValue",
                    "Tag has simulated value",
                    node,
                    AnalyzerItemType.INFO,
                    f"The value of tag {node.tag_operator_value.tag_name} is simulated.",
                    start=node.tag_operator_value.stripped_lhs_range.start.character,
                    end=node.tag_operator_value.stripped_lhs_range.end.character
                ))
        return super().visit_AlarmNode(node)
"""


class CommandCheckAnalyzer(AnalyzerVisitorBase):
    """
    Checks:
    * Spell check of command name
    * Given command name is defined
    * Arguments pass validation given command argparser
    * Commands that don't accept arguments don't get arguments
    """

    def __init__(self, commands: CommandCollection) -> None:
        super().__init__()
        self.commands = commands

    def __str__(self) -> str:
        items = [str(item) for item in self.items]
        return f'{self.__class__.__name__}(items={items}, commands={self.commands})'

    def visit_InterpreterCommandNode(self, node: p.InterpreterCommandNode):
        yield from ()
        self.check_command_node(node)

    def visit_EngineCommandNode(self, node: p.EngineCommandNode):
        yield from ()
        self.check_command_node(node)

    def visit_UodCommandNode(self, node: p.UodCommandNode):
        yield from ()
        self.check_command_node(node)

    def visit_ErrorInstructionNode(self, node):
        yield from ()
        self.check_command_node(node)

    def check_command_node(self, node: p.Node):
        name = node.instruction_name

        if not self.commands.has(name):
            if len(name) > 2 and self.commands.names:
                similarity = {command: ratio(name, command) for command in self.commands.names}
                most_similar_command = max(similarity, key=similarity.get)  # type: ignore
                if similarity[most_similar_command] > 0.7:
                    self.add_item(AnalyzerItem(
                        "UndefinedCommand",
                        "Undefined command",
                        node,
                        AnalyzerItemType.ERROR,
                        f"Did you mean to type '{most_similar_command}'?",
                        length=len(name),
                        data=dict(type="fix-typo", fix=most_similar_command)
                    ))
                    return
            self.add_item(AnalyzerItem(
                "UndefinedCommand",
                "Undefined command",
                node,
                AnalyzerItemType.ERROR,
                f"The command name '{name}' is not defined.",
                length=len(name)
            ))
            return

        command = self.commands.get(name)

        if command.arg_parser and node.has_argument and command.arg_parser.regex == ArgSpec.NoArgsInstance.regex:
            self.add_item(AnalyzerItem(
                "CommandNoArguments",
                "Commaned takes no arguments",
                node,
                AnalyzerItemType.ERROR,
                "The command does not accept an argument",
                start=node.position.character + len(node.instruction_name or ""),
            ))
            return
        if not command.validate_args(node.arguments):
            self.add_item(AnalyzerItem(
                "CommandArgsInvalid",
                "Invalid command arguments",
                node,
                AnalyzerItemType.ERROR,
                f"The command argument '{node.arguments}' is not valid",
                start=node.position.character + len(node.instruction_name or "") + len(": "),
                length=len(node.arguments)
            ))
            return


class MacroCheckAnalyzer(AnalyzerVisitorBase):
    """
    Checks:
    * "Macro" has an argument
    * "Call macro" has and argument
    * "Call macro" argument is a defined "Macro"
    * "Macro" is not left unused
    * Spell check of "Call macro" argument
    * "Macro" is redefined
    * Macro contains call to itself
    """

    def __init__(self) -> None:
        super().__init__()
        self.macros: dict[str, p.MacroNode] = {}
        self.macro_calls: list[p.CallMacroNode] = []
        self.macros_registered: list[p.MacroNode] = []
        self.macros_called: list[p.MacroNode] = []

    def visit_CallMacroNode(self, node: p.CallMacroNode):
        if node.name is None or node.name.strip() == "":
            self.add_item(AnalyzerItem(
                "MacroCallNameInvalid",
                "Invalid macro call",
                node,
                AnalyzerItemType.ERROR,
                "Call macro must refer to a Macro definition"
            ))
        elif node.name and node.name.strip() not in self.macros:
            similarity = {macro: ratio(node.name.strip(), macro) for macro in self.macros.keys()}
            most_similar_macro = max(similarity, key=similarity.get) if similarity else None  # type: ignore
            if most_similar_macro and similarity[most_similar_macro] > 0.7:
                self.add_item(AnalyzerItem(
                    "MacroCalledNotDefined",
                    "Referenced macro is not defined",
                    node,
                    AnalyzerItemType.ERROR,
                    f"Did you mean to type '{most_similar_macro}'?",
                    start=node.stripped_arguments_range.start.character,
                    end=node.stripped_arguments_range.end.character,
                    data=dict(type="fix-typo", fix=most_similar_macro)
                ))
            else:
                self.add_item(AnalyzerItem(
                    "MacroCalledNotDefined",
                    "Referenced macro is not defined",
                    node,
                    AnalyzerItemType.ERROR,
                    f"Cannot call macro '{node.name.strip()}' because it is not defined",
                    start=node.stripped_arguments_range.start.character,
                    end=node.stripped_arguments_range.end.character,
                ))
        elif node.name and node.name.strip() in self.macros:
            macro_node = self.macros[node.name]
            self.macro_calls.append(node)
            self.macros_called.append(macro_node)
        return super().visit_CallMacroNode(node)

    def visit_MacroNode(self, node: p.MacroNode):
        if node.name is None or node.name.strip() == "":
            self.add_item(AnalyzerItem(
                "MacroNameInvalid",
                "Invalid macro definition",
                node,
                AnalyzerItemType.ERROR,
                "A Macro definition must include a name"
            ))
        if node.name and node.name.strip():
            if node.name.strip() in self.macros:
                previous_macro_with_same_name = self.macros[node.name.strip()]
                self.add_item(AnalyzerItem(
                    "MacroRedefined",
                    "Macro redefined",
                    node,
                    AnalyzerItemType.INFO,
                    f"This macro definition overwrites the previous definition at line {previous_macro_with_same_name.position.line+1}."
                ))
            self.macros[node.name.strip()] = node
            self.macros_registered.append(node)

            cascade = self.macro_calling_macro(node)
            if cascade and node.name in cascade:
                if len(cascade) == 1:
                    self.add_item(AnalyzerItem(
                        "MacroRecursive",
                        "Macro calls itself",
                        node,
                        AnalyzerItemType.ERROR,
                        f'Macro "{node.name}" calls itself. Unfortunately, this is not allowed.'
                    ))
                elif len(cascade) > 1:
                    path = " which calls ".join(f'macro "{link}"' for link in cascade)
                    self.add_item(AnalyzerItem(
                        "MacroRecursive",
                        "Macro calls itself indirectly",
                        node,
                        AnalyzerItemType.ERROR,
                        f'Macro "{node.name}" calls itself by calling {path}. Unfortunately, this is not allowed.'
                    ))

        return super().visit_MacroNode(node)

    def macro_calling_macro(self, node: p.MacroNode, name: str | None = None) -> list[str]:
        '''
        Recurse through macro to produce a path of calls it makes to other macros.
        This is used to identify if a macro will at some point call itself.
        '''
        name = name if name is not None else node.name
        assert node.children is not None
        for child in node.children:
            if isinstance(child, p.CallMacroNode):
                if child.name == name:
                    return [child.name]
                elif child.name in self.macros.keys():
                    return [child.name] + self.macro_calling_macro(self.macros[child.name], name)
        return []

    def analyze(self, n):
        super().analyze(n)

        # Find unused macros
        for macro_node in self.macros_registered:
            if macro_node not in self.macros_called:
                self.add_item(AnalyzerItem(
                    "MacroUnused",
                    "Macro not used",
                    macro_node,
                    AnalyzerItemType.INFO,
                    "This macro is not called"
                ))


class SemanticCheckAnalyzer:
    """ Facade that combines the check analyzers into a single analyzer. """

    def __init__(self, tags: TagValueCollection, commands: CommandCollection) -> None:
        super().__init__()
        self.items: list[AnalyzerItem] = []
        self.analyzers: list[AnalyzerVisitorBase] = [
            UnreachableCodeCheckAnalyzer(),
            InfiniteBlockCheckAnalyzer(),
            IndentationCheckAnalyzer(),
            ThresholdCheckAnalyzer(),
            WhitespaceCheckAnalyzer(),
            ConditionCheckAnalyzer(tags),
            SimulateCheckAnalyzer(tags),
            CommandCheckAnalyzer(commands),
            MacroCheckAnalyzer(),
        ]

    def __str__(self) -> str:
        items = [str(item) for item in self.items]
        return f'{self.__class__.__name__}(items={items})'

    def analyze(self, program: p.ProgramNode):
        for analyzer in self.analyzers:
            analyzer.analyze(program)
            self.items.extend(analyzer.items)

    @property
    def errors(self) -> list[AnalyzerItem]:
        return list([i for i in self.items if i.type == AnalyzerItemType.ERROR])

    @property
    def warnings(self) -> list[AnalyzerItem]:
        return list([i for i in self.items if i.type == AnalyzerItemType.WARNING])
