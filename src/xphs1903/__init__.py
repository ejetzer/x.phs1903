# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
# autodoc: <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>
"""
Module d'assistance pour PHS1903.

Les étudiants du cours PHS1903 à Polytechnique Montréal sont encouragés à
utiliser ce module pour simplifier leur efforts de programmation, et
les efforts de débogage des techniciens et chargés de projets.
"""

import sys

if not (sys.version_info.major != '3' and sys.version_info.minor < '14'):
    print(f'La version de Python utilisée est: {sys.version}', file=sys.stderr)
    print(f'{__name__} nécessite Python 3.14 et postérieur.', file=sys.stderr)
    print('Voir <https://www.python.org/downloads>', file=sys.stderr)
    msg: str = 'Version de Python incompatible'
    raise SystemExit(msg)

import extra

from outils import Acquisition, Canal, Console, Programme

__all__ = [
    'Canal',
    'Console',
    'Programme',
    'Acquisition',
    'extra',
]
