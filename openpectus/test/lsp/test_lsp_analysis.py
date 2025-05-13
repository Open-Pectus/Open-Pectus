
import unittest

from pylsp.workspace import Document, Workspace

from openpectus.protocol.models import CommandDefinition, TagDefinition, UodDefinition, TagValue
from openpectus.lsp import lsp_analysis
from openpectus.lsp.model import CompletionItem, Position, Diagnostic
from openpectus.lang.exec import regex


def create_workspace() -> Workspace:
    return Workspace(root_uri="", endpoint=None, config=None)

def create_document(pcode: str) -> Document:
    workspace = create_workspace()
    return Document(uri="file://workspace/uri", workspace=workspace, source=pcode)

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


class TestLspAnalysisCompletion(unittest.TestCase):

    def get_completions(self, pcode: str, uod_info: UodDefinition | None = None) -> list[CompletionItem]:
        lsp_analysis.create_analysis_input.cache_clear()
        position = create_position(pcode)
        document = create_document(pcode)

        if uod_info is None:
            uod_info = UodDefinition(
                commands=[],
                system_commands=[
                    CommandDefinition(name="Mark", validator=None, docstring=""),
                    CommandDefinition(name="Watch", validator=None, docstring=""),
                    CommandDefinition(name="End block", validator=None, docstring=""),
                    CommandDefinition(name="End blocks", validator=None, docstring=""),
                ],
                tags=[])

        setattr(lsp_analysis, "fetch_uod_info", lambda _: uod_info)
        result = lsp_analysis.completions(document, position, ignored_names=None, engine_id="eng_id")
        return result

    def get_completion_labels(self, pcode: str, uod_info: UodDefinition | None = None) -> list[str]:
        result = self.get_completions(pcode, uod_info)
        return [r["label"] for r in result]

    def test_completions_blank(self):
        pcode = ""
        uod_info = UodDefinition(
            commands=[
                CommandDefinition(name="Command1",  validator=None, docstring=""),
                CommandDefinition(name="Command2",  validator=None, docstring=""),
                CommandDefinition(name="Command3",  validator=None, docstring=""),
            ],
            system_commands=[],
            tags=[]
        )
        result = self.get_completion_labels(pcode, uod_info)
        self.assertEqual(len(uod_info.commands), len(result))
        self.assertEqual(result, [command.name for command in uod_info.commands])

    def test_completions_commands(self):
        pcode = "en"  # typing 'End block' or 'End blocks'
        result = self.get_completion_labels(pcode)
        self.assertEqual(2, len(result))
        self.assertTrue(result[0].startswith("End blo"))

    def test_completions_categorical_additive(self):
        pcode = "Category: "
        uod_info = UodDefinition(
            commands=[CommandDefinition(
                name="Category",
                validator="RNAP-v1-"+regex.RegexCategorical(additive_options=["A", "B", "C"]),
                docstring="")
            ],
            system_commands=[],
            tags=[]
        )
        result = self.get_completion_labels(pcode, uod_info)
        self.assertEqual(3, len(result))
        self.assertTrue(result, ["A", "B", "C"])

    def test_completions_categorical_exclusive(self):
        pcode = "Category: "
        uod_info = UodDefinition(
            commands=[CommandDefinition(
                name="Category",
                validator="RNAP-v1-"+regex.RegexCategorical(additive_options=["A", "B"], exclusive_options=["C"]),
                docstring="")
            ],
            system_commands=[],
            tags=[]
        )
        result = self.get_completion_labels(pcode, uod_info)
        self.assertEqual(3, len(result))
        self.assertTrue(result, ["A", "B", "C"])

    def test_completions_categorical_add_option(self):
        pcode = "Category: A+"
        uod_info = UodDefinition(
            commands=[CommandDefinition(
                name="Category",
                validator="RNAP-v1-"+regex.RegexCategorical(additive_options=["A", "B"], exclusive_options=["C"]),
                docstring="")
            ],
            system_commands=[],
            tags=[]
        )
        result = self.get_completion_labels(pcode, uod_info)
        # Expect two elements. Filtering to remove "A" is on client side.
        self.assertEqual(2, len(result))
        self.assertTrue(result, ["A", "B"])

    def test_completions_categorical_add_option_exclusive(self):
        pcode = "Category: C"
        uod_info = UodDefinition(
            commands=[CommandDefinition(
                name="Category",
                validator="RNAP-v1-"+regex.RegexCategorical(additive_options=["A", "B"], exclusive_options=["C"]),
                docstring="")
            ],
            system_commands=[],
            tags=[]
        )
        result = self.get_completion_labels(pcode, uod_info)
        self.assertEqual(0, len(result))

    def test_completions_tags(self):
        pcode = "Watch: "  # typing 'Watch: Foo' or 'Watch: bar'
        uod_info = UodDefinition(
            commands=[],
            system_commands=[CommandDefinition(name="Watch", validator=None, docstring="")],
            tags=[TagDefinition(name=tag) for tag in ["Foo", "Bar"]]
        )
        result = self.get_completion_labels(pcode, uod_info)
        self.assertEqual(2, len(result))
        self.assertEqual(["Foo", "Bar"], result)

    def test_completions_watch_tag(self):
        pcode = "Watch: ru"

        uod_info = UodDefinition(
            commands=[],
            system_commands=[CommandDefinition(name="Watch", validator=None, docstring="")],
            tags=[TagDefinition(name=tag) for tag in ["Run Time", "Run Counter"]]
        )

        result = self.get_completion_labels(pcode, uod_info)
        self.assertEqual(2, len(result))
        self.assertEqual(["Run Time", "Run Counter"], result)

    def test_completions_watch_operator(self):
        pcode = "Watch: Run Time "

        uod_info = UodDefinition(
            commands=[],
            system_commands=[CommandDefinition(name="Watch", validator=None, docstring="")],
            tags=[TagDefinition(name=tag) for tag in ["Run Time",]]
        )

        result = self.get_completion_labels(pcode, uod_info)
        self.assertEqual(7, len(result))
        self.assertEqual([
            "< (less than)",
            "<= (less than or equal)",
            "> (greater than)",
            ">= (greater than or equal)",
            "== (equal)",
            "= (equal)",
            "!= (not equal)"], result)

    def test_completions_watch_rhs(self):
        pcode = "Watch: Run Time == "

        uod_info = UodDefinition(
            commands=[],
            system_commands=[CommandDefinition(name="Watch", validator=None, docstring="")],
            tags=[TagDefinition(name=tag) for tag in ["Run Time",]]
        )

        result = self.get_completion_labels(pcode, uod_info)
        self.assertEqual(0, len(result))

    def test_completions_watch_unit(self):
        pcode = "Watch: Run Time == "

        uod_info = UodDefinition(
            commands=[],
            system_commands=[CommandDefinition(name="Watch", validator=None, docstring="")],
            tags=[TagDefinition(name="Run Time", unit="s")]
        )

        result = self.get_completion_labels(pcode, uod_info)
        self.assertEqual(4, len(result))
        self.assertEqual([
            "s",
            "min",
            "h",
            "ms",], result)

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

    def test_completions_watch_body_thr(self):
        pcode = """
Watch: Run Time > 5s
    5.7 Mar
"""
        pos = create_position(pcode)
        self.assertEqual(2, pos["line"])
        self.assertEqual(11, pos["character"])

        result = self.get_completion_labels(pcode)
        self.assertEqual(1, len(result))
        self.assertEqual("Mark", result[0])

    def test_complete_call_macro_no_macros(self):
        pcode = """
Call macro: """

        uod_info = UodDefinition(
            commands=[],
            system_commands=[
                CommandDefinition(name="Mark", validator=None, docstring=""),
                CommandDefinition(name="Macro", validator=None, docstring=""),
                CommandDefinition(name="Call macro", validator=None, docstring=""),
            ],
            tags=[TagDefinition(name="Run Time", unit="s")]
        )

        result = self.get_completion_labels(pcode, uod_info)
        self.assertEqual(0, len(result))

    def test_complete_call_macro(self):
        pcode = """
Macro: A
    Mark: a

Call macro: """

        uod_info = UodDefinition(
            commands=[],
            system_commands=[
                CommandDefinition(name="Mark", validator=None, docstring=""),
                CommandDefinition(name="Macro", validator=None, docstring=""),
                CommandDefinition(name="Call macro", validator=None, docstring=""),
            ],
            tags=[TagDefinition(name="Run Time", unit="s")]
        )

        result = self.get_completion_labels(pcode, uod_info)
        self.assertEqual(1, len(result))
        self.assertEqual(["A"], result)


class TestLspAnalysisLint(unittest.TestCase):
    def get_diagnostics(self, pcode: str, uod_info: UodDefinition | None = None) -> list[Diagnostic]:
        lsp_analysis.create_analysis_input.cache_clear()
        document = create_document(pcode)

        if uod_info is None:
            uod_info = UodDefinition(
                commands=[],
                system_commands=[
                    CommandDefinition(name="Mark", validator=None, docstring=""),
                    CommandDefinition(name="Watch", validator=None, docstring=""),
                    CommandDefinition(name="End block", validator=None, docstring=""),
                    CommandDefinition(name="End blocks", validator=None, docstring=""),
                ],
                tags=[])

        setattr(lsp_analysis, "fetch_uod_info", lambda _: uod_info)
        result = lsp_analysis.lint(document, engine_id="eng_id")
        return result

    def test_lint(self):
        uod_info = UodDefinition(
            commands=[CommandDefinition(
                name='Wait',
                validator='RNAP-v1-^\\s*(?P<number>[0-9]+[.][0-9]*?|[.][0-9]+|[0-9]+)\\s* ?(?P<number_unit>s|min|h)\\s*$',
                docstring=""),
            ],
            system_commands=[],
            tags=[TagDefinition(name=tag) for tag in ["Run Time", "Run Counter"]]
        )

        pcode = "Wait: 5"

        diags = self.get_diagnostics(pcode=pcode, uod_info=uod_info)
        self.assertEqual(1, len(diags))
        d = diags[0]

        self.assertEqual("Invalid command arguments", d.get("code", None))

        self.assertEqual(0, d["range"]["start"]["line"])
        self.assertEqual(6, d["range"]["start"]["character"])

        self.assertEqual(0, d["range"]["end"]["line"])
        self.assertEqual(7, d["range"]["end"]["character"])


class TestLspAnalysisHover(unittest.TestCase):
    pcode = """
Invalid command
Mark
Mark: Hej
Watch: Run Time
Watch: Run Time >
Watch: Run Time > 3 min
Macro: And
    Mark: a
Call macro: And
Call macro: Bnd
"""

    def get_hover(self, pcode: str, position: Position, uod_info: UodDefinition | None = None):
        lsp_analysis.create_analysis_input.cache_clear()
        document = create_document(pcode)

        if not uod_info:
            uod_info = UodDefinition(
                commands=[],
                system_commands=[
                    CommandDefinition(name="Mark", validator=None, docstring="MarkDoc"),
                    CommandDefinition(name="Watch", validator=None, docstring="WatchDoc"),
                    CommandDefinition(name="Macro", validator=None, docstring="MacroDoc"),
                    CommandDefinition(name="Call macro", validator=None, docstring="Call macroDoc"),
                ],
                tags=[TagDefinition(name="Run Time", unit="s")]
            )
            tag_value = TagValue(
                name="Run Time",
                tick_time=0,
                value=1.23,
                value_unit="s"
            )
            setattr(lsp_analysis, "fetch_process_value", lambda *args: tag_value)

        setattr(lsp_analysis, "fetch_uod_info", lambda _: uod_info)
        return lsp_analysis.hover(document, position, "eng_id")

    def test_hover_invalid_command(self):
        result = self.get_hover(self.pcode, Position(line=1, character=2))
        self.assertIsNone(result)

    def test_hover_command(self):
        result = self.get_hover(self.pcode, Position(line=2, character=2))
        assert result
        self.assertIn("MarkDoc", result["contents"]["value"])

    def test_hover_command_with_argument(self):
        result = self.get_hover(self.pcode, Position(line=3, character=2))
        assert result
        self.assertIn("MarkDoc", result["contents"]["value"])

    def test_hover_watch_with_tag(self):
        result = self.get_hover(self.pcode, Position(line=4, character=2))
        assert result
        self.assertIn("WatchDoc", result["contents"]["value"])

        result = self.get_hover(self.pcode, Position(line=4, character=8))
        assert result
        self.assertIn("Current value: 1,23 s", result["contents"]["value"])

    def test_hover_watch_with_tag_and_operator(self):
        result = self.get_hover(self.pcode, Position(line=5, character=2))
        assert result
        self.assertIn("WatchDoc", result["contents"]["value"])

        result = self.get_hover(self.pcode, Position(line=5, character=8))
        assert result
        self.assertEqual("Current value: 1,23 s", result["contents"]["value"])

        result = self.get_hover(self.pcode, Position(line=5, character=17))
        assert result
        self.assertEqual("greater than", result["contents"]["value"])

    def test_hover_macro(self):
        result = self.get_hover(self.pcode, Position(line=9, character=2))
        assert result
        self.assertIn("Call macroDoc", result["contents"]["value"])

        result = self.get_hover(self.pcode, Position(line=9, character=12))
        assert result
        self.assertIn('```pcode\r\nMacro: And\n    Mark: a\nCall macro: And\n```', result["contents"]["value"])

    def test_hover_unknown_macro(self):
        result = self.get_hover(self.pcode, Position(line=10, character=2))
        assert result
        self.assertIn("Call macroDoc", result["contents"]["value"])

        result = self.get_hover(self.pcode, Position(line=10, character=12))
        self.assertIsNone(result)


class TestLspAnalysis(unittest.TestCase):

    def test_build_commands(self):
        # test that the command validators are built using the correct closure
        # so that they in fact work

        # Note: hardcoding the serialized values is not great but the commands have different sources
        # and are serialized in different places so it's hard to avoid.
        system_commands = [
            CommandDefinition(name='Base', validator='RNAP-v1-^\\s*(L|h|min|s|mL|CV|DV|g|kg)\\s*$', docstring=""),
            CommandDefinition(
                name='Wait',
                validator='RNAP-v1-^\\s*(?P<number>[0-9]+[.][0-9]*?|[.][0-9]+|[0-9]+)\\s* ?(?P<number_unit>s|min|h)\\s*$',
                docstring=""),
            CommandDefinition(name='Warning', validator='RNAP-v1-', docstring="")
        ]

        uod_info = UodDefinition(
            commands=[],
            system_commands=system_commands,
            tags=[])

        cmds = lsp_analysis.build_commands(uod_info).to_list()

        cmd = next((c for c in cmds if c.name == "Wait"))  # number w unit
        assert cmd is not None

        self.assertEqual(True, cmd.validate_args("5s"))
        self.assertEqual(False, cmd.validate_args(""))

        cmd = next((c for c in cmds if c.name == "Warning"))  # no-check
        assert cmd is not None

        self.assertEqual(True, cmd.validate_args("5s"))
        self.assertEqual(True, cmd.validate_args(""))
        self.assertEqual(True, cmd.validate_args(" "))

        cmd = next((c for c in cmds if c.name == "Base"))  # one of the base unit values
        assert cmd is not None

        self.assertEqual(True, cmd.validate_args("s"))
        self.assertEqual(False, cmd.validate_args("foo"))
