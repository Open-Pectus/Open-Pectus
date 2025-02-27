from __future__ import annotations
from enum import Enum
import logging
import re
from typing import List

from openpectus.lang.model.pprogram import (
    PCommandWithDuration,
    PComment,
    PErrorInstruction,
    PNode,
    PProgram,
    PBlank,
    PBlock,
    PEndBlock,
    PEndBlocks,
    PWatch,
    PAlarm,
    PMacro,
    PCommand,
    PMark,
    PCallMacro,
    PBatch,
)

from openpectus.lang.exec.tags import TagValueCollection
from openpectus.lang.exec.units import are_comparable
from openpectus.lang.exec.commands import CommandCollection
from openpectus.lang.exec.pinterpreter import PNodeVisitor
from openpectus.lang import float_re, unit_re


logging.basicConfig(format=' %(name)s :: %(levelname)-8s :: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class AnalyzerItemType(Enum):
    HINT = 'HINT',
    INFO = 'INFO',
    WARNING = 'WARNING',
    ERROR = 'ERROR'

class AnalyzerItemRange:
    def __init__(self, line: int, character: int) -> None:
        self.line = line
        self.character = character

class AnalyzerItem:
    def __init__(self,
                 id: str,
                 message: str,
                 node: PNode | None,
                 type: AnalyzerItemType,
                 description: str = "",
                 start: int | None = None,
                 length: int | None = None,
                 end: int | None = None) -> None:
        self.id: str = id
        self.message: str = message
        self.description: str = description
        self.type: AnalyzerItemType = type
        self.node: PNode | None = node
        self.range_start: AnalyzerItemRange = AnalyzerItemRange(0, 0)
        self.range_end: AnalyzerItemRange = AnalyzerItemRange(0, 0)

        # use node for ranges by default
        if node is not None:
            self.range_start = AnalyzerItemRange(node.line or 0, node.indent or 0)
            self.range_end = AnalyzerItemRange(self.range_start.line, 100)

        # if start is given, modify default range start (keep line)
        if start is not None:
            self.range_start.character = start

        if length is not None and end is not None:
            raise ValueError("Specify either length or end, not both")
        # if length or end is given, modify range end (keep line)
        if length is not None:
            self.range_end = AnalyzerItemRange(self.range_start.line, self.range_start.character + length)
        if end is not None:
            self.range_end = AnalyzerItemRange(self.range_start.line, end)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(id="{self.id}", message="{self.message}", type={self.type}, node={self.node})'


class AnalyzerVisitorBase(PNodeVisitor):
    """ Override by specific feature analyzers. """

    def __init__(self) -> None:
        super().__init__()
        self.items: List[AnalyzerItem] = []

    def __str__(self) -> str:
        items = [str(item) for item in self.items]
        return f'{self.__class__.__name__}(items={items})'

    def add_item(self, item: AnalyzerItem):
        self.items.append(item)

    def visit_children(self, children: List[PNode] | None):
        if children is not None:
            for child in children:
                self.visit(child)

    def visit_PProgram(self, node: PProgram):
        self.visit_children(node.children)

    def visit_PBlank(self, node: PBlank):
        pass

    def visit_PMark(self, node: PMark):
        pass

    def visit_PBatch(self, node: PMark):
        pass

    def visit_PCallMacro(self, node: PCallMacro):
        pass

    def visit_PBlock(self, node: PBlock):
        self.visit_children(node.children)

    def visit_PEndBlock(self, node: PEndBlock):
        pass

    def visit_PEndBlocks(self, node: PEndBlocks):
        pass

    def visit_PWatch(self, node: PWatch):
        self.visit_children(node.children)

    def visit_PAlarm(self, node: PAlarm):
        self.visit_children(node.children)

    def visit_PMacro(self, node: PMacro):
        self.visit_children(node.children)

    def visit_PCommand(self, node: PCommand):
        self.visit_children(node.children)

    def visit_PCommandWithDuration(self, node: PCommandWithDuration):
        self.visit_children(node.children)

    def visit_PErrorInstruction(self, node: PErrorInstruction):
        self.visit_children(node.children)

    def visit_PComment(self, node: PComment):
        pass

# --- Enriching analyzers ---

class ConditionEnrichAnalyzer(AnalyzerVisitorBase):
    """ Analyzer that enriches parsed conditions with tag name, value and unit """
    def __init__(self) -> None:
        super().__init__()

    def visit_PWatch(self, node: PWatch):
        self.enrich_condition(node)
        return super().visit_PWatch(node)

    def visit_PAlarm(self, node: PAlarm):
        self.enrich_condition(node)
        return super().visit_PAlarm(node)

    def enrich_condition(self, node: PAlarm | PWatch):
        if node.condition is None:
            return
        c = node.condition
        if c.op is None or c.op not in ['<', '<=', '>', '>=', '==', '=', '!=']:
            return
        if c.lhs is None or c.lhs.strip() == '' or c.rhs is None or c.rhs.strip() == '':
            return
        c.tag_name = c.lhs

        re_rhs = '^' + '(?P<float>' + float_re + ')' + '\\s*' + '(?P<unit>' + unit_re + ')' + '$'
        re_rhs_no_unit = '^' + '(?P<float>' + float_re + ')' + '\\s*$'
        match = re.search(re_rhs, c.rhs)
        if match:  # float with unit
            c.tag_value = match.group('float')
            c.tag_value_numeric = float(c.tag_value or "")
            c.tag_unit = match.group('unit')
            c.error = False
        else:
            match = re.search(re_rhs_no_unit, c.rhs)
            if match:  # float without unit
                c.tag_value = match.group('float')
                c.tag_value_numeric = float(c.tag_value or "")
                c.error = False
            else:  # str
                c.tag_value = c.rhs
                c.error = False


class DurationEnrichAnalyzer(AnalyzerVisitorBase):
    """ Analyzer that enriches parsed durations with time and unit """
    def __init__(self) -> None:
        super().__init__()

    def visit_PCommandWithDuration(self, node: PCommandWithDuration):
        self.enrich_duration(node)
        return super().visit_PCommandWithDuration(node)

    def enrich_duration(self, node: PCommandWithDuration):
        if node.duration is None:
            return
        d = node.duration

        re_time_unit = '^' + '(?P<float>' + float_re + ')' + '\\s*' + '(?P<unit>' + unit_re + ')' + '$'
        # re_time = '^' + '(?P<float>' + float_re + ')' + '\\s*$'
        match = re.search(re_time_unit, d.duration_str)
        if match:
            d.time = float(match.group('float'))
            d.unit = match.group('unit')
            d.error = False
        # Removed in #437 although there was a test specifically for this.
        # Cannot think of a situation where as duration would be valid without a unit.
        # else:
        #     match = re.search(re_time, d.duration_str)
        #     if match:
        #         d.time = float(match.group('float'))
        #         d.error = False


class EnrichAnalyzer:
    """ Facade that combines the enrich analyzers into a single analyzer. """

    def __init__(self) -> None:
        super().__init__()
        self.analyzers = [
            ConditionEnrichAnalyzer(),
            DurationEnrichAnalyzer(),
        ]

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'

    def analyze(self, program: PProgram):
        for analyzer in self.analyzers:
            analyzer.visit(program)


# --- Check analyzers ---

class UnreachableCodeCheckAnalyzer(AnalyzerVisitorBase):
    """ Analyser that checks for unreachable code """

    def create_item(self, node: PNode):
        return AnalyzerItem(
            "UnreachableCode",
            "Unreachable code",
            node,
            AnalyzerItemType.WARNING,
            "There is no path to this code."
        )

    def visit_PBlock(self, node: PBlock):
        has_end = False
        if node.children is not None:
            for child in node.children:
                if isinstance(child, (PEndBlock, PEndBlocks)):
                    has_end = True
                    continue
                if has_end:
                    self.add_item(self.create_item(child))


class InfiniteBlockCheckAnalyzer(AnalyzerVisitorBase):
    """ Analyser that checks for non-terminated blocks """

    def create_item(self, node: PNode):
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
        self.requires_global_end: List[PNode] = []

    def __str__(self) -> str:
        items = [str(item) for item in self.items]
        return f'{self.__class__.__name__}(items={items}, has_global_end={self.has_global_end})'

    def check_global_end_block(self, node: PEndBlock | PEndBlocks):
        p = node.parent
        while p is not None:
            if isinstance(p, (PWatch, PAlarm)):
                if isinstance(p.parent, PProgram):
                    self.has_global_end = True
                    break
            p = p.parent

    def check_local_end_block(self, node: PBlock):
        for child in node.get_child_nodes(recursive=True):
            if isinstance(child, (PEndBlock, PEndBlocks)):
                return True
        return False

    def visit_PProgram(self, node: PProgram):
        super().visit_PProgram(node)

        if len(self.requires_global_end) > 0 and not self.has_global_end:
            for n in self.requires_global_end:
                self.add_item(self.create_item(n))

    def visit_PBlock(self, node: PBlock):
        super().visit_PBlock(node)

        has_end = self.check_local_end_block(node)
        # has_end = False
        # if node.children is not None:
        #     for child in node.children:
        #         if isinstance(child, (PEndBlock, PEndBlocks)):
        #             has_end = True
        #             break
        if not has_end:
            self.requires_global_end.append(node)

    def visit_PEndBlock(self, node: PEndBlock):
        self.check_global_end_block(node)

    def visit_PEndBlocks(self, node: PEndBlocks):
        self.check_global_end_block(node)


class ConditionCheckAnalyzer(AnalyzerVisitorBase):
    """ Analyser that checks whether conditions are present and refer to valid tag names """

    def __init__(self, tags: TagValueCollection) -> None:
        super().__init__()
        self.tags = tags

    def __str__(self) -> str:
        items = [str(item) for item in self.items]
        tags = [str(tag) for tag in self.tags]
        return f'{self.__class__.__name__}(items={items}, tags={tags})'

    def visit_PWatch(self, node: PWatch):
        self.analyze_condition(node)
        super().visit_PWatch(node)

    def visit_PAlarm(self, node: PAlarm):
        self.analyze_condition(node)
        super().visit_PAlarm(node)

    def analyze_condition(self, node: PWatch | PAlarm):
        assert node.line is not None
        assert node.instruction_name is not None

        if node.condition is None:
            self.add_item(AnalyzerItem(
                "ConditionMissing",
                "Condition missing",
                node,
                AnalyzerItemType.ERROR,
                "A condition is required",
                start=len(node.instruction_name) + 1,
                end=len(node.instruction_name) + 1000  # Valid way to express the whole line
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
                start=node.condition.start_column,
                end=node.condition.start_column
            ))
            return

        if not self.tags.has(tag_name):
            self.add_item(AnalyzerItem(
                "UndefinedTag",
                "Undefined tag",
                node,
                AnalyzerItemType.ERROR,
                f"The tag name '{tag_name}' is not valid",
                start=node.condition.start_column,
                length=len(node.condition.lhs)
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
                start=node.condition.rhs_start,
                end=node.condition.rhs_end + 1
            ))
            return

        if tag.unit is not None and condition.tag_unit is None:
            self.add_item(AnalyzerItem(
                "MissingUnit",
                "Missing tag unit",
                node,
                AnalyzerItemType.ERROR,
                "The tag requires that a unit is provided",
                start=node.condition.rhs_start,
                end=node.condition.rhs_end + 1
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
                    start=node.condition.rhs_start,
                    end=node.condition.rhs_end + 1
                ))
                return
            if not comparable:
                self.add_item(AnalyzerItem(
                    "IncompatibleUnits",
                    "Incompatible units",
                    node,
                    AnalyzerItemType.ERROR,
                    f"The tag unit '{tag.unit}' is not compatible with the provided unit '{condition.tag_unit}'",
                    start=node.condition.rhs_start,
                    end=node.condition.rhs_end + 1
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

    def visit_PCommand(self, node: PCommand):
        assert node.name is not None
        name = node.name

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
        if not command.validate_args(node.args):
            self.add_item(AnalyzerItem(
                "CommandArgsInvalid",
                "Invalid command arguments",
                node,
                AnalyzerItemType.ERROR,
                f"The command argument '{node.args}' is not valid",
                start=(node.indent or 0) + len(node.instruction_name or "") + len(": "),
                length=len(node.args)
            ))
            return

    def visit_PCommandWithDuration(self, node: PCommandWithDuration):
        assert node.name is not None
        name = node.name

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

        # command = self.commands.get(name)
        # interesting case here - who should validate the args?
        # the command def or the node? The command def must be able to do it
        # because it needs to in lsp
        # if we decide to parse in full depth we will have a result
        # but what about an error message
        # if not command.validate_args(node.args):
        
        # seems it was already run? probably by an enhance analyzer
        # node.collect_errors()
        if node.errors is not None:
            for err in node.errors:
                self.add_item(AnalyzerItem(
                    "CommandArgsInvalid",
                    "Invalid command arguments",
                    node,
                    AnalyzerItemType.ERROR,
                    err.message or "",
                    start=(node.indent or 0) + len(node.instruction_name or "") + len(": "),
                    length=100  # TODO we should make the node length available 
                ))
            return


class MacroCheckAnalyzer(AnalyzerVisitorBase):
    def __init__(self) -> None:
        super().__init__()
        self.macros: list[PMacro] = []
        self.macro_calls: list[PCallMacro] = []

    def visit_PCallMacro(self, node: PCallMacro):
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
        return super().visit_PCallMacro(node)

    def visit_PMacro(self, node: PMacro):
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
        return super().visit_PMacro(node)

    def visit_PProgram(self, node: PProgram):
        super().visit_PProgram(node)

        for call in self.macro_calls:
            if call.name not in [m.name for m in self.macros]:
                self.add_item(AnalyzerItem(
                    "MacroCallInvalid",
                    "Invalid macro call",
                    call,
                    AnalyzerItemType.ERROR,
                    f"Cannot call macro {call.name} because it is not defined"
                ))


class SemanticCheckAnalyzer:
    """ Facade that combines the check analyzers into a single analyzer. """

    def __init__(self, tags: TagValueCollection, commands: CommandCollection) -> None:
        super().__init__()
        self.items: List[AnalyzerItem] = []
        self.analyzers = [
            UnreachableCodeCheckAnalyzer(),
            InfiniteBlockCheckAnalyzer(),
            ConditionCheckAnalyzer(tags),
            CommandCheckAnalyzer(commands),
            MacroCheckAnalyzer(),
        ]

    def __str__(self) -> str:
        items = [str(item) for item in self.items]
        return f'{self.__class__.__name__}(items={items})'

    def analyze(self, program: PProgram):
        for analyzer in self.analyzers:
            analyzer.visit(program)
            self.items.extend(analyzer.items)

    @property
    def errors(self) -> List[AnalyzerItem]:
        return list([i for i in self.items if i.type == AnalyzerItemType.ERROR])

    @property
    def warnings(self) -> List[AnalyzerItem]:
        return list([i for i in self.items if i.type == AnalyzerItemType.WARNING])
