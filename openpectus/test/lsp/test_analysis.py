
import unittest

from pylsp.workspace import Document, Workspace

from openpectus.aggregator.routers.dto import CommandDefinition, TagDefinition, UodDefinition
from openpectus.lsp import lsp_analysis
from openpectus.lsp.model import CompletionItem, Position


def create_workspace() -> Workspace:
    return Workspace(root_uri="root_uri", endpoint=None, config=None)

def create_document(pcode: str) -> Document:
    workspace = create_workspace()
    return Document(uri="doc_uri", workspace=workspace, source=pcode)

def create_position(pcode: str) -> Position:
    lines = pcode.splitlines()
    if len(lines) == 0:
        return Position(line=0, character=0)
    elif len(lines) == 1:
        return Position(line=0, character=len(lines[0]))
    else:        
        last_line_index = len(lines) - 1
        last_line = lines[last_line_index]
        return Position(line=last_line_index, character=len(last_line))


class TestLspAnalysis(unittest.TestCase):

    def get_completions(self, pcode: str, uod_info: UodDefinition | None = None) -> list[CompletionItem]:
        position = create_position(pcode)
        document = create_document(pcode)

        if uod_info is None:
            uod_info = UodDefinition(
                commands=[],
                system_commands=[],
                tags=[])

        setattr(lsp_analysis, "fetch_uod_info", lambda _: uod_info)
        result = lsp_analysis.completions(document, position, ignored_names=None, engine_id="eng_id")
        return result

    def get_completion_labels(self, pcode: str, uod_info: UodDefinition | None = None) -> list[str]:
        result = self.get_completions(pcode, uod_info)
        return [r["label"] for r in result]

    def test_completions_commands(self):
        pcode = "in"  # typing 'Increment run counter'
        result = self.get_completion_labels(pcode)
        self.assertEqual(1, len(result))
        self.assertEqual("Increment run counter", result[0])

    def test_completions_tags(self):
        pcode = "Watch: "  # typing 'Watch: Foo' or 'Watch: bar'
        uod_info = UodDefinition(
            commands=[],
            system_commands=[],
            tags=[TagDefinition(name=tag) for tag in ["Foo", "Bar"]]
        )
        result = self.get_completion_labels(pcode, uod_info)
        self.assertEqual(2, len(result))
        self.assertEqual(["Foo", "Bar"], result)

    def test_completions_watch_tag(self):
        pcode = "Watch: ru"

        uod_info = UodDefinition(
            commands=[],
            system_commands=[],
            tags=[TagDefinition(name=tag) for tag in ["Run Time", "Run Counter"]]
        )

        result = self.get_completion_labels(pcode, uod_info)
        self.assertEqual(2, len(result))
        self.assertEqual(["Run Time", "Run Counter"], result)

    def test_completions_watch_body(self):
        pcode = """
Watch: Run Time > 5s
    Mar
"""
        pos = create_position(pcode)
        self.assertEqual(2, pos["line"])
        self.assertEqual(7, pos["character"])

        result = self.get_completion_labels(pcode)
        self.assertEqual(1, len(result))
        self.assertEqual("Mark", result[0])
