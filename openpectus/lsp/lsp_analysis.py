from __future__ import annotations
import functools
import logging
import time
import httpx

from pylsp.workspace import Document
from pylsp.lsp import DiagnosticSeverity, SymbolKind

from openpectus.lang.exec.uod import RegexNamedArgumentParser
from openpectus.lang.exec.analyzer import AnalyzerItem, SemanticCheckAnalyzer
from openpectus.lang.exec.commands import Command, CommandCollection
from openpectus.lang.exec.tags import TagValue, TagValueCollection
from openpectus.lang.model.pprogram import PBlank, PComment, PNode, PProgram
from openpectus.lsp.model import (
    CompletionItem, CompletionItemKind, Diagnostics, DocumentSymbol, Location, Position, Range, SymbolInformation,
    get_item_range, get_item_severity, get_node_range
)
from openpectus.test.engine.utility_methods import build_program
import openpectus.aggregator.routers.dto as Dto


logger = logging.getLogger(__name__)

@functools.cache
def fetch_uod_info(engine_id: str) -> Dto.UodDefinition | None:
    t1 = time.perf_counter()
    try:
        response = httpx.get(f"http://localhost:9800/uod/{engine_id}")
        if response.status_code == 200:
            result = response.json()
            uod_def = Dto.UodDefinition(**result)
            dt = time.perf_counter() - t1
            logger.debug(f"Fetched uod_info, duration: {dt:0.2f}s")
            return uod_def
    except Exception:
        logger.error("Exception fetching UodDefinition", exc_info=True)

    logger.error("uod info is not available")
    return Dto.UodDefinition(
        commands=[],
        system_commands=[],
        tags=[Dto.TagDefinition(name="Foo")]
    )


def build_tags(uod_def: Dto.UodDefinition) -> TagValueCollection:
    return TagValueCollection([TagValue(name=t.name, unit=t.unit) for t in uod_def.tags])


def build_commands(uod_def: Dto.UodDefinition) -> CommandCollection:
    cmds = []
    for c_def in uod_def.commands + uod_def.system_commands:
        try:
            parser = RegexNamedArgumentParser.deserialize(c_def.validator) if c_def.validator is not None else None

            # build a validate function using the command's own validate function
            def outer(key: str, parser: RegexNamedArgumentParser | None):
                def validate(args: str) -> bool:
                    #logger.debug(f"Validating args '{args}' for command key '{key}' and builder name {c_def.name}")
                    if parser is None:
                        return True
                    else:
                        return parser.validate(args)
                return validate

            cmd = Command(c_def.name, validatorFn=outer(c_def.name, parser))
            cmds.append(cmd)
        except Exception:
            logger.error(f"Failed to build command '{c_def.name}'", exc_info=True)

    return CommandCollection(cmds)


class AnalysisInput:
    def __init__(self, pcode: str, commands: CommandCollection, tags: TagValueCollection, engine_id: str):
        self.pcode: str = pcode
        self.commands: CommandCollection = commands
        self.tags: TagValueCollection = tags
        self.engine_id: str = engine_id

        self.command_completions = [c.name for c in self.commands.to_list()] + \
            ["Watch", "Alarm",
             "Block", "End block", "End blocks",
             "Increment run counter",
             "Mark",
             "Macro", "Call macro",
             "Batch"]
        self.tag_completions = [t.name for t in self.tags]

    def get_first_word_completions(self, query: str) -> list[str]:
        return [c for c in self.command_completions if c.lower().startswith(query.lower())] + []

    def get_tag_completions(self, query: str) -> list[str]:
        return [tag for tag in self.tag_completions if tag.lower().startswith(query.lower())]


def create_analysis_input(document: Document, engine_id: str) -> AnalysisInput: 
    uod_def = fetch_uod_info(engine_id)
    if uod_def is None:
        logger.error(f"Failed to load uod definition (was none) for engine: {engine_id}")
        raise RuntimeError("Failed to fetch uod_info")
    return AnalysisInput(
        pcode=document.source,
        commands=build_commands(uod_def),
        tags=build_tags(uod_def),
        engine_id=engine_id
    )


class AnalysisResult:
    def __init__(self, program: PProgram, items: list[AnalyzerItem], input: AnalysisInput):
        self.program = program
        self.items = items
        self.input = input


def analyze(input: AnalysisInput) -> AnalysisResult:
    """ Parse document as pcode and run semantic analysis on it """
    try:
        program = build_program(input.pcode)
    except Exception as ex:
        logger.error("Failed to build program: '{pcode}'", exc_info=True)
        raise ex
    analyzer = SemanticCheckAnalyzer(input.tags, input.commands)
    analyzer.analyze(program)
    return AnalysisResult(program, analyzer.items, input)


def lint(document: Document, engine_id: str) -> list[Diagnostics]:    
    diagnostics: list[Diagnostics] = []

    try:
        analysis_input = create_analysis_input(document, engine_id)
        analysis_result = analyze(analysis_input)
    except Exception as ex:
        logger.error("Failed to build program: '{pcode}'", exc_info=True)
        diagnostics.append(
            Diagnostics(
                source="Open Pectus",
                range=Range(
                    start=Position(line=0, character=1),
                    end=Position(line=0, character=100)
                ),
                code="Demo Code??",
                message="Parse error: " + str(ex),
                severity=DiagnosticSeverity.Error
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
                severity=get_item_severity(item)
            )
        )
    return diagnostics

def create_node_symbol(node: PNode) -> DocumentSymbol | None:
    if isinstance(node, (PComment, PBlank)):
        return None
    node_range = get_node_range(node)
    if node_range is None:
        logger.warning(f"Node {node} has no range")
        return None

    child_symbols = []
    for child_node in node.get_child_nodes(recursive=False):
        child_symbol = create_node_symbol(child_node)
        if child_symbol is not None:
            child_symbols.append(child_symbol)

    symbol = DocumentSymbol(
        name=node.instruction_name or f"(missing instruction name, node type {type(node).__name__})",
#        detail=None,
        kind=SymbolKind.Function,
        range=node_range,
        selectionRange=node_range,
        children=child_symbols
    )
    return symbol


def symbols_slow(document: Document, engine_id: str) -> list[DocumentSymbol]:
    result = []

    try:
        analysis_input = create_analysis_input(document, engine_id)
        analysis_result = analyze(analysis_input)
        assert analysis_result is not None
    except Exception:
        logger.error("Failed to build program: '{pcode}'", exc_info=True)
        return []

    # iterate the root and add nodes as direct decendant symbols
    for node in analysis_result.program.get_child_nodes(recursive=False):
        symbol = create_node_symbol(node)
        if symbol is not None:
            result.append(symbol)

    return result


def symbols(document: Document, engine_id: str) -> list[DocumentSymbol]:
    """ Return a fixed set of symbols for testing. """
    mark = DocumentSymbol(
        name="Mark",
        kind=SymbolKind.Field,
        range=Range(
            start=Position(line=0, character=0), end=Position(line=0, character=4)
        ),
        selectionRange=Range(
            start=Position(line=0, character=0), end=Position(line=0, character=4)
        ),
        children=[]
    )
    stop = DocumentSymbol(
        name="Stop",
        kind=SymbolKind.Method,
        range=Range(
            start=Position(line=1, character=0), end=Position(line=1, character=4)
        ),
        selectionRange=Range(
            start=Position(line=1, character=0), end=Position(line=1, character=4)
        ),
        children=[]
    )

    info = DocumentSymbol(
        name="Info",
        kind=SymbolKind.Method,
        range=Range(
            start=Position(line=2, character=0), end=Position(line=2, character=4)
        ),
        selectionRange=Range(
            start=Position(line=2, character=0), end=Position(line=2, character=4)
        ),
        children=[]
    )

    return [mark, stop, info]


def starts_with_any(query: str, candidates: list[str]) -> bool:
    """ Return True if query starts with any of the candidates """
    for candidate in candidates:
        if query.startswith(candidate):
            return True
    return False


def completions(document: Document, position: Position, ignored_names, engine_id: str) -> list[CompletionItem]:
    # Note: Returning a CompletionList with items does not work in the client for some reason. Only
    # The array/list of CompletionItem is working in the client.
    # Also consider the hook pylsp_completion_item_resolve. The spec has info about how this can be used to add 
    # more detail to the suggestions.
    try:
        analysis_input = create_analysis_input(document, engine_id)
    except Exception:
        logger.error("Failed to build program: '{pcode}'", exc_info=True)
        return []

    # determine whether position is in first word on the line
    line = get_line(document, position)
    if line is None:
        return []

    # get whole query, eg "St" or "Alarm: Run T"
    char: int = position["character"]
    if char < len(line):
        query = line[0:char]
    else:
        query = line

    # remove indentation from query
    query = query.lstrip().removesuffix("\n")

    is_first_word = True if " " not in query else False
    if is_first_word:
        # the simplest and most important case - completions for the first word on a line
        return [
            CompletionItem(label=word, kind=CompletionItemKind.Function, preselect=False)
            for word in analysis_input.get_first_word_completions(query)
        ]
    else:
        if starts_with_any(query, ["Watch:", "Watch: ", "Alarm:", "Alarm: "]):
            # suggest tags
            second_word = query[6:].strip()
            return [
                CompletionItem(label=name, kind=CompletionItemKind.Enum, preselect=False)
                for name in analysis_input.get_tag_completions(second_word)
            ]
        else:
            # difficult amd possibly not important case
            # we could autocomplete all parts of a condition
            return []


def get_line(document: Document, position: Position) -> str | None:
    for i, line in enumerate(document.lines):
        if position["line"] == i:
            return line


def find_first_word_position(document: Document, word: str) -> Position | None:
    for i, line in enumerate(document.lines):
        if word in line:
            character = line.index(word)
            return {"line": i, "character": character}

def find_word_at_position(document: Document, position: Position) -> str | None:
    for i, line in enumerate(document.lines):
        if position["line"] == i:
            if " " in line:
                word = line.index(" ")
            else:
                word = line if position["character"] < len(line) else None
                return word
