# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../'))

# -- Project information -----------------------------------------------------

project = 'Open Pectus'
copyright = '2023, Open Pectus'
author = 'Open Pectus'

# -- General configuration ---------------------------------------------------
numfig = True
# -- General configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.mermaid",
]
autosummary_generate = True  # Turn on sphinx.ext.autosummary

intersphinx_mapping = {
    "rtd": ('https://docs.readthedocs.io/en/stable/', None),
    "python": ('https://docs.python.org/3/', None),
    "sphinx": ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for EPUB output
epub_show_urls = 'footnote'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['static']
#html_sidebars = { '**': ['globaltoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html'] }

# P-code lexer for highlighting
from pygments.lexer import RegexLexer, bygroups
from pygments.token import *

__all__ = ['pcodeLexer']

class pcodeLexer(RegexLexer):
    name = 'p-code'
    aliases = ['pcode']
    filenames = ['*.pcode']

    tokens = {
        'root': [
            (r'((?: {4})*)( )*((?:\d*(?:\.\d*)?) )?([^:#\n]+)(: (?:[^#\n]+))?(\s*#\s*(?:.*$))?(\n)?',
            bygroups(Whitespace, Error, Literal.Number, Keyword, Name, Comment, Text)),
        ],
    }
from sphinx.highlighting import lexers
lexers['pcode'] = pcodeLexer(startinline=True)