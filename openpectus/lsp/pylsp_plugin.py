import atexit
import json
import logging
import logging.config
from typing import Any

from pylsp import hookimpl
from pylsp.config.config import Config
from pylsp.workspace import Document, Workspace

from openpectus.lsp import lsp_analysis


# logging must be setup already - either by lsp/main or by the pylsp command
logger = logging.getLogger(__name__)



# hooks provided by pylsp: https://github.com/python-lsp/python-lsp-server/blob/develop/pylsp/hookspecs.py
# lsp spec overview: https://microsoft.github.io/language-server-protocol/overviews/lsp/overview/


logger.warning("Open Pectus LSP plugin loading")
logger.debug("Open Pectus LSP plugin loading - debug")
logger.info("Open Pectus LSP plugin loading - info")

@hookimpl
def pylsp_settings(config: Config) -> dict[str, dict[str, dict[str, Any]]]:
    """Configuration options that can be set on the client."""
    logger.info("pylsp_settings")
    # logger.info(f"config provided: {as_json(config)}")
    
    # logger.info("textDocument capabilities: " + as_json(config.capabilities["textDocument"]))
    # config.capabilities["textDocument"]["codeLens"] = None
    # config.capabilities["workspace"].pop("codeLens", None)
    # config.capabilities["textDocument"].pop("codeLens", None)

    # logger.info("textDocument capabilities modified: " + as_json(config.capabilities["textDocument"]))

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
        }
    }

# @hookimpl
# async def pylsp_initialize(config: Config, workspace: Workspace):
#     logger.info("pylsp_initialize")
#     logger.debug("config: " + as_json(config))
#     logger.debug("workspace:" + as_json(workspace))


@hookimpl
def pylsp_initialized():
    logger.debug("pylsp_initialized")


@hookimpl
def pylsp_document_did_open(config: Config, workspace: Workspace, document: Document):
    logger.info("pylsp_document_did_open")
    logger.debug(f"config: {as_json(config)}")
    # logger.debug(f"workspace: {as_json(workspace)}")
    logger.info(f"document: {as_json(document)}")


# @hookimpl
# def pylsp_document_did_save(config, workspace, document):
#     logger.info("pylsp_document_did_save")
#     # logger.debug(f"config: {as_json(config)}")
#     # logger.debug(f"workspace: {as_json(workspace)}")
#     # logger.info(f"document: {as_json(document)}")


@hookimpl
def pylsp_lint(config: Config, workspace: Workspace, document: Document, is_saved: bool) \
        -> list[lsp_analysis.DiagnosticsItem]:
    logger.debug("pylsp_lint")
    logger.debug(f"document: {as_json(document)}")
    logger.debug("Document source:'\n" + document.source + "\n'")
    # TODO get engine_id from document.uri, eg. document:
    # {"uri": "file:///workspace/model53.json", "version": 104, "filename": "model53.json", "dot_path": "model53"}
    engine_id = "MIAWLT-1645-MPO_DemoUod"
    try:
        diagnostics = lsp_analysis.lint(document, engine_id)
        #diagnostics = []
        logger.debug(f"Lint ok, items: {len(diagnostics)}")
        return diagnostics
    except Exception:
        logger.error("Lint error", exc_info=True)
        return []


# @hookimpl
# def pylsp_hover(config: Config, workspace: Workspace, document: Document, position):
#     logger.info("pylsp_hover")
#     logger.debug(f"config: {as_json(config)}")
#     logger.debug(f"workspace: {as_json(workspace)}")
#     logger.debug(f"document: {as_json(document)}")
#     logger.debug(f"position: {position}")
#     word = document.word_at_position(position)
#     logger.debug(f"source word: {word}")
#     logger.debug(f"position: {position}")
#     if word and word != "secret":
#         return {"contents": {"kind": "markdown", "value": f"You hovered the word: '{word}'"}}
#     return None


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


@atexit.register
def close() -> None:
    logger.info("close()")
