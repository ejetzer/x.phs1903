# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
# https://stackoverflow.com/a/57387909
# https://stackoverflow.com/a/63967448
"""Fonctions de contrôle ordiné."""

import logging
import queue
import threading
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

__logger = logging.getLogger(__name__)
"""Journal de débogage interne du module.

Utile pour le débogage, ne devrait être obtenu qu'avec
:func:`logging.getLogger`.
"""

__logger.addHandler(logging.NullHandler())

if TYPE_CHECKING:
    from types import TracebackType
    from typing import Self

type TraceurSerie = list[dict[str, float]]
type IterTraceurSerie = iter[dict[str, float]]


class Tableau:
    __logger = logging.getLogger(f'{__name__}.Tableau')
    """Journal de débogage pour les objets de classe Tableau."""

    __logger.addHandler(logging.NullHandler())

    def __init__(self, _iter: IterTraceurSerie) -> None:
        self.__iter: IterTraceurSerie = _iter
        self.__df: pd.DataFrame = pd.DataFrame()
        self.__buffer: list[pd.Series] = []
        self.__thread_consume: threading.Thread = threading.Thread(target=self.__run_consume)
        self.__thread_update: threading.Thread = threading.Thread(target=self.__run_update)
        self.__arret: threading.Event = threading.Event()
        self.__loquet_df: threading.Lock = threading.Lock()
        self.__loquet_buffer: threading.Lock = threading.Lock()

    def __run_consume(self) -> None:
        self.__logger.debug('%s', self.__iter)

        while not self.__arret.is_set():
            ser = next(self.__iter)

            if ser is None:
                continue

            with self.__loquet_buffer:
                self.__buffer.append(pd.Series(ser).to_frame().T)

        self.__logger.debug('len(buffer) = %s', len(self.__buffer))

    def __run_update(self) -> None:
        while not self.__arret.is_set():
            with self.__loquet_buffer, self.__loquet_df:
                self.__df = pd.concat([self.__df] + self.__buffer).reset_index(drop=True)

    def close(self) -> None:
        self.__arret.set()
        self.__thread_consume.join()
        self.__thread_update.join()

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> pd.DataFrame:
        return self.df

    def start(self):
        self.__thread_consume.start()
        self.__thread_update.start()

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        self.close()
        return False  # Re-raise the exception please

    @property
    def df(self) -> pd.DataFrame:
        with self.__loquet_df:
            return self.__df.copy()


def aléatoire(
    *, n: int = 10, incert: float = 0.001, seed: int = 1903
) -> TraceurSerie:
    gna = np.random.default_rng(seed=seed)
    ts: np.ndarray = np.arange(n) + gna.normal(0, incert, n)
    xs: np.ndarray = np.arange(n) + gna.normal(0, incert, n)
    ys: np.ndarray = (np.arange(n) + gna.normal(0, incert, n)) ** 2
    zs: np.ndarray = (np.arange(n) + gna.normal(0, incert, n)) ** 2
    lignes: TraceurSerie = [
        {'t': t, 'x': x, 'y': y, 'z': z}
        for t, x, y, z in zip(ts, xs, ys, zs, strict=True)
    ]
    return lignes


def sinus(
    *, n: int = 10, incert: float = 0.001, seed: int = 1903, phase: int = 0
) -> TraceurSerie:
    gna = np.random.default_rng(seed=seed)
    ts: np.ndarray = np.arange(phase, phase + n) + gna.normal(0, incert, n)
    xs: np.ndarray = 2 * np.sin(np.arange(phase, phase + n)) + gna.normal(
        0, incert, n
    ) + 2.5
    ys: np.ndarray = 2 * np.cos(np.arange(phase, phase + n)) + gna.normal(
        0, incert, n
    ) + 2.5
    lignes: TraceurSerie = [
        {'t': t, 'x': x, 'y': y} for t, x, y in zip(ts, xs, ys, strict=True)
    ]
    return lignes


def main(*, debug: bool = True) -> None:
    import time  # noqa: PLC0415

    from .serial import LigneSerie  # noqa: PLC0415

    if debug:
        from .logging import config, DEBUG
        config(__name__, level=DEBUG)

    n = 50
    phase = 0
    lignes = sinus(n=n, phase=phase)

    with LigneSerie() as com:
        __logger.debug('%s', com)
        com.print(lignes)

        with Tableau(com.parse()) as tab:
            __logger.debug('%s', tab)

            while True:
                phase += n
                lignes = sinus(n=n, phase=phase)
                com.print(lignes)
                df = tab.df

                print()
                print(df)
                print()

                time.sleep(5)

            tab.close()

        com.close()

    df = tab.df
    print()
    print('Position')
    print('===========================')
    print()
    print(df)
    print()


if __name__ == '__main__':
    main(debug=False)
