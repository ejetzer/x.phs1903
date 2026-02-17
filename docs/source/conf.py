# Copyright (C) 2025 Émile Jetzer, Polytechnique Montréal
# autodoc: <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>
"""
Fichier de configuration pour le constructeur documentaire Sphinx.

Pour la liste complète des valeurs de configurations incluses, voir la
documentation: <https://www.sphinx-doc.org/en/master/usage/configuration.html>
"""

import sys
from pathlib import Path

from clang.cindex import Config

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'x.phs1903'
author = 'Émile Jetzer & Jacques Massicotte, Polytechnique Montréal'
project_copyright = '%Y ' + author
release = '2.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'hawkmoth',  # https://github.com/jnikula/hawkmoth
    'hawkmoth.ext.napoleon',
]

# Autres extensions:
# 'sphinx_readme' <https://sphinx-readme.readthedocs.io/en/latest/index.html>

templates_path = ['_templates']
exclude_patterns = []

# Configuration d'autodoc
autoclass_content = 'both'
autodoc_class_signature = 'mixed'
autodoc_typehints = 'both'
autodoc_typehints_description_target = 'all'
autodoc_typehints_format = 'short'
autodoc_inherit_docstrings = True

sys.path.insert(0, str(Path('..', '..', 'src').resolve()))

hawkmoth_root = str(Path('..', '..', 'src').resolve())
hawkmoth_clang = ['-DA0=23', '-DA1=22', '-DA2=21']

autosectionlabel_prefix_document = True

extlinks = {
    'arduino': ('https://docs.arduino.cc/language-reference/en/%s', '%s'),
    'arduinocard': ('https://docs.arduino.cc/hardware/en/%s', '%s'),
    'gammon': ('https://www.gammon.com.au/%s', '%s'),
}

extlinks_detect_hardcoded_links = True

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'matplotlib': ('https://matplotlib.org/stable', None),
    'Sphinx': ('https://www.sphinx-doc.org/en/master/', None),
    'serial': ('https://pyserial.readthedocs.io/en/latest/', None),
    'pip': ('https://pip.pypa.io/en/stable/', None),
    'pipenv': ('https://pipenv.pypa.io/en/latest/', None),
    'conda': ('https://docs.conda.io/projects/conda/en/stable/', None),
}

language = 'fr'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'classic'
html_static_path = ['_static']

# Options pour la sortie LaTeX
latex_additional_files = [
    'latexmkrc',
]
