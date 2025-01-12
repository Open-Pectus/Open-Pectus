import os

from sphinx.highlighting import lexers
from pygments.lexer import RegexLexer, bygroups
from pygments import token

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# Project information
project = "Open Pectus"
copyright = "2025, Open Pectus"
author = "Open Pectus"

# General configuration
source_suffix = {".rst": "restructuredtext"}
language = "en"
master_doc = "index"
numfig = True
todo_include_todos = True
autoapi_generate_api_docs = True
autoapi_dirs = [
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "openpectus",
    )
]
autoapi_ignore = ["*alembic/versions*"]
autoapi_keep_files = True
autoapi_add_toctree_entry = True
autodoc_typehints = 'description'
spelling_exclude_patterns = ["autoapi**", "_autosummary**", '**To Do List.rst']
spelling_word_list_filename = "spelling_wordlist.txt"

# Sphinx extensions
extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinxcontrib.mermaid",
    "sphinxcontrib.openapi",
    "sphinxcontrib.spelling",
    "sphinxarg.ext",
    "sphinx.ext.autodoc",
    "autoapi.extension",
]

templates_path = ["_templates"]
exclude_patterns = ["html", "Thumbs.db", ".DS_Store"]
html_theme = "sphinx_rtd_theme"
html_static_path = ["src/static"]
html_css_files = ['custom.css']

__all__ = ["pcodeLexer"]


class pcodeLexer(RegexLexer):
    name = "p-code"
    aliases = ["pcode"]
    filenames = ["*.pcode"]

    tokens = dict(root=[
        (
            # Indent
            r"((?: {4})*)" +  # Matches multiples of 4 white space
            # Possible syntax error
            r"( )*" +
            # Threshold
            r"((?:\d*(?:\.\d*)?) )?" +  # Matches a positive decimal number
            # Command
            r"([^:#\n]+)" +  # Matches string not comment
            # Command argument
            r"(: (?:[^#\n]+))?" +  # Matches string not comment including :
            # Comment
            r"(\s*#\s*(?:.*$))?" +  # Matches string startin with #
            r"(\n)?",  # Next line in method
            bygroups(
                token.Whitespace,
                token.Error,
                token.String,
                token.Keyword,
                token.Name,
                token.Comment,
                token.Text
            )
        ),
    ])


lexers["pcode"] = pcodeLexer(startinline=True)
