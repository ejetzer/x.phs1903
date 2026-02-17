# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
# autodoc: <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>
"""
Sous-modules facilitant l'implémentation de fonctionnalités avancées.

Si vous êtes un étudiant de la session courante du cours PHS1903,
vous devriez consulter votre chargé de projet et technicien pour vérifier
si vous êtes assez avancés pour vous concentrer sur ces ajouts.
"""

import sys

if not (sys.version_info.major != '3' and sys.version_info.minor < '14'):
    print(f'La version de Python utilisée est: {sys.version}', file=sys.stderr)
    print(f'{__name__} nécessite Python 3.14 et postérieur.', file=sys.stderr)
    print('Voir <https://www.python.org/downloads>', file=sys.stderr)
    msg: str = 'Version de Python incompatible'
    raise SystemExit(msg)
