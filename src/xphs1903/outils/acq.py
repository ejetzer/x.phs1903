# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
# https://stackoverflow.com/a/57387909
# https://stackoverflow.com/a/63967448
"""Fonctions de contrôle ordiné."""

import logging
import sys
import queue
import threading
from typing import TYPE_CHECKING
import pandas as pd
import numpy as np

from matplotlib.axes import Axes

__logger = logging.getLogger(__name__)
"""Journal de débogage interne du module.

Utile pour le débogage, ne devrait être obtenu qu'avec
:func:`logging.getLogger`.
"""

__logger.addHandler(logging.NullHandler())

if TYPE_CHECKING:
    from collections.abc import Callable

    from pandas import DataFrame
    from serial import Serial

class Tableau:
    __logger = logging.getLogger(f'{__name__}.Tableau')
    """Journal de débogage pour les objets de classe Tableau."""

    __logger.addHandler(logging.NullHandler())

    def __init__(self, _iter: iter[dict[str, float]]) -> None:
        self.__iter: iter[dict[str, float]] = _iter
        self.__df: pd.DataFrame = pd.DataFrame()
        self.__buffer: list[pd.Series] = []
        self.__thread: threading.Thread = threading.Thread(target=self.__run)
        self.__queue: queue.Queue = queue.Queue()
        self.__arret: threading.Event = threading.Event()


    def __run(self):
        self.__logger.debug('%s', self.__iter)

        for i, ser in enumerate(self.__iter):
            if self.__arret.is_set():
                break

            try:
                self.__queue.put(pd.Series(ser).to_frame().T)
            except queue.ShutDown as err:
                self.__logger.info('%s', self.__queue, exc_info=err)
                break

        self.__logger.debug('%s', self.__queue)

    def close(self):
        self.__event.set()

    def __iter__(self):
        return self

    def __next__(self):
        return self.df

    def __enter__(self) -> Self:
        self.__thread.start()
        self.__logger.debug('%s', self.__thread)
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.__queue.shutdown()
        self.__thread.join()
        return True

    def __consume(self):
        self.__logger.debug('')
        count: int = 0
        while True:
            try:
                item = self.__queue.get(timeout=0.01)
                self.__logger.debug('#%s %s', count, item)
            except queue.Empty as err:
                self.__logger.debug('#%s %s', count, self.__queue, exc_info=err)
                break
            except queue.ShutDown as err:
                self.__logger.debug('#%s %s', count, self.__queue, exc_info=err)
                break
            except KeyboardInterrupt as err:
                self.__logger.debug('#%s %s', count, self.__queue, exc_info=err)
                break
            else:
                self.__buffer.append(item)
                self.__logger.debug('#%s %s', count, self.__buffer)
            finally:
                count += 1

    @property
    def df(self) -> pd.DataFrame:
        self.__logger.debug('')
        self.__consume()
        self.__logger.debug('%s', self.__buffer)

        if len(self.__buffer) > 0:
            self.__logger.debug('%s', self.__buffer)
            self.__logger.debug('%s', self.__df)

            self.__df = pd.concat([self.__df] + self.__buffer)\
                          .reset_index(drop=True)
            self.__logger.debug('%s', self.__df)

            del self.__buffer[:]
            self.__logger.debug('%s', self.__buffer)

        self.__logger.debug('%s', self.__df)
        return self.__df.copy()


def aléatoire(*, N: int = 10, incert: float = 0.001, seed: int = 1903) -> list[dict[str, float]]:
    gna = np.random.default_rng(seed=seed)
    ts = np.arange(N) + gna.normal(0, incert, N)
    xs = np.arange(N) + gna.normal(0, incert, N)
    ys = (np.arange(N) + gna.normal(0, incert, N))**2
    zs = (np.arange(N) + gna.normal(0, incert, N))**2
    lignes = [{'t': t, 'x': x, 'y': y, 'z': z} for t, x, y, z in zip(ts, xs, ys, zs)]
    return lignes

def sinus(*, N: int = 10, incert: float = 0.001, seed: int = 1903, phase: int = 0):
    gna = np.random.default_rng(seed=seed)
    ts = np.arange(phase, phase+N) + gna.normal(0, incert, N)
    xs = np.sin(np.arange(phase, phase+N)) + gna.normal(0, incert, N)
    lignes = [{'t': t, 'x': x} for t, x in zip(ts, xs)]
    return lignes

def main(*, debug: bool = True):
    from pprint import pprint
    import numpy as np
    from .serial import LigneSerie
    import time

    if debug:
        __logger.setLevel(logging.DEBUG)
        __handler = logging.StreamHandler()
        fmt: str = (
            '%(levelname)s\t'
            '%(threadName)s\t'
            '%(funcName)s (%(lineno)s)\t'
            '%(message)s'
        )
        __formatter = logging.Formatter(fmt)
        __handler.setFormatter(__formatter)
        __logger.addHandler(__handler)

    N = 50
    phase = 0
    lignes = sinus(N=N, phase=phase)

    with LigneSerie() as com:
        __logger.debug('%s', com)
        com.print(lignes)

        with Tableau(com.parse()) as tab:
            __logger.debug('%s', tab)

            while True:
                try:
                    phase += N
                    lignes = sinus(N=N, phase=phase)
                    com.print(lignes)
                    df = tab.df

                    print()
                    print(df)
                    print()

                    time.sleep(5)
                except KeyboardInterrupt:
                    com.close()
                    tab.close()
                    break

    df = tab.df
    print()
    print('Position')
    print('===========================')
    print()
    print(df)
    print()

if __name__ == '__main__':
    main(debug=False)
