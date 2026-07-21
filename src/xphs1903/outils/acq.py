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
        self.__thread: threading.Thread = threading.Thread(target=self.__run)
        self.__queue: queue.Queue = queue.Queue()
        self.__arret: threading.Event = threading.Event()

    def __run(self) -> None:
        self.__logger.debug('%s', self.__iter)

        for ser in self.__iter:
            if self.__arret.is_set():
                break

            try:
                self.__queue.put(pd.Series(ser).to_frame().T)
            except queue.ShutDown as err:
                self.__logger.info('%s', self.__queue, exc_info=err)
                break

        self.__logger.debug('%s', self.__queue)

    def close(self) -> None:
        self.__arret.set()

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> pd.DataFrame:
        return self.df

    def __enter__(self) -> Self:
        self.__thread.start()
        self.__logger.debug('%s', self.__thread)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        self.close()
        self.__queue.shutdown()
        self.__thread.join()
        return False  # Re-raise the exception please

    def __consume(self) -> None:
        self.__logger.debug('')
        count: int = 0
        while True:
            try:
                item = self.__queue.get(timeout=0.001)
                self.__logger.debug('#%s %s', count, type(item))
            except queue.Empty as err:
                self.__logger.debug(
                    '#%s %s', count, self.__queue, exc_info=err
                )
                break
            except queue.ShutDown as err:
                self.__logger.debug(
                    '#%s %s', count, self.__queue, exc_info=err
                )
                break
            else:
                self.__buffer.append(item)
                self.__queue.task_done()
                self.__logger.debug('#%s len(buffer) = %s', count, len(self.__buffer))
            finally:
                count += 1

    @property
    def df(self) -> pd.DataFrame:
        self.__logger.debug('')
        self.__consume()
        self.__logger.debug('len(buffer) = %s', len(self.__buffer))

        if len(self.__buffer) > 0:
            self.__logger.debug('len(buffer) = %s', len(self.__buffer))
            self.__logger.debug('%s %s', self.__df.size, self.__df.columns)

            self.__df = pd.concat([self.__df] + self.__buffer).reset_index(
                drop=True
            )
            self.__logger.debug('%s %s', self.__df.size, self.__df.columns)

            del self.__buffer[:]
            self.__logger.debug('%s', self.__buffer)

        self.__logger.debug('%s %s', self.__df.size, self.__df.columns)
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

    df = tab.df
    print()
    print('Position')
    print('===========================')
    print()
    print(df)
    print()


if __name__ == '__main__':
    main(debug=False)
