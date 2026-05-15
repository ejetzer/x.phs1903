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

from .serie import FilAppelReponse, FileCommandes, FileRéponses, Réponse
from .data import Data, FileData

if TYPE_CHECKING:
    from collections.abc import Callable

    from pandas import DataFrame
    from serial import Serial


class FilEntree(Thread):
    def __init__(
        self,
        commandes: FileCommandes | None = None,
        invite: str = '>>>',
        encoding: str = 'utf-8',
    ):
        self.commandes = commandes
        self.invite: str = invite
        self.encoding: str = encoding

        super().__init__(daemon=True)

    @classmethod
    def dune_ligneserie(cls, ser: FilAppelReponse):
        return cls(ser.commandes)

    def run(self):
        while not self.arret:
            nouv: str = input(self.invite)
            cmd: bytes = bytes(nouv, encoding=self.encoding)
            try:
                self.commandes.put(nouv, cmd=cmd)
            except ShutDown:
                break

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.join()
        return exc[0] is None


class FilSortie(Thread):
    def __init__(
        self, reponses: FileRéponses | None = None, prefixe: str = ''
    ):
        self.reponses: FileRéponses = reponses
        self.prefixe: str = prefixe
        super().__init__(daemon=True)

    def run(self):
        while True:
            try:
                nouv: Réponse = self.reponses.get()
            except ShutDown:
                break
            print(f'{self.prefixe}{nouv}')

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.join()
        return exc[0] is None


class Traceur:
    def __init__(self, data: FileData | None, ax: Axes | None):
        self.data: FileData = data
        self.ax: Axes = ax

    def call(self):
        try:
            df: Data = self.data.get()
        except ShutDown:
            break
        else:
            df.plot(ax=self.axes)
