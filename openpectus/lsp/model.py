from __future__ import annotations
from typing import TypedDict

from pylsp.lsp import DiagnosticSeverity, SymbolKind

from openpectus.lang.exec.analyzer import AnalyzerItem, AnalyzerItemType
from openpectus.lang.model.pprogram import PNode


class Position(TypedDict):
    """ Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#position """
    line: int
    """ Zero-based line counter"""
    character: int
    """ Zero based character counter """


class Range(TypedDict):
    """ Representation of https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#range

    Note:
    - Lines are zero-based (where PNode lines are 1-based)
    - Characters are also zero-based (like PNode increment and column) but the end position is not included. To include a
      complete line, use character 0 on the next line as end position.
    """
    start: Position
    end: Position


class Diagnostics(TypedDict):
    """ Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#diagnostic """
    source: str
    range: Range
    code: str
    message: str
    severity: int
    """ One of DiagnosticSeverity """


class DocumentSymbol(TypedDict):
    """ Representation of https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#documentSymbol """
    name: str
    #detail: str | None
    kind: int
    """ One of SymbolKind """
    # tags: list[object] | None
    # deprecated: bool | None
    range: Range
    selectionRange: Range
    children: list[DocumentSymbol]  # the spec defines this as optional but the client errors out if set to None


class Location(TypedDict):
    """ Repreesntation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#location """
    uri: str
    range: Range


class SymbolInformation(TypedDict):
    """ Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#symbolInformation """
    name: str
    kind: int
    location: Location


class CompletionItemKind:
    Text = 1
    Method = 2
    Function = 3
    Constructor = 4
    Field = 5
    Variable = 6
    Class = 7
    Interface = 8
    Module = 9
    Property = 10
    Unit = 11
    Value = 12
    Enum = 13
    Keyword = 14
    Snippet = 15
    Color = 16
    File = 17
    Reference = 18
    Folder = 19
    EnumMember = 20
    Constant = 21
    Struct = 22
    Event = 23
    Operator = 24
    TypeParameter = 25


class CompletionItem(TypedDict):
    """ Representation of 
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#completionItem
    Has LOTS of options
    """
    label: str
    kind: int | None
    preselect: bool | None

class CompletionList(TypedDict):
    """ Representation of 
    https://microsoft.github.io/language-server-protocol/specifications/specification-3-16/#completionList """
    isIncomplete: bool
    items: list[CompletionItem]

def get_item_severity(item: AnalyzerItem) -> int:
    """ Represent analyser item type as lsp DiagnosticSeverity """
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
            line=item.range_start.line - 1,
            character=item.range_start.character
        ),
        end=Position(
            line=item.range_end.line - 1,
            character=item.range_end.character
        ),
    )

def get_node_range(node: PNode) -> Range | None:
    """ Represent item position range as lsp RangeItem """
    if node.line is None or node.indent is None:
        return None

    return Range(
        start=Position(
            line=node.line - 1,
            character=node.indent
        ),
        end=Position( # for now we just pick the rest of the line
            line=node.line,
            character=0
        ),
    )
