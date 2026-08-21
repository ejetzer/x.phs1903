# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
# https://stackoverflow.com/a/57387909
# https://stackoverflow.com/a/63967448
"""Fonctions de contrôle ordiné."""

import threading
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from .logging import WithLogger
from .dummy import signal, noise
from .serial import LigneSerie, ArduinoNanoEvery

if TYPE_CHECKING:
    from types import TracebackType
    from typing import Self

type TraceurSerie = list[dict[str, float]]
type IterTraceurSerie = iter[dict[str, float]]


class Tableau(WithLogger):
    """Tableau d'acquisition de données par la ligne série."""

    def __init__(self, ser: LigneSerie | None) -> None:
        """Initialise le tableau."""
        self.__iter: LigneSerie | None = ser
        self.__df: pd.DataFrame = pd.DataFrame()
        self.__buffer: list[pd.Series] = []
        self.__thread_consume: threading.Thread = threading.Thread(
            target=self.__run_consume,
            daemon=True
        )
        self.__thread_update: threading.Thread = threading.Thread(
            target=self.__run_update
        )
        self.__arret: threading.Event = threading.Event()
        self.__loquet_df: threading.Lock = threading.Lock()
        self.__loquet_buffer: threading.Lock = threading.Lock()
        self._updated: threading.Event = threading.Event()

    @property
    def connection(self) -> LigneSerie | None:
        return self.__iter

    @connection.setter
    def connection(self, val: LigneSerie | None) -> None:
        if val is not None and not isinstance(val, LigneSerie):
            raise TypeError

        self.__iter = val

    def __run_consume(self) -> None:
        """Lit les nouvelles données."""
        self.checkin()

        try:
            while not self.__arret.is_set():
                ser = None
                if self.__iter is not None:
                    ser = self.__iter.next(block=False, parse=True)

                if ser is not None:
                    self.debug('ser = %r', ser)
                    with self.__loquet_buffer:
                        self.__buffer.append(pd.Series(ser).to_frame().T)
                        self.debug('len(buffer) = %s', len(self.__buffer))
        except Exception as err:
            self.error('', exc_info=err)
        finally:
            if not self.__arret.is_set():
                self.__arret.set()

    def __run_update(self) -> None:
        """Concatène les DataFrame."""
        self.checkin()

        try:
            while not self.__arret.is_set():
                if len(self.__buffer) > 0:
                    self.debug('len(buffer) = %s', len(self.__buffer))
                    with self.__loquet_buffer, self.__loquet_df:
                        self.__df = pd.concat([self.__df] + self.__buffer).reset_index(
                            drop=True
                        )
                        self.__buffer = []

                        if not self._updated.is_set():
                            self._updated.set()
        except Exception as err:
            self.error('', exc_info=err)
        finally:
            if not self.__arret.is_set():
                self.__arret.set()

    def close(self) -> None:
        """Arrête la compilation des données."""
        self.checkin()
        self.__arret.set()
        self.__thread_update.join()
        self.__thread_consume.join()

    def __iter__(self) -> Self:
        """Retourne soi-même.

        Returns
        ---------------------
        self: Tableau
        """
        self.checkin()
        return self

    def __next__(self) -> pd.DataFrame:
        """Retourne un DataFrame à jour.

        Returns
        ---------------------
        self.df: pandas.DataFrame
        """
        self.checkin()
        return self.df

    def start(self, *, ser: LigneSerie | None = None) -> None:
        """Démarre l'exécution."""
        self.checkin()

        if ser is not None and self.__iter is not None:
            raise ValueError
        elif ser is not None:
            self.__iter = ser

        self.__thread_consume.start()
        self.__thread_update.start()

    def __enter__(self) -> Self:
        """Démarre la compilation des données.

        Returns
        ---------------------
        self: Tableau
            Soi-même.
        """
        self.checkin()
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        """Ferme le tableau.

        Returns
        ---------------------
        False
            Soulève toute exception.
        """
        self.checkin()
        self.close()
        return False  # Re-raise the exception please

    @property
    def df(self) -> pd.DataFrame:
        """Obtiens sécuritairement une copie du DataFrame interne.

        Returns
        ---------------------
        ret: pandas.DataFrame
            La copie du DataFrame sous-jacent.
        """
        self.checkin()
        ret = pd.DataFrame()
        with self.__loquet_df:
            ret = self.__df.copy()
        return ret  # noqa: RET504

    def __getitem__(self, key: int) -> pd.DataFrame:
        self.checkin()
        if key > len(self.df.columns) // 2:
            raise KeyError

        i = 2*key
        return self.df.iloc[:, i:i+2]

    @property
    def ts(self) -> pd.DataFrame:
        self.checkin()
        num = len(self.df.columns)
        return [self.df.iloc[:, i] for i in range(0, num, 2)]

    @property
    def xs(self) -> pd.DataFrame:
        self.checkin()
        num = len(self.df.columns)
        return [self.df.iloc[:, i+1] for i in range(0, num, 2)]

    def wait(self) -> None:
        self.__iter.wait()

        while len(self.__buffer) > 0:
            continue


def aléatoire():
    yield from signal(*noise(d=4), bunch=10)


def sinus():
    yield from signal(np.sin, np.cos, bunch=10, noise=noise(d=2))


def echotab(*, debug: bool = True) -> None:
    """Démonstration des outils d'acquisition."""
    import time  # noqa: PLC0415

    lignes = sinus()
    with LigneSerie() as com:
        with Tableau(com) as tab:
            if debug:
                tab.log_to_stderr()
                tab.setLevel('debug')

            for ligne in lignes:
                try:
                    com.print(ligne)
                    print(tab.df)
                    time.sleep(5)
                except KeyboardInterrupt:
                    break

def ardtab(*, debug: bool = False) -> None:
    import time

    with ArduinoNanoEvery() as ard:
        with Tableau(ard) as tab:
            while True:
                try:
                    print(tab.df)
                    time.sleep(5)
                except KeyboardInterrupt:
                    break

__all__ = ['Tableau']
