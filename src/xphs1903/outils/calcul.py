# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Utilitaires de calcul en parallèle."""

import functools
import itertools
import logging
import queue
import threading
import typing
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor

import numpy as np
import pandas as pd
import scipy

from .acq import Tableau as AcqTab
from .exceptions import WrongWindowTypeError
from .logging import WithLogger
from .serial import ArduinoNanoEvery, LigneSerie

if typing.TYPE_CHECKING:
    from types import TracebackType
    from typing import Final, Self

    from .acq import Tableau


class TableauCalcul(AcqTab):
    def __init__(self, ser: LigneSerie | None) -> None:
        self.checkin()
        super().__init__(ser)

        self.__sync_thread = threading.Thread(
            target=self.__syncing, name=type(self).__name__
        )
        self.__f_threads = {}
        self.__in_queues = {}
        self.__loquets = {}
        self.__results = {}
        self.__updates = {}
        self.__arret = threading.Event()
        self.__executor = ThreadPoolExecutor()

    def start(self, *, ser: LigneSerie | None = None) -> None:
        self.checkin()
        super().start(ser=ser)

        self.__sync_thread.start()
        for thread in self.__f_threads.values():
            thread.start()

    def close(self) -> None:
        self.checkin()
        self.__arret.set()
        for thread in self.__f_threads.values():
            thread.join()

        self.__sync_thread.join()
        self.__executor.shutdown()
        super().close()

    def __syncing(self) -> None:
        self.checkin()
        try:
            while not self.__arret.is_set():
                if self._updated.is_set():
                    self.checkin()
                    nouv = self.df
                    self._updated.clear()
                    for q in self.__in_queues.values():
                        q.put(nouv)
        except Exception as err:
            self.error('', exc_info=err)
        finally:
            if not self.__arret.is_set():
                self.__arret.set()

            for q in self.__in_queues.values():
                q.shutdown()

    def wrap(self, f: Callable) -> Callable:
        self.checkin()
        name = f.__name__
        self.__in_queues[name] = queue.Queue()
        self.__loquets[name] = threading.Lock()
        self.__results[name] = None
        self.__updates[name] = threading.Event()

        @functools.wraps(f)
        def func() -> None:
            self.checkin()

            self.debug('arret = %s', self.__arret)
            try:
                while not self.__arret.is_set():
                    entree = self.__in_queues[name].get()
                    self.debug('entree = %r', entree)
                    res = f(
                        entree, executor=self.__executor, logger=self.logger
                    )
                    self.__in_queues[name].task_done()

                    with self.__loquets[name]:
                        self.__results[name] = res
                    self.__updates[name].set()
            except Exception as err:
                self.error('', exc_info=err)
            finally:
                if not self.__arret.is_set():
                    self.__arret.set()

                for q in self.__in_queues.values():
                    q.shutdown()

        return func

    def register(self, f: Callable):
        self.checkin()
        self.__f_threads[f.__name__] = threading.Thread(
            target=self.wrap(f), name=f.__name__, daemon=True
        )

    def __getitem__(self, key: int | str) -> pd.DataFrame:
        self.checkin()
        if isinstance(key, int):
            return super().__getitem__(key)

        if not isinstance(key, str):
            raise TypeError

        return self.get(key)

    def get(
        self,
        key: str,
        *,
        default: Any = None,
        timeout: float | None = None,
        wait: bool = False,
    ):
        self.checkin()

        self.debug('wait = %s, timeout = %s', wait, timeout)
        self.debug('updates[%s] = %s', key, self.__updates[key])
        self.debug('threads[%s] = %s', key, self.__f_threads[key])
        if wait or timeout is not None:
            self.__updates[key].wait(timeout=timeout)

        if self.__updates[key].is_set():
            self.__updates[key].clear()

        res = self.__results.get(key, default)
        self.debug('res = %r', res)

        return res

    def wait(self) -> None:
        super().wait()

        while not all(map(queue.Queue.empty, self.__in_queues.values())):
            continue


def rfftfreq(t: np.ndarray) -> np.ndarray:
    dt = np.mean(t[1:] - t[:-1])
    return np.fft.rfftfreq(len(t), dt)


def rfft(x: np.ndarray) -> np.ndarray:
    res = np.fft.rfft(x)
    return np.real(np.sqrt(np.multiply(res, res.conjugate())))


def fft(
    df: pd.DataFrame,
    *,
    executor: Executor | None = None,
    logger: logging.Logger | None = None,
) -> pd.DataFrame:
    if logger is None:
        logger = logging.getLogger(f'{__name__}.fft')

    logger.debug('df =\n%r', df)
    ts, xs = zip(
        *(
            (df.iloc[:, i].to_numpy(), df.iloc[:, i + 1].to_numpy())
            for i in range(0, len(df.columns), 2)
        )
    )

    logger.debug('len(ts), len(xs) = %s, %s', len(ts), len(xs))

    if executor is not None:
        results = list(
            itertools.chain(executor.map(rfftfreq, ts), executor.map(rfft, xs))
        )
    else:
        results = list(
            itertools.chain([rfftfreq(t) for t in ts], [rfft(x) for x in xs])
        )

    logger.debug('results = %r', results)

    num = len(df.columns) // 2
    cols = [
        pd.Series(r)
        for r in itertools.chain(*zip(results[:num], results[num:]))
    ]
    logger.debug('len(cols) = %s', len(cols))
    return pd.concat(cols, axis='columns')


def parallellize(f: Callable[[pd.DataFrame], pd.DataFrame]) -> Callable:

    @wraps(f)
    def fct(
        df: pd.DataFrame,
        *,
        executor: Executor | None = None,
        logger: logging.Logger | None = None,
    ) -> pd.DataFrame:
        if logger is None:
            logger = logging.getLogger(f'{__name__}.{f.__name__}')

        logger.debug('df.size = %s', df.size)
        ts, xs = zip(
            *(
                (df.iloc[:, i].to_numpy(), df.iloc[:, i + 1].to_numpy())
                for i in range(0, len(df.columns), 2)
            )
        )

        logger.debug('len(ts), len(xs) = %s, %s', len(ts), len(xs))

        if executor is not None:
            results = list(executor.map(f, ts, xs))
        else:
            results = [f(t, x) for t, x in zip(ts, xs)]

        logger.debug('results = %r', results)

        cols = [pd.Series(r) for r in itertools.chain(*zip(ts, results))]
        logger.debug('len(cols) = %s', len(cols))
        return pd.concat(cols, axis='columns')

    return fct


def no_op(*, debug: bool = False) -> None:
    import time

    with LigneSerie as com:
        with TableauCalcul(com) as tab:
            time.sleep(1)


def echocalc(*, debug: bool = False) -> None:
    import time  # noqa: PLC0415

    from .acq import sinus

    lignes = sinus()
    with LigneSerie() as com:
        tab = TableauCalcul(com)
        tab.register(fft)

        if debug:
            tab.log_to_stderr()
            tab.setLevel('debug')

        with tab as tab:
            while True:
                try:
                    com.print(next(lignes))
                    print(tab.get('fft', timeout=5))
                except KeyboardInterrupt:
                    break


def ardcalc(*, debug: bool = False) -> None:
    import time  # noqa: PLC0415

    with ArduinoNanoEvery(baudrate=9600) as com:
        tab = TableauCalcul(com)
        tab.register(fft)
        with tab:
            while True:
                try:
                    print(tab.get('fft', timeout=5))
                except KeyboardInterrupt:
                    break
