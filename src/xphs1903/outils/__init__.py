# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Fonctionnalités de base."""

# Activer la journalisation
import logging

# Modules internes du sous-module xphs1903.outils
import console
import definitions
import exceptions
import graphe
import serie

logging.getLogger(__name__).addHandler(logging.NullHandler())

# Objets accessibles avec import *
__all__ = [
    'console',
    'definitions',
    'exceptions',
    'graphe',
    'serie',
]
