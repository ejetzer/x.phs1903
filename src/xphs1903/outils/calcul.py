# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
import logging
import typing
import functools
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor

import numpy as np
import pandas as pd

if typing.TYPE_CHECKING:
    from types import TracebackType
    from typing import Final, Self

__logger = logging.getLogger(__name__)
"""Journal de débogage interne du module.

Utile pour le débogage, ne devrait être obtenu qu'avec
:func:`logging.getLogger`.
"""

__logger.addHandler(logging.NullHandler())

type FonctionCalcul = Callable[pd.DataFrame, pd.DataFrame]


class Calcul:
    __logger = logging.getLogger(f'{__name__}.Calcul')
    """Journal de débogage pour les objets de classe Calcul."""

    __logger.addHandler(logging.NullHandler())

    def __init__(
        self,
        fct: FonctionCalcul = lambda x: x,
        nom: str = '',
    ) -> None:
        self.__logger.debug('')
        self.__nom: Final[str] = str(nom)
        self.__fct: Final[FonctionCalcul] = fct
        self.__executor: ThreadPoolExecutor = ThreadPoolExecutor()

    @property
    def nom(self):
        self.__logger.debug('')
        return self.__nom

    @property
    def fct(self):
        self.__logger.debug('')
        return self.__fct

    def __call__(self, df: pd.DataFrame) -> Future:
        self.__logger.debug('')
        future = self.__executor.submit(self.__run, df.copy())
        self.__logger.debug('%s', future)
        return future

    def __run(self, df: pd.DataFrame) -> pd.DataFrame:
        self.__logger.debug('')
        return self.fct(df)

    def __enter__(self) -> None:
        self.__logger.debug('')
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        self.__logger.debug('')
        self.__excutor.shutdown(wait=True, cancel_futures=True)
        return False  # Re-raise the exception please

    def shutdown(self) -> None:
        self.__logger.debug('')
        self.__executor.shutdown(wait=True, cancel_futures=True)

    def __matmul__(self, other: Self) -> Self:
        self.__logger.debug('')
        if not isinstance(other, Calcul):
            return NotImplemented

        def fct(df: pd.DataFrame) -> pd.DataFrame:
            self.__logger.debug('')
            return self.fct(other.fct(df))

        return type(self)(fct, f'{self.nom} @ {other.nom}')

    def __add__(self, other: Self) -> Self:
        self.__logger.debug('')
        if not isinstance(other, Calcul):
            return NotImplemented

        def fct(df: pd.DataFrame) -> pd.DataFrame:
            return self.fct(df) + other.fct(df)

        return type(self)(fct)

    def __mul__(self, other: Self) -> Self:
        self.__logger.debug('')
        if not isinstance(other, Calcul):
            return NotImplemented

        def fct(df: pd.DataFrame) -> pd.DataFrame:
            return self.fct(df) * other.fct(df)

        return type(self)(fct)

    def __sub__(self, other: Self) -> Self:
        self.__logger.debug('')
        if not isinstance(other, Calcul):
            return NotImplemented

        def fct(df: pd.DataFrame) -> pd.DataFrame:
            return self.fct(df) - other.fct(df)

        return type(self)(fct)


def _i(df: pd.DataFrame) -> pd.DataFrame:
    __logger.debug('')
    return df


class Identite(Calcul):
    def __init__(
        self, fct: FonctionCalcul = _i, nom: str = 'identite'
    ) -> None:
        super().__init__(fct, nom)


def _moyenne(df: pd.DataFrame) -> pd.DataFrame:
    __logger.debug('')
    res: pd.Series = df.aggregate('mean', 'index')
    res.name = 'moyenne'
    res: pd.DataFrame = res.to_frame()
    return res


class Moyenne(Calcul):
    def __init__(
        self, fct: FonctionCalcul = _moyenne, nom: str = 'moyenne'
    ) -> None:
        super().__init__(fct, nom)


def _fft(df: pd.DataFrame) -> pd.DataFrame:
    __logger.debug('')

    items = df.items()
    _, index = next(items)
    index = index.to_numpy()
    index = np.subtract(index, index[0])
    __logger.debug('index[0] = %s', index[0])
    __logger.debug('index[-1] = %s', index[-1])
    __logger.debug('len(index) = %s', len(index))

    dt = np.mean(np.subtract(index[1:], index[:-1]))
    __logger.debug('dt = %s', dt)

    cols = [v.to_numpy() for _, v in items]
    ffts = [np.fft.rfft(col) for col in cols]
    ffts = [np.multiply(fft, fft.conjugate()) for fft in ffts]
    ffts = [np.sqrt(fft.real) for fft in ffts]
    fs = np.fft.rfftfreq(len(index), dt)
    dico = {'f': fs} | {(col + 1): fft for col, fft in enumerate(ffts)}
    df = pd.DataFrame(dico)

    return df.copy()


class FFT(Calcul):
    def __init__(self, fct: FonctionCalcul = _fft, nom: str = 'fft') -> None:
        super().__init__(fct, nom)


def _der(df: pd.DataFrame) -> pd.DataFrame:
    __logger.debug('')
    items = df.items()
    _, index = next(items)
    index = index.to_numpy()
    cols = [v.to_numpy() for _, v in items]
    ders = [np.gradient(col, index) for col in cols]
    dico = {'t': index} | {(col + 1): der for col, der in enumerate(ders)}
    df = pd.DataFrame(dico)
    return df.copy()


class Derivee(Calcul):
    def __init__(
        self, fct: FonctionCalcul = _der, nom: str = 'dérivée'
    ) -> None:
        super().__init__(fct, nom)

def window(win: str = 'boxcar', n: int = 100, **kargs) -> type[Calcul]:
    __logger.debug('')

    import scipy.signal.windows

    win = scipy.signal.get_window(win, n, **kargs)
    __logger.debug('len(win) = %s', len(win))

    def fct(df: pd.DataFrame) -> pd.DataFrame:
        __logger.debug('')
        __logger.debug('df.size = %s', df.size)
        __logger.debug('win.size = %s', win.size)

        tail = df.tail(n)
        items = tail.items()
        _, index = next(items)
        index = index.to_numpy()

        __logger.debug('len(index) = %s', len(index))

        cols = [v.to_numpy() for _, v in items]

        __logger.debug('len(<cols>) = %s', list(map(len, cols)))

        mask = win[:len(index)]

        __logger.debug('len(mask) = %s', len(mask))

        masked = [np.multiply(col, mask) for col in cols]
        dico = {'t': index} | {(col+1): m for col, m in enumerate(masked)}
        df = pd.DataFrame(dico)
        return df.copy()

    class Window(Calcul):
        def __init__(
            self,
            fct: FonctionCalcul = fct,
            nom: str = f'{win}<{n}>'
        ):
            super().__init__(fct, nom)

    return Window

def rectangle(n: int = 100) -> type[Calcul]:
    __logger.debug('')
    return window('rect', n)

def main(*, debug: bool = False) -> None:
    from .acq import Tableau, sinus  # noqa: PLC0415
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
    lignes = sinus(n=50, phase=phase)

    fenetre: Calcul = rectangle(50)()
    calcul_fft: Calcul = FFT() @ fenetre
    calcul_moyenne: Calcul = Moyenne() @ fenetre


    with LigneSerie() as com:
        __logger.debug('%s', com)
        com.print(lignes)

        with Tableau(com.parse()) as tab:
            __logger.debug('%s', tab)

            pending_moy, pending_fft, res = None, None, None
            while True:
                print('.', end='')
                phase += n
                lignes = sinus(n=n, phase=phase)
                com.print(lignes)

                df = tab.df
                if pending_fft is None:
                    fft_para = calcul_fft(df)
                else:
                    fft_para, pending_fft = pending_fft, None

                if pending_moy is None:
                    moy_para = calcul_moyenne(df)
                else:
                    moy_para, pending_moy = pending_moy, None

                try:
                    res = fft_para.result(timeout=1e-9)
                except TimeoutError:
                    pending_fft = fft_para
                else:
                    print()
                    print(res)
                    print()

                try:
                    res = moy_para.result(timeout=1e-9)
                except TimeoutError:
                    pending_moy = moy_para
                else:
                    print()
                    print(res)
                    print()

            com.close()


if __name__ == '__main__':
    import sys

    debug = '--debug' in sys.argv
    main(debug=debug)
