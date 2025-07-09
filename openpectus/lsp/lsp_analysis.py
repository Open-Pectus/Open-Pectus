from __future__ import annotations
import functools
import logging
import time

from pylsp.workspace import Document, Workspace
from pylsp.lsp import DiagnosticSeverity, CompletionItemKind
from pylsp.config.config import Config

from openpectus.lang.exec.uod import RegexNamedArgumentParser
from openpectus.lang.exec.analyzer import AnalyzerItem, SemanticCheckAnalyzer
from openpectus.lang.exec.commands import Command, CommandCollection
from openpectus.lang.exec.tags import TagValue, TagValueCollection
from openpectus.lang.exec.units import get_compatible_unit_names, convert_value_to_unit
from openpectus.lang.exec import visitor
from openpectus.lang.model.parser import ParserMethod, create_method_parser, PcodeParser
from openpectus.lsp.model import (
    CompletionItem, Diagnostic,
    Position, Range, TextEdit,
    Hover, MarkupContent, CodeActionContext,
    CodeAction, WorkspaceEdit,
    get_item_range, get_item_severity
)
from openpectus.lsp.model import Command as LSPCommand
import openpectus.lang.model.ast as p
import openpectus.protocol.models as ProMdl
import openpectus.aggregator.deps as agg_deps


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

def fetch_uod_info(engine_id: str) -> ProMdl.UodDefinition | None:
    aggregator = agg_deps.get_aggregator()

    if not aggregator:
        return None
    engine_data = aggregator.get_registered_engine_data(engine_id)
    if not engine_data:
        return None
    return engine_data.uod_definition


def fetch_process_value(engine_id: str, tag_name) -> ProMdl.TagValue | None:
    aggregator = agg_deps.get_aggregator()

    if not aggregator:
        return None
    engine_data = aggregator.get_registered_engine_data(engine_id)
    if not engine_data:
        return None

    return engine_data.tags_info.map.get(tag_name, None)


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


def lint(document: Document, engine_id: str) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    logger.debug(f"lint called | {engine_id=} | {document.version=}")
    try:
        analysis_input = create_analysis_input(engine_id)
        analysis_result = analyze(analysis_input, document)
    except Exception as ex:
        logger.error(f"Failed to lint program for engine_id: '{engine_id}'", exc_info=True)
        diagnostics.append(
            Diagnostic(
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
            Diagnostic(
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


class MacroVisitor(visitor.NodeVisitor):
    def __init__(self, macro_call: p.CallMacroNode | None = None) -> None:
        super().__init__()
        self.macros: dict[str, p.MacroNode] = {}
        self.macro_calls: list[p.CallMacroNode] = []
        self.macro_call: p.CallMacroNode | None = macro_call
        self.macro_called_by_macro_call: p.MacroNode | None = None

    def visit_CallMacroNode(self, node: p.CallMacroNode):
        if self.macro_call and node.position == self.macro_call.position and node.name.strip() in self.macros:
            self.macro_called_by_macro_call = self.macros[node.name.strip()]
        if node.name is not None and node.name.strip() in self.macros:
            self.macro_calls.append(node)
        return super().visit_CallMacroNode(node)

    def visit_MacroNode(self, node: p.MacroNode):
        if node.name is not None and node.name.strip():
            self.macros[node.name.strip()] = node
        return super().visit_MacroNode(node)


def identify_called_macro(program: p.ProgramNode, macro_call: p.CallMacroNode) -> None | p.MacroNode:
    # Call visitor
    macro_visitor = MacroVisitor(macro_call)
    for _ in macro_visitor.visit(program):
        pass

    return macro_visitor.macro_called_by_macro_call

def get_code_called_by_macro(document: Document, macro_call: p.CallMacroNode) -> None | str:
    # Parse code in document
    pcode = document.source
    method = ParserMethod.from_pcode(pcode)
    parser = create_method_parser(method, uod_command_names=[])
    try:
        program = parser.parse_method(method)
    except Exception:
        return None

    # Identify called macro
    macro_node = identify_called_macro(program, macro_call)
    if macro_node is None:
        return None

    # Calculate range of lines containing macro
    indentation = macro_node.position.character
    line_start = macro_node.position.line
    line_end = line_start + 1
    last_line_not_whitespace = line_start + 1
    for child in reversed(macro_node.children):
        if not isinstance(child, p.WhitespaceNode):
            last_line_not_whitespace = child.position.line
            break
    if len(macro_node.children):
        line_end = last_line_not_whitespace + 1

    # Remove indentation to increase readability and format as pcode
    macro_node_code_lines = ["```pcode\r\n"]
    for line_no, line in enumerate(document.lines):
        if line_start <= line_no <= line_end:
            if len(line) <= indentation:
                macro_node_code_lines.append("\r\n")
            else:
                macro_node_code_lines.append(line[indentation:])
    macro_node_code_lines.append("```")

    return "".join(macro_node_code_lines)

def hover(document: Document, position: Position, engine_id: str) -> Hover | None:
    analysis_input = create_analysis_input(engine_id)
    line = get_line(document, position)
    if not line:
        return
    pcode_parser = PcodeParser()
    node = pcode_parser._parse_line(line, position["line"])
    position_ast = ast_position_from_lsp_position(position)
    if node and node.instruction_name in analysis_input.commands.names:
        arg_parser = analysis_input.commands.get(node.instruction_name).arg_parser
        # Hovering instruction name
        if position_ast in node.instruction_range:
            docstring = analysis_input.commands.get(node.instruction_name).docstring
            return Hover(
                contents=MarkupContent(
                    kind="markdown",
                    value="```pcode\r\n"+docstring+"\r\n```" if docstring else "",
                ),
                range=lsp_range_from_ast_range(node.stripped_instruction_range),
            )
        # Hovering condition
        if isinstance(node, p.NodeWithTagOperatorValue) and node.tag_operator_value:
            # Show current tag value
            if node.tag_operator_value.tag_name and analysis_input.tags.has(node.tag_operator_value.tag_name) and position_ast in node.tag_operator_value.stripped_lhs_range:
                process_value = fetch_process_value(engine_id, node.tag_operator_value.tag_name)
                if not process_value:
                    return
                value_str = ""
                if process_value.value_formatted:
                    value_str = process_value.value_formatted
                elif process_value.value and process_value.value_unit:
                    value = f"{process_value.value:0.2f}".replace(".", ",") if isinstance(process_value.value, float) else str(process_value.value)
                    value_str = value + " " + process_value.value_unit
                    # If the value specified on the RHS has a different measurement unit
                    # than the tag unit, then we want to show the unit in its own unit
                    # as well as the one the user want to compare to.
                    if (node.tag_operator_value.tag_unit and
                       process_value.value_unit != node.tag_operator_value.tag_unit and
                       node.tag_operator_value.tag_unit in units_compaible_with_tag(analysis_input, node.tag_operator_value.lhs) and
                       isinstance(process_value.value, (int, float))):
                        converted_value = convert_value_to_unit(
                            process_value.value,
                            process_value.value_unit,
                            node.tag_operator_value.tag_unit
                        )
                        value_str += " (" + f"{converted_value:0.2f}".replace(".", ",") + f" {node.tag_operator_value.tag_unit})"
                elif process_value.value:
                    value_str = str(process_value.value)
                return Hover(
                    contents=MarkupContent(
                        kind="markdown",
                        value=f"Current value: {value_str}",
                    ),
                    range=lsp_range_from_ast_range(node.tag_operator_value.stripped_lhs_range),
                )
            # Show text desciption of comparison operator
            if position_ast in node.tag_operator_value.op_range:
                return Hover(
                    contents=MarkupContent(
                        kind="plaintext",
                        value=operator_descriptions[node.tag_operator_value.op],
                    ),
                    range=lsp_range_from_ast_range(node.tag_operator_value.op_range),
                )
            # Show compatible units of measurement
            unit_options = units_compaible_with_tag(analysis_input, node.tag_operator_value.lhs)
            unit_options_str = ", ".join(unit_options)
            if unit_options_str and position_ast in node.tag_operator_value.stripped_rhs_range:
                if len(unit_options) >= 1:
                    return Hover(
                        contents=MarkupContent(
                            kind="markdown",
                            value=f"Unit{'s' if len(unit_options) > 1 else ''}: {unit_options_str}.",
                        ),
                        range=lsp_range_from_ast_range(node.tag_operator_value.stripped_rhs_range),
                    )
        # Hovering "Call macro"
        elif isinstance(node, p.CallMacroNode) and position_ast in node.arguments_range:
            code = get_code_called_by_macro(document, node)
            if code is not None:
                return Hover(
                    contents=MarkupContent(
                        kind="markdown",
                        value=code,
                    ),
                    range=lsp_range_from_ast_range(node.arguments_range),
                )
        # Hovering argument
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
                        range=lsp_range_from_ast_range(node.stripped_arguments_range),
                    )
                elif len(units) > 1:
                    return Hover(
                        contents=MarkupContent(
                            kind="markdown",
                            value=f"Specify a value with one of the following units: {units_str}.",
                        ),
                        range=lsp_range_from_ast_range(node.stripped_arguments_range),
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
                        range=lsp_range_from_ast_range(node.stripped_arguments_range),
                    )
                elif not additive_options and exclusive_options:
                    options_str = ", ".join(exclusive_options)
                    return Hover(
                        contents=MarkupContent(
                            kind="markdown",
                            value=f"Specify one of the following options: {options_str}",
                        ),
                        range=lsp_range_from_ast_range(node.stripped_arguments_range),
                    )
                elif additive_options and exclusive_options:
                    options_str = ", ".join(additive_options+exclusive_options)
                    return Hover(
                        contents=MarkupContent(
                            kind="markdown",
                            value=f"Specify one or possibly more of the following options: {options_str}.",
                        ),
                        range=lsp_range_from_ast_range(node.stripped_arguments_range),
                    )


def completions(document: Document, position: Position, ignored_names, engine_id: str) -> list[CompletionItem]:
    # Return a list of completion items because pylsp encapsulates it in a CompletionList for us
    analysis_input = create_analysis_input(engine_id)
    line = get_line(document, position)
    if line is None:
        # Show all possible commands
        return [
            CompletionItem(
                label=command_name,
                insertText=command_name+": " if analysis_input.commands.get(command_name).accepts_arguments else command_name,
                kind=CompletionItemKind.Function,
                command=LSPCommand(title="", command="editor.action.triggerSuggest"),
            )
            for command_name in analysis_input.commands.names
        ]

    # get whole query, eg "St" or "Alarm: Run T"
    char = position["character"]
    if char < len(line):
        query = line[0:char]
    else:
        query = line
    pcode_parser = PcodeParser()
    node = pcode_parser._parse_line(line, position["line"])
    position_ast = ast_position_from_lsp_position(position)
    leading_space = position["character"] > 0 and line[position["character"]-1:position["character"]] == " "
    leading_plus = position["character"] > 0 and line[position["character"]-1:position["character"]] == "+"

    if node:
        if node.instruction_name in analysis_input.commands.names:
            # Completion of Watch/Alarm which are special because of conditions
            if isinstance(node, p.NodeWithTagOperatorValue) and node.tag_operator_value:
                # Complete tag name
                if position_ast in node.tag_operator_value.stripped_lhs_range or (node.tag_operator_value.lhs == "" and node.arguments_part.strip() not in analysis_input.tags.names):
                    prefix = "" if leading_space else " "
                    if node.tag_operator_value.lhs_range.is_empty():
                        return [
                            CompletionItem(
                                label=name,
                                insertText=prefix+name+" ",
                                kind=CompletionItemKind.Enum,
                                command=LSPCommand(title="", command="editor.action.triggerSuggest") if node.tag_operator_value.op == "" else None
                            )
                            for name in analysis_input.get_tag_completions(node.tag_operator_value.lhs)
                        ]
                    else:
                        return [
                            CompletionItem(
                                label=name,
                                kind=CompletionItemKind.Enum,
                                textEdit=TextEdit(
                                    range=lsp_range_from_ast_range(node.tag_operator_value.lhs_range),
                                    newText=" "+name+" "
                                ),
                                command=LSPCommand(title="", command="editor.action.triggerSuggest") if node.tag_operator_value.op == "" else None
                            )
                            for name in analysis_input.get_tag_completions(node.tag_operator_value.lhs)
                        ]
                # Complete operator
                elif position_ast in node.tag_operator_value.op_range or node.tag_operator_value.op == "":
                    prefix = "" if leading_space else " "
                    if node.tag_operator_value.op_range.is_empty():
                        return [
                            CompletionItem(
                                label=f"{operator} ({operator_descriptions[operator]})",
                                insertText=prefix+operator+" ",
                                kind=CompletionItemKind.Enum,
                                command=LSPCommand(title="", command="editor.action.triggerSuggest") if node.tag_operator_value.tag_unit is None else None
                            )
                            for operator in node.operators
                        ]
                    else:
                        return [
                            CompletionItem(
                                label=f"{operator} ({operator_descriptions[operator]})",
                                kind=CompletionItemKind.Enum,
                                textEdit=TextEdit(
                                    range=lsp_range_from_ast_range(node.tag_operator_value.op_range),
                                    newText=operator
                                ),
                                command=LSPCommand(title="", command="editor.action.triggerSuggest") if node.tag_operator_value.tag_unit is None else None
                            )
                            for operator in node.operators
                        ]
                # Complete unit
                elif position_ast in node.tag_operator_value.rhs_range or position_ast > node.tag_operator_value.op_range:
                    prefix = "" if leading_space else " "
                    unit_options = units_compaible_with_tag(analysis_input, node.tag_operator_value.lhs)
                    if len(unit_options) > 0 and node.tag_operator_value.tag_unit is None:
                        return [
                            CompletionItem(
                                label=unit,
                                insertText=prefix+unit,
                                kind=CompletionItemKind.Enum,
                            )
                            for unit in unit_options
                        ]
            # Completion of argument to "Call macro"
            elif isinstance(node, p.CallMacroNode):
                # Parse code in document up until this "Call macro" node
                # to avoid suggesting macros which are not actually defined
                # at the point where this call is made.
                pcode = "\r\n".join(document.source.splitlines()[:node.position.line])
                method = ParserMethod.from_pcode(pcode)
                parser = create_method_parser(method, uod_command_names=[])
                try:
                    program = parser.parse_method(method)
                except Exception:
                    return []
                # Call visitor
                macro_visitor = MacroVisitor()
                for _ in macro_visitor.visit(program):
                    pass
                prefix = "" if leading_space else " "
                if node.arguments_range.is_empty():
                    return [
                        CompletionItem(
                            label=name,
                            insertText=prefix+name,
                            kind=CompletionItemKind.Enum,
                        )
                        for name in list(macro_visitor.macros.keys())
                    ]
                else:
                    return [
                        CompletionItem(
                            label=name,
                            kind=CompletionItemKind.Enum,
                            textEdit=TextEdit(
                                range=lsp_range_from_ast_range(node.arguments_range),
                                newText=prefix+name
                            ),
                        )
                        for name in list(macro_visitor.macros.keys())
                    ]
            elif isinstance(node, p.SimulateOffNode):
                # Complete tag name
                if position_ast in node.arguments_range or node.arguments == "" or node.arguments not in analysis_input.tags.names:
                    prefix = "" if leading_space else " "
                    if node.arguments_range.is_empty():
                        return [
                            CompletionItem(
                                label=name,
                                insertText=prefix+name,
                                kind=CompletionItemKind.Enum,
                            )
                            for name in analysis_input.get_tag_completions(node.arguments)
                        ]
                    else:
                        return [
                            CompletionItem(
                                label=name,
                                kind=CompletionItemKind.Enum,
                                textEdit=TextEdit(
                                    range=lsp_range_from_ast_range(node.arguments_range),
                                    newText=prefix+name
                                ),
                            )
                            for name in analysis_input.get_tag_completions(node.arguments)
                        ]

            # Completion of all other commands
            elif node.instruction_name in analysis_input.commands.names:
                arg_parser = analysis_input.commands.get(node.instruction_name).arg_parser
                prefix = "" if leading_space or leading_plus else " "
                if arg_parser:
                    options = arg_parser.get_additive_options()+arg_parser.get_exclusive_options()+arg_parser.get_units()
                    # Complete additive options
                    if node.arguments.endswith("+"):
                        return [
                            CompletionItem(
                                label=name,
                                insertText=prefix+name,
                                kind=CompletionItemKind.Enum,
                            )
                            for name in arg_parser.get_additive_options() if name not in node.arguments
                        ]
                    # Complete additive, exclusive and units
                    if not contains_any(node.arguments, options):
                        return [
                            CompletionItem(
                                label=name,
                                insertText=prefix+name,
                                kind=CompletionItemKind.Enum,
                            )
                            for name in options
                        ]
        elif node.instruction_name and node.arguments == "":
            # Completion of command name
            return [
                CompletionItem(
                    label=command_name,
                    kind=CompletionItemKind.Function,
                    textEdit=TextEdit(
                        range=lsp_range_from_ast_range(node.instruction_range),
                        newText=command_name+": " if analysis_input.commands.get(command_name).accepts_arguments else command_name,
                    ),
                    command=LSPCommand(title="", command="editor.action.triggerSuggest"),
                )
                for command_name in analysis_input.get_command_completions(node.instruction_name)
                ]
    if query.strip() == "":
        # Blank line. Show all possible commands
        return [
            CompletionItem(
                label=command_name,
                insertText=command_name+": " if analysis_input.commands.get(command_name).accepts_arguments else command_name,
                kind=CompletionItemKind.Function,
                command=LSPCommand(title="", command="editor.action.triggerSuggest")
            )
            for command_name in analysis_input.commands.names
        ]

    return []

def code_actions(config: Config, workspace: Workspace, document: Document, range: Range, context: CodeActionContext) -> list[CodeAction]:
    for diagnostic in context["diagnostics"]:
        data = diagnostic.get("data", None)
        if data:
            if data["type"] == "fix-typo":
                action = CodeAction(
                    title="Fix spelling",
                    kind="quickfix",
                    edit=WorkspaceEdit(
                        changes={
                            document.uri: [TextEdit(range=diagnostic["range"], newText=data["fix"])]
                        },
                    ),
                    diagnostics=[diagnostic],
                )
                return [action]
    return []

def get_line(document: Document, position: Position) -> str | None:
    for i, line in enumerate(document.lines):
        if position["line"] == i:
            return line

def units_compaible_with_tag(analysis_input: AnalysisInput, tag_name: str) -> list[str]:
    try:
        tag = analysis_input.tags.get(tag_name)
    except ValueError:
        return []
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
