import json
import logging
import time
from typing import Any

from pylsp import hookimpl
from pylsp.config.config import Config
from pylsp.workspace import Document, Workspace
from pylsp.python_lsp import PythonLSPServer

from openpectus.lsp import lsp_analysis
from openpectus.lsp.model import Position, CodeAction, Range, CodeActionContext


logger = logging.getLogger(__name__)
logger.info("Open Pectus LSP plugin loading")


class OPPythonLSPServer(PythonLSPServer):
    """ Subclass of PythonLSPServer which triggers autocomplete calculation on specific characters. """

    def capabilities(self):
        capabilities = super().capabilities()
        # Let the client know that the following providers are not available
        # This saves the client from making requests that we have to answer with []
        # as well as removing stale options from the GUI right click menu.
        capabilities["codeLensProvider"]["resolveProvider"] = False
        capabilities["completionProvider"]["resolveProvider"] = False
        capabilities["documentFormattingProvider"] = False
        capabilities["documentHighlightProvider"] = False
        capabilities["documentRangeFormattingProvider"] = False
        capabilities["documentSymbolProvider"] = False
        capabilities["definitionProvider"] = False
        capabilities["referencesProvider"] = False
        capabilities["renameProvider"] = False
        capabilities["foldingRangeProvider"] = False
        capabilities["signatureHelpProvider"] = {"triggerCharacters": []},
        capabilities["declarationProvider"] = False
        capabilities["typeDefinitionProvider"] = False
        capabilities["implementationProvider"] = False
        # capabilities["documentLinkProvider"] = dict()
        # capabilities["documentLinkProvider"]["resolveProvider"] = False
        capabilities["colorProvider"] = False
        capabilities["documentOnTypeFormattingProvider"] = False
        capabilities["executeCommandProvider"]["commands"] = []
        capabilities["selectionRangeProvider"] = False
        capabilities["linkedEditingRangeProvider"] = False
        capabilities["callHierarchyProvider"] = False
        capabilities["semanticTokensProvider"] = False
        capabilities["monikerProvider"] = False
        capabilities["typeHierarchyProvider"] = False
        capabilities["inlineValueProvider"] = False
        capabilities["inlayHintProvider"] = False
        capabilities["diagnosticProvider"] = False
        capabilities["workspaceSymbolProvider"] = False
        capabilities["experimental"] = []
        # Make sure that the following are enabled
        capabilities["codeActionProvider"] = True
        capabilities["hoverProvider"] = True
        # Trigger completion re-calculation on colon, space and plus characters
        capabilities["completionProvider"]["triggerCharacters"] = [":", " ", "+"]

        return capabilities


@hookimpl
def pylsp_settings(config: Config) -> dict[str, dict[str, dict[str, Any]]]:
    """Configuration options that can be set on the client."""
    return {
        "plugins": {
            "pylsp_openpectus": {"enabled": True},
            "flake8":  {"enabled": False},
            "pycodestyle":  {"enabled": False},
            "yapf": {"enabled": False},
            "autopep8": {"enabled": False},
            "pyflakes":  {"enabled": False},
            "mccabe":  {"enabled": False},
            "jedi_completion":  {"enabled": False},
            "jedi_definition":  {"enabled": False},
            "jedi_hover":  {"enabled": False},
            "jedi_highlight":  {"enabled": False},
            "jedi_references":  {"enabled": False},
            "jedi_rename":  {"enabled": False},
            "jedi_signature_help":  {"enabled": False},
            "jedi_symbols":  {"enabled": False},
            "preload":  {"enabled": False},
            "rope_autoimport":  {"enabled": False},
        }
    }

@hookimpl
def pylsp_document_did_open(config: Config, workspace: Workspace, document: Document):
    logger.info("pylsp_document_did_open")

@hookimpl
def pylsp_document_did_save(config, workspace, document):
    logger.info("pylsp_document_did_save")

@hookimpl
def pylsp_lint(config: Config, workspace: Workspace, document: Document, is_saved: bool):
    logger.debug("pylsp_lint")
    t1 = time.perf_counter()
    engine_id = get_engine_id(config)
    try:
        diagnostics = lsp_analysis.lint(document, engine_id)
        dt = time.perf_counter() - t1
        logger.debug(f"Lint ok, items: {len(diagnostics)}, duration: {dt:0.2f}s")
        return diagnostics
    except Exception:
        logger.error("Lint error", exc_info=True)
        return []

@hookimpl
def pylsp_completions(config: Config, workspace: Workspace, document: Document, position: Position, ignored_names):
    logger.debug("pylsp_completions")
    t1 = time.perf_counter()
    engine_id = get_engine_id(config)
    try:
        completions = lsp_analysis.completions(document, position, ignored_names, engine_id)
        dt = time.perf_counter() - t1
        logger.debug(f"Completions ok, items: {len(completions)}, duration: {dt:0.2f}s")
        return completions
    except Exception:
        logger.error("Completions error", exc_info=True)
        return []

@hookimpl
def pylsp_code_actions(
    config: Config,
    workspace: Workspace,
    document: Document,
    range: Range,
    context: CodeActionContext,
) -> list[CodeAction]:
    return lsp_analysis.code_actions(config, workspace, document, range, context)

@hookimpl
def pylsp_hover(config: Config, workspace: Workspace, document: Document, position: Position):
    return lsp_analysis.hover(document, position, get_engine_id(config))

def as_json(obj) -> str:
    if obj is None:
        return "(None)"
    if isinstance(obj, (int, float, str)):
        return str(obj)
    if isinstance(obj, Config):
        return json.dumps({
            "root_uri": obj.root_uri,
            "init_opts": obj.init_opts,
            "capabilities": obj.capabilities
        })
    if isinstance(obj, Workspace):
        return json.dumps({
            "root_uri": obj.root_uri,
            "root_path": obj.root_path,
            "documents_count": len(obj.documents),
            "documents": [str(d) for d in obj.documents],
        })
    if isinstance(obj, Document):
        return json.dumps({
            "uri": obj.uri,
            "version": obj.version,
            "filename": obj.filename,
            "dot_path": obj.dot_path,
        })
    return json.dumps(obj)

def get_engine_id(config: Config) -> str:
    return config.init_opts["engineId"]
