
from typing import TypedDict
from pylsp.workspace import Document

from pylsp.lsp import DiagnosticSeverity

from openpectus.lang.exec.analyzer import AnalyzerItem, AnalyzerItemType, SemanticCheckAnalyzer
from openpectus.lang.exec.commands import Command, CommandCollection
from openpectus.lang.exec.tags import TagCollection
from openpectus.test.engine.utility_methods import build_program


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

#def lint_example(document: Document, engine_id: str) -> list[DiagnosticsItem]:
def lint_example(document: Document) -> list[DiagnosticsItem]:
    # parse document context as pcode and run semantic analysis on it
    diagnostics: list[DiagnosticsItem] = []

    # uod_name = engine_id.split("_")[1]
    # TODO to build TagCollection we should probably ask aggregator
    # TODO We should probably have another representation than TagCollection more like TagValue's
    tags = (
        TagCollection()
    )

    # TODO to build CommandCollection we need access to the uod commands somehow.
    # thats not trivial
    cmds = (
        CommandCollection()
        .with_cmd(Command("Stop"))
        .with_cmd(Command("Base"))
    )

    analyzer = SemanticCheckAnalyzer(tags, cmds)
    try:
        program = build_program(document.source)
    except Exception as ex:
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
