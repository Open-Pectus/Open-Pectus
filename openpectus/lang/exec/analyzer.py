from __future__ import annotations
from enum import Enum
import logging

from openpectus.lang.exec.visitor import NodeVisitor
import openpectus.lang.model.ast as p
from openpectus.lang.exec.tags import TagValueCollection
from openpectus.lang.exec.units import are_comparable
from openpectus.lang.exec.commands import CommandCollection


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
                 node: p.Node | None,
                 type: AnalyzerItemType,
                 description: str = "",
                 start: int | None = None,
                 length: int | None = None,
                 end: int | None = None) -> None:
        self.id: str = id
        self.message: str = message
        self.description: str = description
        self.type: AnalyzerItemType = type
        self.node: p.Node | None = node
        self.range: p.Range = p.Range.empty

        # use node for ranges by default
        if node is not None:
            self.range.start = node.position
            if node.threshold:
                self.range.start.character += len(node.threshold_part) + 1

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

    def __str__(self) -> str:
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
    """ Analyser that checks for unreachable code """

    def create_item(self, node: p.Node):
        return AnalyzerItem(
            "UnreachableCode",
            "Unreachable code",
            node,
            AnalyzerItemType.WARNING,
            "There is no path to this code."
        )

    def visit_BlockNode(self, node: p.BlockNode):
        has_end = False
        if node.children is not None:
            for child in node.children:
                if isinstance(child, (p.EndBlockNode, p.EndBlocksNode)):
                    has_end = True
                    continue
                if has_end:
                    self.add_item(self.create_item(child))
        return super().visit_BlockNode(node)


class InfiniteBlockCheckAnalyzer(AnalyzerVisitorBase):
    """ Analyser that checks for non-terminated blocks """

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

    def check_global_end_block(self, node: p.EndBlockNode | p.EndBlocksNode):
        parent = node.parent
        while parent is not None:
            if isinstance(parent, (p.WatchNode, p.AlarmNode)):
                if isinstance(parent.parent, p.ProgramNode):
                    self.has_global_end = True
                    break
            parent = parent.parent

    def check_local_end_block(self, node: p.BlockNode):
        for child in node.get_child_nodes(recursive=True):
            if isinstance(child, (p.EndBlockNode, p.EndBlocksNode)):
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


class ConditionCheckAnalyzer(AnalyzerVisitorBase):
    """ Analyser that checks whether conditions are present and refer to valid tag names """

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

    def analyze_condition(self, node: p.WatchNode | p.AlarmNode):
        if node.condition is None:
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
        assert node.condition is not None
        condition = node.condition

        tag_name = condition.tag_name
        if tag_name is None or tag_name.strip() == '':
            self.add_item(AnalyzerItem(
                "MissingTag",
                "Missing tag",
                node,
                AnalyzerItemType.ERROR,
                "A condition must start with a tag name",
                start=node.condition.range.start.character,
                end=node.condition.range.end.character
            ))
            return

        if not self.tags.has(tag_name):
            self.add_item(AnalyzerItem(
                "UndefinedTag",
                "Undefined tag",
                node,
                AnalyzerItemType.ERROR,
                f"The tag name '{tag_name}' is not valid",
                start=node.condition.lhs_range.start.character,
                end=node.condition.lhs_range.end.character,
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
                start=node.condition.rhs_range.start.character,
                end=node.condition.rhs_range.end.character
            ))
            return

        if tag.unit is not None and condition.tag_unit is None:
            self.add_item(AnalyzerItem(
                "MissingUnit",
                "Missing tag unit",
                node,
                AnalyzerItemType.ERROR,
                "The tag requires that a unit is provided",
                start=node.condition.rhs_range.start.character,
                end=node.condition.rhs_range.end.character
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
                    str(vex),
                    start=node.condition.rhs_range.start.character,
                    end=node.condition.rhs_range.end.character
                ))
                return
            if not comparable:
                self.add_item(AnalyzerItem(
                    "IncompatibleUnits",
                    "Incompatible units",
                    node,
                    AnalyzerItemType.ERROR,
                    f"The tag unit '{tag.unit}' is not compatible with the provided unit '{condition.tag_unit}'",
                    start=node.condition.range.start.character,
                    end=node.condition.range.end.character
                ))
                return


class CommandCheckAnalyzer(AnalyzerVisitorBase):
    """ Analyzer that checks commands and arguments. """

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
            self.add_item(AnalyzerItem(
                "UndefinedCommand",
                "Undefined command",
                node,
                AnalyzerItemType.ERROR,
                f"The command name '{name}' is not valid",
                length=len(name)
            ))
            return

        command = self.commands.get(name)
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
    def __init__(self) -> None:
        super().__init__()
        self.macros: list[p.MacroNode] = []
        self.macro_calls: list[p.CallMacroNode] = []

    def visit_CallMacroNode(self, node: p.CallMacroNode):
        if node.name is None or node.name.strip() == "":
            self.add_item(AnalyzerItem(
                "MacroCallNameInvalid",
                "Invalid macro call",
                node,
                AnalyzerItemType.ERROR,
                "Call macro must refer to a Macro definition"
            ))
        else:
            self.macro_calls.append(node)
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
        else:
            self.macros.append(node)
        return super().visit_MacroNode(node)

    def visit_ProgramNode(self, node: p.ProgramNode):
        yield from super().visit_ProgramNode(node)

        for call in self.macro_calls:
            if call.name not in [m.name for m in self.macros]:
                self.add_item(AnalyzerItem(
                    "MacroCallInvalid",
                    "Invalid macro call",
                    call,
                    AnalyzerItemType.ERROR,
                    f"Cannot call macro {call.name} because it is not defined"
                ))
        yield


class SemanticCheckAnalyzer:
    """ Facade that combines the check analyzers into a single analyzer. """

    def __init__(self, tags: TagValueCollection, commands: CommandCollection) -> None:
        super().__init__()
        self.items: list[AnalyzerItem] = []
        self.analyzers: list[AnalyzerVisitorBase] = [
            UnreachableCodeCheckAnalyzer(),
            InfiniteBlockCheckAnalyzer(),
            ConditionCheckAnalyzer(tags),
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
