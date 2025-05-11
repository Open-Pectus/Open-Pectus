from __future__ import annotations
import functools
import logging
import time

from pylsp.workspace import Document
from pylsp.lsp import DiagnosticSeverity, SymbolKind

from openpectus.lang.exec.uod import RegexNamedArgumentParser
from openpectus.lang.exec.analyzer import AnalyzerItem, SemanticCheckAnalyzer
from openpectus.lang.exec.commands import Command, CommandCollection
from openpectus.lang.exec.tags import TagValue, TagValueCollection
from openpectus.lang.exec.units import get_compatible_unit_names
import openpectus.lang.model.ast as p
from openpectus.lang.model.parser import ParserMethod, create_method_parser, lsp_parse_line, Grammar, PcodeParser
from openpectus.lsp.model import (
    CompletionItem, CompletionItemKind, Diagnostics,
    DocumentSymbol, Position, Range,
    Hover, MarkupContent,
    get_item_range, get_item_severity
)

import openpectus.aggregator.routers.dto as Dto
import openpectus.protocol.models as ProMdl


logger = logging.getLogger(__name__)

operator_descriptions = {
    "<": "less than",
    "<=": "less than or equal",
    ">": "greater than",
    ">=": "greater than or equal",
    "==": "equal",
    "=": "equal",
    "!=": "not equal",
}

@functools.cache
def fetch_uod_info(engine_id: str) -> ProMdl.UodDefinition | None:
    from openpectus.lsp.config import aggregator

    if not aggregator:
        return None
    engine_data = aggregator.get_registered_engine_data(engine_id)
    if not engine_data:
        return None

    return engine_data.uod_definition


def fetch_process_value(engine_id: str, tag_name) -> ProMdl.TagValue | None:
    from openpectus.lsp.config import aggregator

    if not aggregator:
        return None
    engine_data = aggregator.get_registered_engine_data(engine_id)
    if not engine_data:
        return None

    for tag_name_, tag_value in engine_data.tags_info.map.items():
        if tag_name_ == tag_name:
            return tag_value


def build_tags(uod_def: ProMdl.UodDefinition) -> TagValueCollection:
    return TagValueCollection([TagValue(name=t.name, unit=t.unit) for t in uod_def.tags])


def build_commands(uod_def: ProMdl.UodDefinition) -> CommandCollection:
    cmds = []
    for c_def in uod_def.commands + uod_def.system_commands:
        try:
            parser = RegexNamedArgumentParser.deserialize(c_def.validator, c_def.name) \
                if c_def.validator is not None else None

            # build a validate function using the command's own validate function
            def outer(key: str, parser: RegexNamedArgumentParser | None):
                logger.debug(f"Building validator for '{key}': {parser.regex if parser else '(no parser)'}")

                def validate(args: str) -> bool:
                    # parser_name = parser.name if parser is not None else "(parser none)"
                    # logger.debug(f"Validating args '{args}' for command key '{key}' and parser name {parser_name}")
                    if parser is None:
                        return True
                    else:
                        return parser.validate(args)
                return validate

            cmd = Command(c_def.name, validatorFn=outer(c_def.name, parser), arg_parser=parser, docstring=c_def.docstring)
            cmds.append(cmd)
        except Exception:
            logger.error(f"Failed to build command '{c_def.name}'", exc_info=True)

    return CommandCollection(cmds)


class AnalysisInput:
    def __init__(self, commands: CommandCollection, tags: TagValueCollection, engine_id: str):
        self.commands: CommandCollection = commands
        self.tags: TagValueCollection = tags
        self.engine_id: str = engine_id
        self.command_completions = [c.name for c in self.commands.to_list()]
        self.tag_completions = [t.name for t in self.tags]

    def get_command_completions(self, query: str) -> list[str]:
        return [c for c in self.command_completions if c.lower().startswith(query.lower())] + []

    def get_tag_completions(self, query: str) -> list[str]:
        if query:
            return [tag for tag in self.tag_completions if tag.lower().startswith(query.lower())]
        else:
            return self.tag_completions

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(engine_id="{self.engine_id}", commands={self.commands}, tags={self.tags})'


@functools.cache
def create_analysis_input(engine_id: str) -> AnalysisInput:
    uod_def = fetch_uod_info(engine_id)
    if uod_def is None:
        logger.error(f"Failed to load uod definition (was none) for engine: {engine_id}")
        raise RuntimeError("Failed to fetch uod_info")
    logger.info("Building validation commands+tags")
    return AnalysisInput(
        commands=build_commands(uod_def),
        tags=build_tags(uod_def),
        engine_id=engine_id
    )


class AnalysisResult:
    def __init__(self, program: p.ProgramNode, items: list[AnalyzerItem], input: AnalysisInput):
        self.program = program
        self.items = items
        self.input = input

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(program="{self.program}", commands={self.items}, tags={self.input})'


def analyze(input: AnalysisInput, document: Document) -> AnalysisResult:
    """ Parse document as pcode and run semantic analysis on it """
    t1 = time.perf_counter()
    logger.debug(f"Starting new analysis, ver: {document.version}")
    pcode = document.source
    method = ParserMethod.from_pcode(pcode)
    parser = create_method_parser(method, uod_command_names=[])
    try:
        program = parser.parse_method(method)
    except Exception as ex:
        logger.error(f"Failed to build program: '{pcode}'", exc_info=True)
        raise ex
    try:
        analyzer = SemanticCheckAnalyzer(input.tags, input.commands)
        analyzer.analyze(program)
    except Exception as ex:
        logger.error(f"Failed to analyze program: '{pcode}'", exc_info=True)
        raise ex
    result = AnalysisResult(program, analyzer.items, input)
    dt = time.perf_counter() - t1
    logger.debug(f"Analysis completed, ver: {document.version}, duration: {dt:0.2f}s")
    return result


def lint(document: Document, engine_id: str) -> list[Diagnostics]:
    diagnostics: list[Diagnostics] = []
    logger.debug(f"lint called | {engine_id=} | {document.version=}")
    try:
        analysis_input = create_analysis_input(engine_id)
        analysis_result = analyze(analysis_input, document)
    except Exception as ex:
        logger.error("Failed to build program: '{pcode}'", exc_info=True)
        diagnostics.append(
            Diagnostics(
                source="Open Pectus",
                range=Range(
                    start=Position(line=0, character=1),
                    end=Position(line=0, character=100)
                ),
                code="Parse error",
                message="Syntax error: " + str(ex),
                severity=DiagnosticSeverity.Error,
                data={},
            )
        )
        return diagnostics

    if analysis_result is None:
        return diagnostics

    # map analyzer result to lsp diagnostics
    for item in analysis_result.items:
        diagnostics.append(
            Diagnostics(
                source="Open Pectus",
                range=get_item_range(item),
                code=item.message,
                message=item.description,
                severity=get_item_severity(item),
                data=item.data
            )
        )

    # log unspecific errors
    if analysis_result.program.has_error():
        logger.error(f"Program errors: {len(analysis_result.program.errors)}")
        for error in analysis_result.program.errors:
            logger.error(error.message)

    return diagnostics

def starts_with_any(query: str, candidates: list[str]) -> bool:
    """ Return True if query starts with any of the candidates """
    for candidate in candidates:
        if query.startswith(candidate):
            return True
    return False


def ends_with_any(query: str, candidates: list[str]) -> bool:
    """ Return True if query ends with any of the candidates """
    for candidate in candidates:
        if query.endswith(candidate):
            return True
    return False


def contains_any(query: str, candidates: list[str]) -> bool:
    """ Return True if query contains any of the candidates """
    for candidate in candidates:
        if candidate in query:
            return True
    return False


def hover(document: Document, position: Position, engine_id: str) -> Hover | None:
    analysis_input = create_analysis_input(engine_id)
    line = get_line(document, position)
    if not line:
        return
    pcode_parser = PcodeParser()
    node = pcode_parser._parse_line(line, position["line"])
    position_ast = ast_position_from_lsp_position(position)
    if node and node.instruction_name in analysis_input.commands.names:
        # Check if hovering instruction name
        if position_ast in node.instruction_range:
            docstring = analysis_input.commands.get(node.instruction_name).docstring
            return Hover(
                contents=MarkupContent(
                    kind="markdown",
                    value=docstring if docstring else "",
                ),
                range=lsp_range_from_ast_range(node.instruction_range),
            )
        # Check if argument
        arg_parser = analysis_input.commands.get(node.instruction_name).arg_parser
        if node.arguments_part and arg_parser:
            if position_ast in node.arguments_range:
                units = arg_parser.get_units()
                units_str = ", ".join(units)
                if len(units) == 1:
                    return Hover(
                        contents=MarkupContent(
                            kind="markdown",
                            value=f"Specify a value with unit '{units_str}'.",
                        ),
                        range=lsp_range_from_ast_range(node.arguments_range),
                    )
                elif len(units) > 1:
                    return Hover(
                        contents=MarkupContent(
                            kind="markdown",
                            value=f"Specify a value with one of the following units: {units_str}.",
                        ),
                        range=lsp_range_from_ast_range(node.arguments_range),
                    )
                additive_options = arg_parser.get_additive_options()
                exclusive_options = arg_parser.get_exclusive_options()
                if additive_options and not exclusive_options:
                    options_str = ", ".join(additive_options)
                    return Hover(
                        contents=MarkupContent(
                            kind="markdown",
                            value=f"Specify one or more (separate with +) of the following options: {options_str}.",
                        ),
                        range=lsp_range_from_ast_range(node.arguments_range),
                    )
                elif not additive_options and exclusive_options:
                    options_str = ", ".join(exclusive_options)
                    return Hover(
                        contents=MarkupContent(
                            kind="markdown",
                            value=f"Specify one of the following options: {options_str}",
                        ),
                        range=lsp_range_from_ast_range(node.arguments_range),
                    )
                elif additive_options and exclusive_options:
                    options_str = ", ".join(additive_options+exclusive_options)
                    return Hover(
                        contents=MarkupContent(
                            kind="markdown",
                            value=f"Specify one or possibly more of the following options: {options_str}.",
                        ),
                        range=lsp_range_from_ast_range(node.arguments_range),
                    )
        # Check if condition
        if isinstance(node, p.NodeWithCondition) and node.condition:
            if analysis_input.tags.has(node.condition.lhs) and position_ast in node.condition.lhs_range:
                process_value = fetch_process_value(engine_id, node.condition.lhs)
                if not process_value:
                    return
                value_str = ""
                if process_value.value_formatted:
                    value_str = process_value.value_formatted
                elif process_value.value and process_value.value_unit:
                    value = f"{process_value.value:0.2f}".replace(".", ",") if isinstance(process_value.value, float) else str(process_value.value)
                    value_str = value + " " + process_value.value_unit
                elif process_value.value:
                    value_str = str(process_value.value)
                return Hover(
                    contents=MarkupContent(
                        kind="markdown",
                        value=f"Current value: {value_str}",
                    ),
                    range=lsp_range_from_ast_range(node.condition.lhs_range),
                )

            if position_ast in node.condition.op_range:
                return Hover(
                    contents=MarkupContent(
                        kind="markdown",
                        value=operator_descriptions[node.condition.op],
                    ),
                    range=lsp_range_from_ast_range(node.condition.op_range),
                )

            unit_options = units_compaible_with_tag(analysis_input, node.condition.lhs)
            unit_options_str = ", ".join(unit_options)
            if unit_options_str and position_ast in node.condition.rhs_range:
                if len(unit_options) >= 1:
                    return Hover(
                        contents=MarkupContent(
                            kind="markdown",
                            value=f"Comparison value unit{'s' if len(unit_options) > 1 else ''}: {unit_options_str}.",
                        ),
                    range=lsp_range_from_ast_range(node.condition.rhs_range),
                    )


def completions(document: Document, position: Position, ignored_names, engine_id: str) -> list[CompletionItem]:
    # Return a list of completion items because pylsp encapsulates it in a CompletionList for us
    analysis_input = create_analysis_input(engine_id)
    line = get_line(document, position)
    if line is None:
        # Show all possible commands
        return [
            CompletionItem(label=command_name, kind=CompletionItemKind.Function, preselect=False)
            for command_name in analysis_input.commands.names
        ]

    # get whole query, eg "St" or "Alarm: Run T"
    char: int = position["character"]
    if char < len(line):
        query = line[0:char]
    else:
        query = line
    pcode_parser = PcodeParser()
    node = pcode_parser._parse_line(line, position["line"])
    position_ast = ast_position_from_lsp_position(position)

    if node:
        if node.instruction_name in analysis_input.commands.names:
            # Completion of Watch/Alarm which are special because of conditions
            if isinstance(node, p.NodeWithCondition) and node.condition:
                # Complete tag name
                if position_ast in node.condition.lhs_range or (node.condition.lhs == "" and node.arguments_part.strip() not in analysis_input.tags.names):
                    prefix = " " if query.endswith(":") else ""
                    if node.condition.lhs_range.is_empty():
                        return [
                            CompletionItem(
                                label=name,
                                insertText=prefix+name,
                                kind=CompletionItemKind.Enum,
                                preselect=False,
                            )
                            for name in analysis_input.get_tag_completions(node.condition.lhs)
                        ]
                    else:
                        return [
                            CompletionItem(
                                label=name,
                                kind=CompletionItemKind.Enum,
                                preselect=False,
                                textEdit=TextEdit(range=lsp_range_from_ast_range(node.condition.lhs_range), newText=prefix+name),
                            )
                            for name in analysis_input.get_tag_completions(node.condition.lhs)
                        ]
                # Complete operator
                elif position_ast in node.condition.op_range or node.condition.op_range.is_empty():
                    prefix = "" if query.endswith(" ") else " "
                    if node.condition.op_range.is_empty():
                        return [
                            CompletionItem(
                                label=f"{operator} ({operator_description})",
                                insertText=prefix+operator,
                                kind=CompletionItemKind.Enum,
                                preselect=False,
                            )
                            for operator, operator_description in operator_descriptions.items()
                        ]
                    else:
                        return [
                            CompletionItem(
                                label=f"{operator} ({operator_description})",
                                kind=CompletionItemKind.Enum,
                                preselect=False,
                                textEdit=TextEdit(range=lsp_range_from_ast_range(node.condition.op_range), newText=prefix+operator),
                            )
                            for operator, operator_description in operator_descriptions.items()
                        ]
                # Complete unit
                elif position_ast in node.condition.rhs_range or position_ast.character > node.condition.op_range.end.character:
                    prefix = "" if query.endswith(" ") else " "
                    unit_options = units_compaible_with_tag(analysis_input, node.condition.lhs)
                    if len(unit_options) > 0:
                        return [
                            CompletionItem(
                                label=unit,
                                insertText=prefix+unit,
                                kind=CompletionItemKind.Enum,
                                preselect=False,
                            )
                            for unit in unit_options
                        ]
            # Completion of all other commands
            elif node.instruction_name in analysis_input.commands.names:
                arg_parser = analysis_input.commands.get(node.instruction_name).arg_parser
                prefix = " " if query.endswith(":") else ""
                if arg_parser:
                    options = arg_parser.get_additive_options()+arg_parser.get_exclusive_options()+arg_parser.get_units()
                    # Complete additive options
                    if node.arguments_part.endswith("+"):
                        return [
                            CompletionItem(
                                label=name,
                                insertText=prefix+name,
                                kind=CompletionItemKind.Enum,
                                preselect=False,
                            )
                            for name in arg_parser.get_additive_options()
                        ]
                    # Complete additive, exclusive and units
                    if not contains_any(query.split(":")[1].strip(), options):
                        return [
                            CompletionItem(
                                label=name,
                                insertText=prefix+name,
                                kind=CompletionItemKind.Enum,
                                preselect=False,
                            )
                            for name in options
                        ]
        elif node.instruction_name and node.arguments_part == "":
            # Completion of command name
            return [
                CompletionItem(
                    label=word,
                    kind=CompletionItemKind.Function,
                    preselect=False,
                    textEdit=TextEdit(range=lsp_range_from_ast_range(node.instruction_range), newText=word),
                )
                for word in analysis_input.get_command_completions(node.instruction_name)
                ]
    if query.strip() == "":
        # Blank line. Show all possible commands
        return [
            CompletionItem(
                label=command_name,
                kind=CompletionItemKind.Function,
                preselect=False,
            )
            for command_name in analysis_input.commands.names
        ]

    return []

def get_line(document: Document, position: Position) -> str | None:
    for i, line in enumerate(document.lines):
        if position["line"] == i:
            return line

def units_compaible_with_tag(analysis_input: AnalysisInput, tag_name: str) -> list[str]:
    tag = analysis_input.tags.get(tag_name)
    if tag:
        if tag.unit:
            return get_compatible_unit_names(tag.unit)
    return []

def lsp_range_from_ast_range(ast_range: p.Range) -> Range:
    return Range(
        start=Position(
            line=ast_range.start.line,
            character=ast_range.start.character
        ),
        end=Position(
            line=ast_range.end.line,
            character=ast_range.end.character
        )
    )

def ast_position_from_lsp_position(lsp_position: Position) -> p.Position:
    return p.Position(
        line=lsp_position["line"],
        character=lsp_position["character"],
    )