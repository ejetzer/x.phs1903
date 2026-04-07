# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Affichage de mesures sur un graphe en temps réel."""

import logging
import sys
from typing import TYPE_CHECKING

import pandas as pd
from pandas import DataFrame

from .console import Programme

if TYPE_CHECKING:
    from collections.abc import Callable

    from pandas import Series

if not (sys.version_info.major != '3' and sys.version_info.minor < '14'):
    print(f'La version de Python utilisée est: {sys.version}', file=sys.stderr)
    print(f'{__name__} nécessite Python 3.14 et postérieur.', file=sys.stderr)
    print('Voir <https://www.python.org/downloads>', file=sys.stderr)
    msg: str = 'Version de Python incompatible'
    raise SystemExit(msg)

logging = logging.getLogger(__name__)


class Acquisition(Programme):
    """Programme d'acquisition de données."""

    def __init__(self, port: str, *cmds: str, loop: bool = False) -> None:
        """Programme d'acquisition de données."""
        super(self).__init__(port, *cmds, loop)
        self.stack = DataFrame()

    def __next__(self) -> str:
        """Exécution d'une commande du programme."""
        self.msg = self.cmds[self.pos].format(stack=self.stack)
        self.canal.write(msg)
        self.rep = self.canal.read(d='\n')
        print(self.rep)

        self.stack = pd.concat([
            self.stack,
            DataFrame({'x': [self.msg], 'y': [self.rep]}),
        ])

        self.pos += 1
        if self.pos == len(self.cmds):
            if self.loop:
                self.pos = 0
            else:
                raise StopIteration

        return self.rep

    def iterrows(self) -> Series:
        """Itérateur des commandes et réponses passées."""
        yield from self.stack.iterrows()

    @property
    def loc(self) -> DataFrame:
        """Localisateur du cadre de données sous-jacent."""
        return self.stack.loc

    def print(
        self,
        x_col: str = 'x',
        x_fmt: Callable = lambda x: x,
        y_col: str = 'y',
        y_fmt: Callable = lambda y: y,
    ) -> None:
        """Afficher les commandes et données dans un tableau."""
        self.stack.loc[:, x_col] = self.stack.loc[:, :].apply(x_fmt)
        self.stack.loc[:, y_col] = self.stack.loc[:, :].apply(y_fmt)
        print(self.stack.loc[:, [x_col, y_col]])

    def plot(
        self,
        x_col: str = 'x',
        x_fmt: Callable = lambda x: x,
        y_col: str = 'y',
        y_fmt: Callable = lambda y: y,
    ) -> None:
        """Afficher les données dans un graphe."""
        self.stack.loc[:, x_col] = self.stack.loc[:, :].apply(x_fmt)
        self.stack.loc[:, y_col] = self.stack.loc[:, :].apply(y_fmt)
        self.stack.loc[:, [x_col, y_col]].plot()
