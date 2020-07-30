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


import sys

#MOCK_MODULES = ['numpy', 'scipy', 'matplotlib', 'matplotlib.pyplot', 'scipy.interpolate']
#for mod_name in MOCK_MODULES:
#    sys.modules[mod_name] = mock.Mock()
# -- Project information -----------------------------------------------------

project = 'ipympl-interactions'
copyright = '2020, Ian Hunt-Isaak'
author = 'Ian Hunt-Isaak'

# The full version, including alpha/beta/rc tags
release = '0.12'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
#    'sphinx.ext.autodoc',
#    'sphinx.ext.autosummary',
    'nbsphinx',
    'nbsphinx_link',
    'sphinx.ext.mathjax',
#    'sphinx.ext.napoleon']
    'numpydoc',]

nbsphinx_execute = 'always'
nbsphinx_execute_arguments = [
    "--InlineBackend.figure_formats={'svg', 'pdf'}",
    "--InlineBackend.rc={'figure.dpi': 96}",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**ipynb_checkpoints']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'nature'
html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'

html_theme_options = {
        # Toc options
        'collapse_navigation': False,
        'sticky_navigation': True,
        'navigation_depth': 2,
}


master_doc = 'index'


# following: https://github.com/readthedocs/sphinx_rtd_theme/issues/766#issuecomment-517145293
# to fix an issue with rendering numpydoc in read the docs style
def setup(app):
    app.add_css_file("basic.css")
