from __future__ import annotations
from typing import TypedDict

from pylsp.lsp import DiagnosticSeverity, SymbolKind

from openpectus.lang.exec.analyzer import AnalyzerItem, AnalyzerItemType


class PositionItem(TypedDict):
    """ Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#position """
    line: int
    """ Zero-based line counter"""
    character: int
    """ Zero based character counter """


class RangeItem(TypedDict):
    """ Representation of https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#range

    Note:
    - Lines are zero-based (where PNode lines are 1-based)
    - Characters are also zero-based (like PNode increment and column) but the end position is not included. To include a
      complete line, use character 0 on the next line as end position.
    """
    start: PositionItem
    end: PositionItem


class DiagnosticsItem(TypedDict):
    """ Representation of
    https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#diagnostic """
    source: str
    range: RangeItem
    code: str
    message: str
    severity: int
    """ One of DiagnosticSeverity """


class DocumentSymbolItem(TypedDict):
    """ Representation of https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#documentSymbol """
    name: str
    detail: str | None
    kind: int
    """ One of SymbolKind """
    #tags: list[SymbolTag] | None;
    range: RangeItem
    selectionRange: RangeItem
    children: list[DocumentSymbolItem] | None

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


def get_item_range(item: AnalyzerItem) -> RangeItem:
    """ Represent item position range as lsp RangeItem """
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
