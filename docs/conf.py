# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import inspect

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

import sphinx_rtd_theme

import mpl_interactions as mpl_inter

sys.path.insert(0, os.path.abspath("../mpl_interactions"))
sys.path.insert(0, os.path.abspath("."))
from gifmaker import gogogo_all

gogogo_all("../examples", "examples/")
gogogo_all("../examples/tidbits", "examples/tidbits/")

release = mpl_inter.__version__


# -- Project information -----------------------------------------------------

project = "mpl-interactions"
copyright = "2020, Ian Hunt-Isaak"
author = "Ian Hunt-Isaak"

# The full version, including alpha/beta/rc tags


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.mathjax",
    "sphinx.ext.linkcode",
    "sphinx.ext.napoleon",
    "numpydoc",
    "jupyter_sphinx",
    "nbsphinx",
    "sphinx_copybutton",
    "sphinx_gallery.gen_gallery",
]

from mpl_playback.scraper import matplotlib_scraper

sphinx_gallery_conf = {
    "examples_dirs": "../examples/gallery",  # path to your example scripts
    "gallery_dirs": "gallery",  # path to where to save gallery generated output
    "filename_pattern": "/.*",
    "ignore_pattern": "/_.*",  # https://www.debuggex.com/
    "image_scrapers": (matplotlib_scraper),
}


# prolog taken nearly verbatim from https://github.com/spatialaudio/nbsphinx/blob/98005a9d6b331b7d6d14221539154df69f7ae51a/doc/conf.py#L38
nbsphinx_prolog = r"""
{% set docname = env.doc2path(env.docname, base=None) %}

.. raw:: html

    <div class="admonition note">
      This page was generated from
      <a class="reference external" href="https://github.com/ianhi/mpl-interactions/blob/{{ env.config.release|e }}/{{ docname|e }}">{{ docname|e }}</a>.
      Interactive online version:
      (Warning: The interactions will be much laggier on Binder than on your computer.)
      <span style="white-space: nowrap;"><a href="https://mybinder.org/v2/gh/ianhi/mpl-interactions/{{ env.config.release|e }}?filepath={{ docname|e }}"><img alt="Binder badge" src="https://mybinder.org/badge_logo.svg" style="vertical-align:text-bottom"></a>.</span>
    </div>

.. raw:: latex

    \nbsphinxstartnotebook{\scriptsize\noindent\strut
    \textcolor{gray}{The following section was generated from
    \sphinxcode{\sphinxupquote{\strut {{ docname | escape_latex }}}} \dotfill}}
"""

nbsphinx_execute = "never"
# nbsphinx_allow_errors = True

# ensure widget output is not duplicated
# see https://github.com/spatialaudio/nbsphinx/issues/378
nbsphinx_widgets_path = ""

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = False
napoleon_use_rtype = False
add_module_names = False

autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = ['css/custom.css']

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**ipynb_checkpoints"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_theme_options = {
    # Toc options
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
}


master_doc = "index"


def setup(app):
    app.add_css_file("custom.css")


# based on pandas/doc/source/conf.py
def linkcode_resolve(domain, info):
    """
    Determine the URL corresponding to Python object
    """
    if domain != "py":
        return None

    modname = info["module"]
    fullname = info["fullname"]

    submod = sys.modules.get(modname)
    if submod is None:
        return None

    obj = submod
    for part in fullname.split("."):
        try:
            obj = getattr(obj, part)
        except AttributeError:
            return None

    try:
        fn = inspect.getsourcefile(inspect.unwrap(obj))
    except TypeError:
        fn = None
    if not fn:
        return None

    try:
        source, lineno = inspect.getsourcelines(obj)
    except OSError:
        lineno = None

    if lineno:
        linespec = f"#L{lineno}-L{lineno + len(source) - 1}"
    else:
        linespec = ""

    fn = os.path.relpath(fn, start=os.path.dirname(mpl_inter.__file__))

    return f"https://github.com/ianhi/mpl-interactions/blob/master/mpl_interactions/{fn}{linespec}"
