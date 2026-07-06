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

if TYPE_CHECKING:
    from collections.abc import Callable

    from pandas import DataFrame
    from serial import Serial

class Format:
    pass

class FormatTexte(Format):
    pass

class FormatTraceurSerie(Format):
    pass

class FormatDico(Format):
    pass

class FormatListe(Format):
    pass

class FormatFlotOctets(Format):
    pass
