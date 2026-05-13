# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
# https://stackoverflow.com/a/57387909
# https://stackoverflow.com/a/63967448
"""Fonctions de contrôle ordiné."""

import logging
import sys
from queue import ShutDown
from threading import Thread
from typing import TYPE_CHECKING

from .serie import FilAppelReponse, FileCommandes, FileRéponses, Réponse

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
