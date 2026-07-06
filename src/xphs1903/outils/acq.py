# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
# https://stackoverflow.com/a/57387909
# https://stackoverflow.com/a/63967448
"""Fonctions de contrôle ordiné."""

import logging
import sys
from queue import ShutDown
from threading import Thread
from typing import TYPE_CHECKING

from matplotlib.axes import Axes

from .data import Data, FileData
from .serie import FilAppelReponse, FileCommandes, FileRéponses, Réponse

if TYPE_CHECKING:
    from collections.abc import Callable

    from pandas import DataFrame
    from serial import Serial


class Clavier:
    """Capture l'entrée clavier et la transmet à un autre fil."""
    pass

class Fichier:
    """Reçoit des entrées et les écrits dans un fichier bloc par bloc."""
    pass

class Sortie:
    """Reçoit des entrées et les écrits dans la sortie standard."""
    pass

class Données(Fichier):
    """Sauvegarde des entrées dans un:class:`~pandas.DataFrame`."""

class LigneSérie(Clavier):
    pass

class Arduino(LigneSérie):
    pass

class TerminalArduino(Arduino):
    pass

class TraceurArduino(Arduino):
    pass
