import logging
from typing import TypedDict
import httpx

from pylsp.workspace import Document
from pylsp.lsp import DiagnosticSeverity

from openpectus.lang.exec.analyzer import AnalyzerItem, AnalyzerItemType, SemanticCheckAnalyzer
from openpectus.lang.exec.commands import Command, CommandCollection
from openpectus.lang.exec.tags import TagValue, TagValueCollection, create_system_tags
from openpectus.lang.exec.tags_impl import MarkTag
from openpectus.test.engine.utility_methods import build_program
import openpectus.aggregator.routers.dto as Dto


logger = logging.getLogger(__name__)
system_tags = create_system_tags()  # will not include the Mark tag ...
system_tags.add(MarkTag())

class PositionItem(TypedDict):
    line: int
    character: int

class RangeItem(TypedDict):
    start: PositionItem
    end: PositionItem

class DiagnosticsItem(TypedDict):
    source: str
    range: RangeItem
    code: str
    message: str
    severity: int
    """ One of DiagnosticSeverity """


def get_item_severity(item: AnalyzerItem) -> int:
    if item.type == AnalyzerItemType.HINT:
        return DiagnosticSeverity.Hint
    elif item.type == AnalyzerItemType.INFO:
        return DiagnosticSeverity.Information
    elif item.type == AnalyzerItemType.WARNING:
        return DiagnosticSeverity.Warning
    elif item.type == AnalyzerItemType.ERROR:
        return DiagnosticSeverity.Error
    return DiagnosticSeverity.Error

def get_item_range(item: AnalyzerItem) -> RangeItem:
    # pslsp document is zero based, analyzer is 1-based
    return RangeItem(
        start=PositionItem(
            line=item.range_start.line - 1,
            character=item.range_start.character
        ),
        end=PositionItem(
            line=item.range_end.line - 1,
            character=item.range_end.character
        ),
    )

def fetch_tags_info(engine_id: str) -> list[Dto.TagDefinition]:
    # http://localhost:9800/tags/MIAWLT-1645-MPO_DemoUod
    response = httpx.get(f"http://localhost:9800/tags/{engine_id}")
    result = response.json()
    values: list[Dto.TagDefinition] = []
    for t in result:
        p = Dto.TagDefinition(**t)
        values.append(p)
    return values

def fetch_commands_info(engine_id: str) -> list[Dto.CommandDefinition]:
    response = httpx.get(f"http://localhost:9800/commands/{engine_id}")
    result = response.json()
    values: list[Dto.CommandDefinition] = []
    for t in result:
        p = Dto.CommandDefinition(**t)
        values.append(p)
    return values

def fetch_uod_info(engine_id: str) -> list[Dto.CommandDefinition]:
    response = httpx.get(f"http://localhost:9800/uod/{engine_id}")
    result = response.json()
    info = Dto.UodDefinition(**result)
    
    

#def lint_example(document: Document, engine_id: str) -> list[DiagnosticsItem]:
def lint_example(document: Document) -> list[DiagnosticsItem]:
    # parse document context as pcode and run semantic analysis on it
    diagnostics: list[DiagnosticsItem] = []

    engine_id = "MIAWLT-1645-MPO_DemoUod"

    values = fetch_tags_info(engine_id)
    tags = [
        TagValue(t.name, unit=t.unit)
        for t in values
    ]

    # add system tags
    for t in system_tags:
        tags.append(TagValue(name=t.name, unit=t.unit))

    # maybe just access aggregator directly - should be doable

    # TODO we also need to access system commands
    cmd_values = fetch_commands_info(engine_id)
    cmds = [Command(name=c.name) for c in cmd_values]

    analyzer = SemanticCheckAnalyzer(TagValueCollection(tags), CommandCollection(cmds))
    pcode = document.source
    try:
        program = build_program(pcode)
    except Exception as ex:
        logger.error("Failed to build program: '{pcode}'", exc_info=True)
        diagnostics.append(
            DiagnosticsItem(
                source="Open Pectus",
                range=RangeItem(
                    start=PositionItem(line=0, character=1),
                    end=PositionItem(line=0, character=100)
                ),
                code="Demo Code??",
                message="Parse error: " + str(ex),
                severity=DiagnosticSeverity.Error
            )
        )
        return diagnostics

    analyzer.analyze(program)
    for item in analyzer.items:
        diagnostics.append(
            DiagnosticsItem(
                source="Open Pectus",
                range=get_item_range(item),
                code=item.message,
                message=item.description,
                severity=get_item_severity(item)
            )
        )
    return diagnostics


def lint_example_typed(document: Document) -> list[DiagnosticsItem]:
    """ This TypedDict based typed example works, i.e. the client accepts and renders it. """
    diagnostics: list[DiagnosticsItem] = []
    diagnostics.append(
        DiagnosticsItem(
            source="Open Pectus",
            range=RangeItem(
                start=PositionItem(line=0, character=1),
                end=PositionItem(line=0, character=100)
            ),
            code="Demo Code",
            message="Demo message",
            severity=DiagnosticSeverity.Information
        )
    )
    return diagnostics

def lint_example_untyped(document: Document) -> list[DiagnosticsItem]:
    """ This untyped example works, i.e. the client accepts and renders it. """
    diagnostics = []
    diagnostics.append(
        {
            "source": "Open Pectus",
            "range": {
                "start": {"line": 0, "character": 0},
                # Client is supposed to clip end column to line length.
                "end": {"line": 0, "character": 1000},
            },
            "code": "Foo bar",
            "message": "my error",
            "severity": 1,  # Error: 1, Warning: 2, Information: 3, Hint: 4, typed: lsp.DiagnosticSeverity.*
        }
    )
    pos = find_first_word_position(document, "secret")
    if pos is not None:
        diagnostics.append(
            {
                "source": "Open Pectus",
                "range": {
                    "start": pos,
                    # Client is supposed to clip end column to line length.
                    "end": {"line": pos["line"], \
                            "character": int(pos["character"]) + len("secret")},
                },
                "code": "Secret error",
                "message": "Do not type the secret word",
                "severity": 2,  # Error: 1, Warning: 2, Information: 3, Hint: 4
            }
        )
    return diagnostics


def find_first_word_position(document: Document, word: str):

    for i, line in enumerate(document.lines):
        if word in line:
            character = line.index(word)
            return {"line": i, "character": character}
    return None
