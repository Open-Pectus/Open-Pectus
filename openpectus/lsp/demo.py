import logging
from typing import TypedDict
import httpx

from pylsp.workspace import Document
from pylsp.lsp import DiagnosticSeverity

from openpectus.engine.hardware import NullHardware
from openpectus.engine.main import create_uod
from openpectus.lang.exec.uod import UnitOperationDefinitionBase, UodCommandBuilder
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
    response = httpx.get(f"http://localhost:9800/uod/{engine_id}")
    if response.status_code == 200:
        result = response.json()
        return Dto.UodDefinition(**result)
    else:
        return None

def create_local_uod(engine_id: str) -> UnitOperationDefinitionBase | None:
    uod_info = fetch_uod_info(engine_id)
    if uod_info is None:
        logger.warning(f"Uod information for engine '{engine_id}' is not available. Engine may be down")
        return None
    logger.debug(f"Uod info: {str(uod_info)}")
    uod = create_uod(uod_info.filename)
    uod.system_tags = system_tags
    uod.hwl = NullHardware()
    uod.validate_configuration()
    uod.build_commands()
    return uod


class CommandsValidator():
    def __init__(self, builder: UodCommandBuilder) -> None:
        pass

#def lint_example(document: Document, engine_id: str) -> list[DiagnosticsItem]:
def lint_example(document: Document) -> list[DiagnosticsItem]:
    # parse document context as pcode and run semantic analysis on it
    diagnostics: list[DiagnosticsItem] = []

    engine_id = "MIAWLT-1645-MPO_DemoUod"


    # add system tags
    tags = []
    for t in system_tags:
        tags.append(TagValue(name=t.name, unit=t.unit))

    # TODO we also need to access system commands

    cmds = []

    uod = create_local_uod(engine_id)
    if uod is not None:
        for key, builder in uod.command_factories.items():
            logger.debug(f"Processing uod command '{key}'")

            # build a validate function using the command's own arg_parse function
            def outer(key, builder: UodCommandBuilder):
                def validate(args: str) -> bool:
                    logger.debug(f"Valudating args '{args}' for command key '{key}' and builder name {builder.name}")
                    if builder.arg_parse_fn is None:
                        # if no argument parser is defined, require that no argument was given
                        if args == "":
                            return True
                        return False
                    try:
                        result = builder.arg_parse_fn(args)
                        return result is not None
                    except Exception:
                        logger.warning("Exception during arg_parse_fn", exc_info=True)
                        return False
                return validate

            cmd = Command(name=key, validatorFn=outer(key, builder))
            cmds.append(cmd)

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
