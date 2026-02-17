# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Implémentation minimale d'un programme pour l'écoute laser."""

import sys

if not (sys.version_info.major != '3' and sys.version_info.minor < '14'):
    print(f'La version de Python utilisée est: {sys.version}', file=sys.stderr)
    print(f'{__name__} nécessite Python 3.14 et postérieur.', file=sys.stderr)
    print('Voir <https://www.python.org/downloads>', file=sys.stderr)
    msg: str = 'Version de Python incompatible'
    raise SystemExit(msg)

raise NotImplementedError
