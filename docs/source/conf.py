# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'x.phs1903'
copyright = '2025, Émile Jetzer & Jacques Massicotte'
author = 'Émile Jetzer & Jacques Massicotte'
release = '1.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'hawkmoth' # https://github.com/jnikula/hawkmoth
]

templates_path = ['_templates']
exclude_patterns = []

hawkmoth_root = 'src/'

autosectionlabel_prefix_document = True

extlinks = {
    'arduino': ('https://docs.arduino.cc/language-reference/en/%s', '%s'),
    'arduino-card': ('https://docs.arduino.cc/hardware/en/%s', '%s'),
    'gammon': ('https://www.gammon.com.au/', '%s')
}

extlinks_detect_hardcoded_links = True

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('http://docs.scipy.org/doc/numpy', None),
    'scipy': ('http://docs.scipy.org/doc/scipy/', None),
    'matplotlib': ('http://matplotlib.org/stable', None),
    'Sphinx': ('https://www.sphinx-doc.org/en/master/', None),
    'serial': ('https://pyserial.readthedocs.io/en/latest/', None),
    'pip': ('https://pip.pypa.io/en/stable/', None),
    'pipenv': ('https://pipenv.pypa.io/en/latest/', None),
    'conda': ('https://docs.conda.io/projects/conda/en/stable/', None)
}

language = 'fr'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'classic'
html_static_path = ['_static']

# Configuration d'autodoc
import sys
from pathlib import Path

sys.path.insert(0, str(Path('..', '..', 'src').resolve()))
