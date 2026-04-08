# -*- coding: utf-8 -*-
# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Fonctionnalités de base."""

import sys

from .console import Canal, Console, Programme
from .graphe import Acquisition
import logging
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from serial.tools.list_ports_common import ListPortInfo

class ChoixInvalideError(ValueError):
    # autodoc: <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>
    """Erreur indiquant un choix invalide."""


def choix() -> ListPortInfo:
    """
    Sélectionner un port série.

    Raises:
        ChoixInvalideError: indique un choix invalide.
        TypeError: indique une entrée non-numérique.

    Returns:
        ListPortInfo: port sélectionné.
    """
    from serial.tools.list_ports import comports  # noqa: PLC0415

    ports_disponibles: list[ListPortInfo] = comports()
    for i, c in enumerate(ports_disponibles):
        print(f'[{i}]\t{c.description}\t{c.device}')

    sélection: str = input('Quel port?')
    if sélection.isdigit():
        sélection = int(sélection)
    else:
        raise TypeError

    if sélection not in range(i):
        raise ChoixInvalideError

    return ports_disponibles[sélection]

__all__ = [
    'Canal',
    'Console',
    'Programme',
    'Acquisition',
    'ChoixInvalideError'
    'choix'
]