# Copyright (C) 2025 Émile Jetzer, Polytechnique Montréal
# autodoc: <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>
"""
Fichier de configuration pour le constructeur documentaire Sphinx.

Pour la liste complète des valeurs de configurations incluses, voir la
documentation: <https://www.sphinx-doc.org/en/master/usage/configuration.html>
"""

import logging
import os
import os.path
import sys
from pathlib import Path

import pygit2 as pygit
from clang.cindex import Config
from hawkmoth.util import readthedocs

__logger = logging.getLogger(__name__)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'x.phs1903'
author = 'Émile Jetzer & Jacques Massicotte, Polytechnique Montréal'
project_copyright = '%Y ' + author

__logger.info('Configuration de la document pour %s', project)
__logger.info('Écrit par %s', author)
__logger.info('%s', project_copyright)

repo_path = (Path(__file__) / '..' / '..' / '..' / '.git').resolve()
__logger.info('Répertoire git: %s', repo_path)

try:
    import pygit2 as pygit

    repo = pygit.Repository(repo_path)
    reference = repo.describe(dirty_suffix='+')
except (ImportError, pygit.GitError) as err:
    __logger.warning('Erreur avec PyGit2', exc_info=err)

    import subprocess  # noqa: S404

    reference = subprocess.run(
        ['/usr/bin/git', 'describe', '--always'],
        capture_output=True,
        check=True,
    ).stdout.decode('utf-8')
finally:
    release = reference.lstrip('v')
    version = release
    __logger.info('Version %s', release)

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

templates_path = ['_templates']
exclude_patterns = []

# Configuration d'autodoc
autoclass_content = 'init'
autodoc_class_signature = 'mixed'
autodoc_typehints = 'both'
autodoc_typehints_description_target = 'all'
autodoc_typehints_format = 'short'
autodoc_inherit_docstrings = False

# Configuration de Napoléon
napoleon_include_init_with_doc = False

# Ajout du répertoire de code source au chemin Python
sys.path.insert(0, str((Path().parent.parent / 'src').resolve()))

autosectionlabel_prefix_document = True

# Configuration de Hawkmoth
hawkmoth_root = Path().parent.parent.resolve()
arduino_libs = (
    Path('/')
    / 'Volumes'
    / 'data'
    / 'home'
    / 'emilejetzer'
    / 'Library'
    / 'Arduino15'
    / 'packages'
    / 'arduino'
)
hawkmoth_domain = 'cpp'
hawkmoth_clang = [
    '-DHAWKMOTH',
    f'-I{hawkmoth_root}/lib/arduinoHawkmoth',
]

dev_clang = (
    Path().parent
    / '.venv'
    / 'lib'
    / 'python3.14'
    / 'site-packages'
    / 'clang'
    / 'native'
    / 'libclang.dylib'
)
clang_file_set = False

if dev_clang.exists():
    Config.set_library_file(str(dev_clang))
    __logger.info('Using %s', dev_clang)
    clang_file_set = True
else:
    any_clang = Path().rglob('libclang.*')
    for cl in any_clang:
        if cl.exists():
            Config.set_library_file(str(cl))
            __logger.warning('Using %s', cl)
            clang_file_set = True
            break

if not clang_file_set:
    __logger.warning('Recherche de clang...')
    readthedocs.clang_setup()

# Configuration des liens externes
extlinks = {
    'arduino': ('https://docs.arduino.cc/language-reference/en/%s', '%s'),
    'arduinolib': ('https://docs.arduino.cc/libraries/%s', '%s'),
    'arduinocard': ('https://docs.arduino.cc/hardware/en/%s', '%s'),
    'gammon': ('https://www.gammon.com.au/%s', '%s'),
}
extlinks_detect_hardcoded_links = True

# Configuration des liens inter-documentation
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
    'pandas': ('https://pandas.pydata.org/docs/', None),
}

language = 'fr'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
html_copy_source = True
html_show_sourcelink = True
html_logo = 'logo-noir.png'
html_use_index = True
html_show_copyright = True
html_search_language = 'fr'

# Options pour la sortie LaTeX et PDF
latex_engine = 'lualatex'
latex_elements = {
    'preamble': r'\usepackage{unicode-math}',
    'papersize': 'letterpaper',
    'babel': r'\usepackage[french]{babel}',
    'tableofcontents': r'\sphinxtableofcontents',
}
latex_additional_files = [
    'latexmkrc',
    'xindex-sphinx.lua',
    'logo-noir.png',
]
latex_logo = 'logo-noir.png'

# -- Options pour viewcode -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/viewcode.html

viewcode_follow_imported_members = True
viewcode_line_numbers = True
