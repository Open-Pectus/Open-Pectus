from __future__ import annotations
from typing import TypedDict, Literal, NotRequired

from pylsp.lsp import DiagnosticSeverity

from openpectus.lang.exec.analyzer import AnalyzerItem, AnalyzerItemType


class MarkupContent(TypedDict):
    """
    Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#markupContentInnerDefinition
    """
    kind: Literal["markdown", "plaintext"]
    value: str

class Hover(TypedDict):
    """
    Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#hover
    """
    contents: MarkupContent
    range: NotRequired[Range]

class Position(TypedDict):
    """
    Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#position
    """
    line: int
    """ Zero-based line counter"""
    character: int
    """ Zero based character counter """


class Range(TypedDict):
    """
    Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#range

    Note:
    - Lines are zero-based
    - Characters are zero-based
    """
    start: Position
    end: Position


class Diagnostic(TypedDict):
    """
    Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#diagnostic
    """
    range: Range
    severity: NotRequired[int]
    code: NotRequired[str]
    source: NotRequired[str]
    message: str
    data: NotRequired[dict[str, str]]  # Actual type is not this strict
    """ One of DiagnosticSeverity """


class TextEdit(TypedDict):
    """
    Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textEdit
    """
    range: Range
    newText: str

class WorkspaceEdit(TypedDict):
    """
    Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#workspaceEdit
    """
    changes: dict[str, list[TextEdit]]


class CodeAction(TypedDict):
    """
    Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#codeAction
    """
    title: str
    kind: NotRequired[Literal[
        "",
        "quickfix",
        "refactor",
        "refactor.extract",
        "refactor.inline",
        "refactor.rewrite",
        "source",
        "source.fixAll"
        ]]
    diagnostics: NotRequired[list[Diagnostic]]
    edit: NotRequired[WorkspaceEdit]


class CodeActionContext(TypedDict):
    """
    Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#codeActionContext
    """
    diagnostics: list[Diagnostic]


class DocumentSymbol(TypedDict):
    """
    Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#documentSymbol
    """
    name: str
    kind: int  # SymbolKind
    range: Range
    selectionRange: Range
    children: list[DocumentSymbol]  # the spec defines this as optional but the client errors out if set to None


class Location(TypedDict):
    """
    Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#location
    """
    uri: str
    range: Range


class SymbolInformation(TypedDict):
    """
    Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#symbolInformation
    """
    name: str
    kind: int  # SymbolKind
    location: Location


class Command(TypedDict):
    """
    Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#command
    """
    title: str
    command: str


class CompletionItem(TypedDict):
    """
    Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#completionItem
    """
    label: str
    kind: NotRequired[int]  # CompletionItemKind
    preselect: NotRequired[bool]
    insertText: NotRequired[str]
    textEdit: NotRequired[TextEdit]
    command: NotRequired[Command | None]

def get_item_severity(item: AnalyzerItem) -> int:
    """ Represent analyzer item type as lsp DiagnosticSeverity """
    if item.type == AnalyzerItemType.HINT:
        return DiagnosticSeverity.Hint
    elif item.type == AnalyzerItemType.INFO:
        return DiagnosticSeverity.Information
    elif item.type == AnalyzerItemType.WARNING:
        return DiagnosticSeverity.Warning
    elif item.type == AnalyzerItemType.ERROR:
        return DiagnosticSeverity.Error
    return DiagnosticSeverity.Error


def get_item_range(item: AnalyzerItem) -> Range:
    """ Represent item position range as lsp RangeItem """
    return Range(
        start=Position(
            line=item.range.start.line,
            character=item.range.start.character
        ),
        end=Position(
            line=item.range.end.line,
            character=item.range.end.character
        ),
    )
