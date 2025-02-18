import logging
from typing import TypedDict
import httpx

from pylsp.workspace import Document
from pylsp.lsp import DiagnosticSeverity

from openpectus.lang.exec.uod import RegexNamedArgumentParser
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


def fetch_uod_info(engine_id: str) -> Dto.UodDefinition | None:
    try:
        response = httpx.get(f"http://localhost:9800/uod/{engine_id}")
        if response.status_code == 200:
            result = response.json()
            return Dto.UodDefinition(**result)
    except Exception:
        logger.error("Exception fetching UodDefinition", exc_info=True)

    logger.error("uod info is not available")
    return Dto.UodDefinition(
        commands=[],
        system_commands=[],
        tags=[Dto.TagDefinition(name="Foo")]
    )


def build_tags(uod_def: Dto.UodDefinition) -> TagValueCollection:
    tags = []
    for t in system_tags:
        tags.append(TagValue(name=t.name, unit=t.unit))
    for t in uod_def.tags:
        tags.append(TagValue(name=t.name, unit=t.unit))
    return TagValueCollection(tags)


def build_commands(uod_def: Dto.UodDefinition) -> CommandCollection:
    cmds = []
    for c_def in uod_def.commands + uod_def.system_commands:
        parser = RegexNamedArgumentParser.deserialize(c_def.validator) if c_def.validator is not None else None

        # build a validate function using the command's own validate function
        def outer(key: str, parser: RegexNamedArgumentParser | None):
            def validate(args: str) -> bool:
                logger.debug(f"Validating args '{args}' for command key '{key}' and builder name {c_def.name}")
                if parser is None:
                    return True
                else:
                    return parser.validate(args)
            return validate

        cmd = Command(c_def.name, validatorFn=outer(c_def.name, parser))
        cmds.append(cmd)

    return CommandCollection(cmds)


def lint(document: Document, engine_id: str) -> list[DiagnosticsItem]:
    # parse document context as pcode and run semantic analysis on it
    diagnostics: list[DiagnosticsItem] = []

    uod_def = fetch_uod_info(engine_id)
    if uod_def is None:
        return []

    logger.debug(f"{uod_def.commands=}")
    logger.debug(f"{uod_def.system_commands=}")
    logger.debug(f"{uod_def.tags=}")

    cmds = build_commands(uod_def)
    tags = build_tags(uod_def)

    analyzer = SemanticCheckAnalyzer(tags, cmds)
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

    # run analyzer
    analyzer.analyze(program)

    # map analyzer result to lsp diagnostics
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


def find_first_word_position(document: Document, word: str):

    for i, line in enumerate(document.lines):
        if word in line:
            character = line.index(word)
            return {"line": i, "character": character}
    return None
