# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Utilitaires de calcul en parallèle."""

import functools
import itertools
import logging
import queue
import threading
import time
import typing
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

from .acq import Tableau as AcqTab
from .acq import sinus
from .exceptions import InvalidCalculKeyTypeError
from .logging import DEBUG, basicConfig, info, suppress
from .serial import ArduinoNanoEvery, LigneSerie

if typing.TYPE_CHECKING:
    from collections.abc import Callable
    from concurrent.futures import Executor


class TableauCalcul(AcqTab):
    """Tableau de calculs en direct."""

    def __init__(self, ser: LigneSerie | None) -> None:
        """Configure les fils d'exécution."""
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
        """Démarre les fils d'exécution."""
        self.checkin()
        super().start(ser=ser)

        self.__sync_thread.start()
        for thread in self.__f_threads.values():
            thread.start()

    def close(self) -> None:
        """Ferme les fils d'exécution."""
        self.checkin()
        self.__arret.set()
        for thread in self.__f_threads.values():
            thread.join()

        self.__sync_thread.join()
        self.__executor.shutdown()
        super().close()

    def __syncing(self) -> None:
        self.checkin()

        def final() -> None:
            if not self.__arret.is_set():
                self.__arret.set()

            for q in self.__in_queues.values():
                q.shutdown()

        with suppress(self, Exception, final):
            while not self.__arret.is_set():
                if self._updated.is_set():
                    self.checkin()
                    nouv = self.df
                    self._updated.clear()
                    for q in self.__in_queues.values():
                        q.put(nouv)

    def wrap(self, f: Callable) -> Callable:
        """Suppresse les erreurs levées par f et les note.

        Returns
        ---------------------------
        func: Callable
            Fonction enveloppant f.
        """
        self.checkin()
        name = f.__name__
        self.__in_queues[name] = queue.Queue()
        self.__loquets[name] = threading.Lock()
        self.__results[name] = None
        self.__updates[name] = threading.Event()

        def final() -> None:
            if not self.__arret.is_set():
                self.__arret.set()

            for q in self.__in_queues.values():
                q.shutdown()

        @functools.wraps(f)
        def func() -> None:
            self.checkin()

            self.debug("arret = %s", self.__arret)
            with suppress(self, Exception, final=final):
                while not self.__arret.is_set():
                    entree = self.__in_queues[name].get()
                    self.debug("entree = %r", entree)
                    res = f(
                        entree, executor=self.__executor, logger=self.logger
                    )
                    self.__in_queues[name].task_done()

                    with self.__loquets[name]:
                        self.__results[name] = res
                    self.__updates[name].set()

        return func

    def register(self, f: Callable) -> None:
        """Ajoute une fonction à calculer."""
        self.checkin()
        self.__f_threads[f.__name__] = threading.Thread(
            target=self.wrap(f), name=f.__name__, daemon=True
        )

    def __getitem__(self, key: int | str) -> pd.DataFrame:
        """Obtiens les derniers résultats du calcul key sans attente.

        Returns
        ---------------------------
        Le résultat du calcul ou les données brutes.

        Raises
        ---------------------------
        InvalidCalculKeyTypeError
            Si la clé key n'est ni un int ni une str.
        """  # noqa: DOC502
        self.checkin()
        if isinstance(key, int):
            return super().__getitem__(key)

        if not isinstance(key, str):
            raise InvalidCalculKeyTypeError(key)

        return self.get(key)

    def get(
        self,
        key: str,
        *,
        default: np.ndarray | None = None,
        timeout: float | None = None,
        wait: bool = False,
    ) -> np.ndarray:
        """Obtiens les derniers résultats du calcul.

        Returns
        ---------------------------
        Les derniers résultats du calcul.
        """
        self.checkin()

        self.debug("wait = %s, timeout = %s", wait, timeout)
        self.debug("updates[%s] = %s", key, self.__updates[key])
        self.debug("threads[%s] = %s", key, self.__f_threads[key])
        if wait or timeout is not None:
            self.__updates[key].wait(timeout=timeout)

        if self.__updates[key].is_set():
            self.__updates[key].clear()

        res = self.__results.get(key, default)
        self.debug("res = %r", res)

        return res

    def wait(self) -> None:
        """Attends la fin de l'exécution des calculs."""
        super().wait()

        while not all(map(queue.Queue.empty, self.__in_queues.values())):
            continue


def rfftfreq(t: np.ndarray) -> np.ndarray:
    """Calcule les fréquences du domaine d'une transformée de Fourier.

    Returns
    ---------------------------
    Les fréquences positives réelles.
    """
    dt = np.mean(t[1:] - t[:-1])
    return np.fft.rfftfreq(len(t), dt)


def rfft(x: np.ndarray) -> np.ndarray:
    """Calcule la transformée de Fourier d'une colonne.

    Returns
    ---------------------------
    La transformée de Fourier discrète réelle.
    """
    res = np.fft.rfft(x)
    return np.real(np.sqrt(np.multiply(res, res.conjugate())))


def fft(
    df: pd.DataFrame,
    *,
    executor: Executor | None = None,
    logger: logging.Logger | None = None,
) -> pd.DataFrame:
    """Calcule la transformée de Fourier.

    Returns
    ---------------------------
    pd.DataFrame
        La transformée de Fourier calculée pour chaque colonne.
    """
    if logger is None:
        logger = logging.getLogger(f"{__name__}.fft")

    logger.debug("df =\n%r", df)
    ts, xs = zip(
        *(
            (df.iloc[:, i].to_numpy(), df.iloc[:, i + 1].to_numpy())
            for i in range(0, len(df.columns), 2)
        ),
        strict=True,
    )

    logger.debug("len(ts), len(xs) = %s, %s", len(ts), len(xs))

    if executor is not None:
        results = list(
            itertools.chain(executor.map(rfftfreq, ts), executor.map(rfft, xs))
        )
    else:
        results = list(
            itertools.chain([rfftfreq(t) for t in ts], [rfft(x) for x in xs])
        )

    logger.debug("results = %r", results)

    num = len(df.columns) // 2
    cols = [
        pd.Series(r)
        for r in itertools.chain(
            *zip(results[:num], results[num:], strict=True)
        )
    ]
    logger.debug("len(cols) = %s", len(cols))
    return pd.concat(cols, axis="columns")


def parallellize(f: Callable[[pd.DataFrame], pd.DataFrame]) -> Callable:
    """Parallélise l'exécution d'une fonction de calculs.

    Returns
    ---------------------------
    fct: Callable
        Fonction enveloppant l'exécution en parallèle de f.
    """

    @functools.wraps(f)
    def fct(
        df: pd.DataFrame,
        *,
        executor: Executor | None = None,
        logger: logging.Logger | None = None,
    ) -> pd.DataFrame:
        if logger is None:
            logger = logging.getLogger(f"{__name__}.{f.__name__}")

        logger.debug("df.size = %s", df.size)
        ts, xs = zip(
            *(
                (df.iloc[:, i].to_numpy(), df.iloc[:, i + 1].to_numpy())
                for i in range(0, len(df.columns), 2)
            ),
            strict=True,
        )

        logger.debug("len(ts), len(xs) = %s, %s", len(ts), len(xs))

        if executor is not None:
            results = list(executor.map(f, ts, xs))
        else:
            results = map(f, ts, xs, strict=True)

        logger.debug("results = %r", results)

        cols = [
            pd.Series(r)
            for r in itertools.chain(*zip(ts, results, strict=True))
        ]
        logger.debug("len(cols) = %s", len(cols))
        return pd.concat(cols, axis="columns")

    return fct


def no_op(*, debug: bool = False) -> None:
    """Test d'exécution minimale."""
    if debug:
        basicConfig(DEBUG)

    with LigneSerie as com, TableauCalcul(com) as tab:
        if debug:
            com.log_to_stderr()
            com.setLevel(DEBUG)
            tab.log_to_stderr()
            tab.setLevel(DEBUG)

        info("Connexion %r établie.", com)
        info("Tableau %r créé.", tab)

        time.sleep(1)

    info("Fin.")


def echocalc(*, debug: bool = False) -> None:
    """Démonstration de calculs en direct."""
    if debug:
        basicConfig(DEBUG)

    lignes = sinus()
    info("Données factices crées: %r.", lignes)

    with LigneSerie() as com:
        info("Connexion %r établie.", com)

        tab = TableauCalcul(com)
        info("Tableau %r créé.", tab)

        tab.register(fft)
        info("Calcul %r enregistré.", tab["fft"])

        with tab:
            while True:
                try:
                    com.print(next(lignes))
                    info("Nouvelles données transmises.")
                    print(tab.get("fft", timeout=5))
                    print()
                    print("^C pour quitter.")
                except KeyboardInterrupt:
                    break

        info("Fin.")


def ardcalc(*, debug: bool = False) -> None:
    """Démonstration de calculs en direct."""
    if debug:
        basicConfig(DEBUG)

    with ArduinoNanoEvery(baudrate=9600) as com:
        info("Connexion %r établie.", com)

        tab = TableauCalcul(com)
        info("Tableau %r créé.", tab)

        tab.register(fft)
        info("Calcul %r enregistré.", "fft")

        with tab:
            while True:
                try:
                    print(tab.get("fft", timeout=5))
                    print()
                    print("^C pour quitter.")
                except KeyboardInterrupt:
                    break

    info("Fin.")


__all__ = ["TableauCalcul"]
