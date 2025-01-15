import ast
import atexit
import collections
import json
import logging
import os
import os.path
import subprocess
from configparser import ConfigParser
from pathlib import Path
from typing import IO, Any, Dict, List, Optional

import tomllib

from pylsp import hookimpl
from pylsp.config.config import Config
from pylsp.workspace import Document, Workspace

#logging.basicConfig(format=' %(name)s :: %(levelname)-8s :: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# A mapping from workspace path to config file path
mypyConfigFileMap: Dict[str, Optional[str]] = {}

settingsCache: Dict[str, Dict[str, Any]] = {}

tmpFile: Optional[IO[str]] = None

# In non-live-mode the file contents aren't updated.
# Returning an empty diagnostic clears the diagnostic result,
# so store a cache of last diagnostics for each file a-la the pylint plugin,
# so we can return some potentially-stale diagnostics.
# https://github.com/python-lsp/python-lsp-server/blob/v1.0.1/pylsp/plugins/pylint_lint.py#L55-L62
last_diagnostics: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)

# Windows started opening opening a cmd-like window for every subprocess call
# This flag prevents that.
# This flag is new in python 3.7
# This flag only exists on Windows
windows_flag: Dict[str, int] = (
    {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}  # type: ignore
)


# see hooks: https://github.com/python-lsp/python-lsp-server/blob/develop/pylsp/hookspecs.py

logger.info("Openpectus lsp plugin loading")

open_document: Document | None = None


def get_open_document() -> Document | None:
    logger.debug("get_open_document")
    return open_document


def set_open_document(document: Document):
    logger.debug("set_open_document")
    logger.debug("document: " + str(document))
    global open_document
    open_document = document


# def obj_to_str(o) -> str:
#     def is_simple_type(type_name):
#         return type_name in ['str', 'int', 'float']

#     type_name = type(o).__name__
#     lines = [type_name]

#     for key in o.__dict__.keys():
#         lines.append(f"{key}:\t" + str(o.__dict__[key]))
#     return "\n".join(lines)


def find_first_word_position(document: Document, word: str):
    for i, line in enumerate(document.lines):
        if word in line:
            character = line.index(word)
            return {"line": i, "character": character}
    return None


@hookimpl
def pylsp_initialize(config: Config, workspace: Workspace):
    logger.info(f"pectus pylsp_initialize,\
        workspace doc count: {len(workspace.documents)}")
    # config is a tricky object to display logger.debug("config:" + as_json(config))
    logger.debug("config:" + str(config))
    logger.debug("workspace:" + str(workspace))


@hookimpl
def pylsp_initialized():
    logger.info("pectus pylsp_initialized")


@hookimpl
def pylsp_document_did_open(config: Config, workspace: Workspace, document: Document):
    logger.info(f"pylsp_document_did_open, \
        workspace: {workspace}, \
        document.source: \n\n{document.source}\n\n")

    # print()
    # print("-------------- Config -------------")
    # print_obj(config)
    # print()
    # print("-------------- Workspace -------------")
    # print_obj(workspace)
    # print()
    # print("-------------- Document -------------")
    # print_obj(document)
    # print()

    set_open_document(document)


@hookimpl
def pylsp_document_did_save(config, workspace, document):
    logger.info(f"pylsp_document_did_save, workspace: {workspace}, document: {document}")


@hookimpl
def pylsp_lint(
    config: Config, workspace: Workspace, document: Document, is_saved: bool
) -> List[Dict[str, Any]]:

    diagnostics = []
    diagnostics.append(
        {
            "source": "pectus",
            "range": {
                "start": {"line": 0, "character": 0},
                # Client is supposed to clip end column to line length.
                "end": {"line": 0, "character": 1000},
            },
            "code": "Foo bar",
            "message": "my error",
            "severity": 1,  # Error: 1, Warning: 2, Information: 3, Hint: 4
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


@hookimpl
def pylsp_hover(config: Config, workspace: Workspace, document: Document, position):

    word = document.word_at_position(position)
    logger.info(f"pylsp_hover, \
        workspace: {workspace.root_uri}, \
        document.source: {document.source}, \
        position: {position}\
        source word: {word}")
    if word and word != "secret":
        return {"contents": {"kind": "markdown", "value": f"You hovered the word: '{word}'"}}
    return None


# @hookimpl
# def pylsp_settings(config: Config) -> Dict[str, Dict[str, Dict[str, str]]]:
#     """
#     Read the settings.

#     Parameters
#     ----------
#     config : Config
#         The pylsp config.

#     Returns
#     -------
#     Dict[str, Dict[str, Dict[str, str]]]
#         The config dict.

#     """
#     logger.info(f"pylsp_settings, config: {config}")

#     configuration = init(config._root_path)

#     logger.info(f"pylsp_settings returning, configuration: {configuration}")
#     return {"plugins": {"pylsp_pectus": configuration}}

def as_json(obj) -> str:
    if obj is None:
        return "(None)"
    if isinstance(obj, (int, float, str)):
        return str(obj)
    return json.dumps(obj)

@hookimpl
def pylsp_settings(config: Config) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Configuration options that can be set on the client."""
    logger.info("pylsp_settings")
    #logger.info("config provided" + as_json(config))
    logger.info("config provided" + str(config))

    # configuration = init(config._root_path)
    configuration = {"enabled": True}

    logger.info("config._capabilities: \n" + str(config._capabilities).replace("'", '"'))

    # TODO disable textDocument/codeAction, textDocument/codeLens and textDocument/foldingRange
    # alternatively, we might implement textDocument/foldingRange for Block, Alarm and Watch
    # this does not work:
    # config._capabilities["textDocument"]["codeLens"]["dynamicRegistration"] = False

    # keys = config._config_sources.keys()
    # logger.info(f"config._config_sources: {', '.join(keys)}")

    return {
        "plugins": {
            "pylsp_openpectus": configuration,
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

def init(workspace: str) -> Dict[str, str]:
    """
    Find plugin and mypy config files and creates the temp file should it be used.

    Parameters
    ----------
    workspace : str
        The path to the current workspace.

    Returns
    -------
    Dict[str, str]
        The plugin config dict.

    """
    logger.info("init workspace = %s", workspace)
    logger.info("doing config file stuff ...")

    configuration = {}
    path = findConfigFile(
        workspace, [], ["pylsp-mypy.cfg", "mypy-ls.cfg", "mypy_ls.cfg", "pyproject.toml"], False
    )
    if path:
        if "pyproject.toml" in path:
            with open(path, "rb") as file:
                configuration = tomllib.load(file).get("tool").get("pylsp-mypy")
        else:
            with open(path) as file:
                configuration = ast.literal_eval(file.read())

    configSubPaths = configuration.get("config_sub_paths", [])
    mypyConfigFile = findConfigFile(
        workspace, configSubPaths, ["mypy.ini", ".mypy.ini", "pyproject.toml", "setup.cfg"], True
    )
    mypyConfigFileMap[workspace] = mypyConfigFile
    settingsCache[workspace] = configuration.copy()

    logger.info("mypyConfigFile = %s configuration = %s", mypyConfigFile, configuration)
    return configuration


def findConfigFile(
    path: str, configSubPaths: List[str], names: List[str], mypy: bool
) -> Optional[str]:
    """
    Search for a config file.

    Search for a file of a given name from the directory specifyed by path through all parent
    directories. The first file found is selected.

    Parameters
    ----------
    path : str
        The path where the search starts.
    configSubPaths : List[str]
        Additional sub search paths in which mypy configs might be located
    names : List[str]
        The file to be found (or alternative names).
    mypy : bool
        whether the config file searched is for mypy (plugin otherwise)

    Returns
    -------
    Optional[str]
        The path where the file has been found or None if no matching file has been found.

    """
    start = Path(path).joinpath(names[0])  # the join causes the parents to include path
    for parent in start.parents:
        for name in names:
            for subPath in [""] + configSubPaths:
                file = parent.joinpath(subPath).joinpath(name)
                if file.is_file():
                    if file.name in ["mypy-ls.cfg", "mypy_ls.cfg"]:
                        raise NameError(
                            f"{str(file)}: {file.name} is no longer supported, you should rename " +
                            "your config file to pylsp-mypy.cfg or preferably use a pyproject.toml " +
                            "instead."
                        )
                    if file.name == "pyproject.toml":
                        with open(file, "rb") as fileO:
                            configPresent = (
                                tomllib.load(fileO)
                                .get("tool", {})
                                .get("mypy" if mypy else "pylsp-mypy")
                                is not None
                            )
                        if not configPresent:
                            continue
                    if file.name == "setup.cfg":
                        config = ConfigParser()
                        config.read(str(file))
                        if "mypy" not in config:
                            continue
                    return str(file)
    # No config file found in the whole directory tree
    # -> check mypy default locations for mypy config
    if mypy:
        defaultPaths = ["~/.config/mypy/config", "~/.mypy.ini"]
        XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME")
        if XDG_CONFIG_HOME:
            defaultPaths.insert(0, f"{XDG_CONFIG_HOME}/mypy/config")
        for path in defaultPaths:
            if Path(path).expanduser().exists():
                return str(Path(path).expanduser())
    return None


@atexit.register
def close() -> None:
    """
    Deltes the tempFile should it exist.

    Returns
    -------
    None.

    """
    logger.info("close()")
    # if tmpFile and tmpFile.name:
    #     os.unlink(tmpFile.name)
