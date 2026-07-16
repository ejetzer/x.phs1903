from concurrent.futures import ThreadPoolExecutor, Future
import pandas as pd
from typing import Callable, Final
import logging
import numpy as np

__logger = logging.getLogger(__name__)
"""Journal de débogage interne du module.

Utile pour le débogage, ne devrait être obtenu qu'avec
:func:`logging.getLogger`.
"""

__logger.addHandler(logging.NullHandler())

class Calcul:
    __logger = logging.getLogger(f'{__name__}.Calcul')
    """Journal de débogage pour les objets de classe Calcul."""

    __logger.addHandler(logging.NullHandler())

    def __init__(
        self,
        fct: Callable[pd.DataFrame, pd.DataFrame] = lambda x: x,
        nom: str = ''
    ) -> None:
        self.__nom: Final[str] = str(nom)
        self.fct: Final[Callable[pd.DataFrame, pd.DataFrame]] = fct
        self.__executor: ThreadPoolExecutor = ThreadPoolExecutor()

    def __call__(self, df: pd.DataFrame) -> Future:
        future = self.__executor.submit(self.__run, df.copy())
        return future

    def __run(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.fct(df)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.__excutor.shutdown(wait=True, cancel_futures=True)
        return False

    def __matmul__(self, other: Self) -> Self:
        if not isinstance(other, Calcul):
            return NotImplemented

        def fct(df: pd.DataFrame) -> pd.DataFrame:
            return self.fct(other.fct(df))

        return type(self)(fct)

    def __rmatmul__(self, other: Self) -> Self:
        if not isinstance(other, Calcul):
            return NotImplemented

        def fct(df: pd.DataFrame) -> pd.DataFrame:
            return other.fct(self.fct(df))

        return type(self)(fct)

    def __add__(self, other: Self) -> Self:
        if not isinstance(other, Calcul):
            return NotImplemented

        def fct(df: pd.DataFrame) -> pd.DataFrame:
            return self.fct(df) + other.fct(df)

        return type(self)(fct)

    def __mul__(self, other: Self) -> Self:
        if not isinstance(other, Calcul):
            return NotImplemented

        def fct(df: pd.DataFrame) -> pd.DataFrame:
            return self.fct(df) * other.fct(df)

        return type(self)(fct)

    def __sub__(self, other: Self) -> Self:
        if not isinstance(other, Calcul):
            return NotImplemented

        def fct(df: pd.DataFrame) -> pd.DataFrame:
            return self.fct(df) - other.fct(df)

        return type(self)(fct)

def _I(df: pd.DataFrame) -> pd.DataFrame:
    return df

class Identite(Calcul):

    def __init__(self, fct=_I, nom='identite'):
        super().__init__(fct, nom)

def _moyenne(df: pd.DataFrame) -> pd.DataFrame:
    res: pd.Series = df.aggregate('mean', 'index')
    res.name = 'moyenne'
    res: pd.DataFrame = res.to_frame()
    return res

class Moyenne(Calcul):

    def __init__(self, fct=_moyenne, nom='moyenne'):
        super().__init__(fct, nom)

def _fft(df: pd.DataFrame) -> pd.DataFrame:
    items = df.items()
    _, index = next(items)
    index = index.to_numpy()
    dt = np.mean(index[1:] - index[:-1])
    cols = [v.to_numpy() for _, v in items]
    ffts = [np.fft.rfft(col) for col in cols]
    ffts = [np.multiply(fft, fft.conjugate()) for fft in ffts]
    ffts = [np.sqrt(fft.real) for fft in ffts]
    fs = np.fft.rfftfreq(len(index), dt)
    dico = {'f': fs} | {(col+1): fft for col, fft in enumerate(ffts)}
    df = pd.DataFrame(dico)
    return df.copy()

class FFT(Calcul):

    def __init__(self, fct=_fft, nom='fft'):
        super().__init__(fct, nom)


def _der(df: pd.DataFrame) -> pd.DataFrame:
    items = df.items()
    _, index = next(items)
    index = index.to_numpy()
    cols = [v.to_numpy() for _, v in items]
    ders = [np.gradient(col, index) for col in cols]
    dico = {'t': index} | {(col+1): der for col, der in enumerate(ders)}
    df = pd.DataFrame(dico)
    return df.copy()

class Derivee(Calcul):

    def __init__(self, fct=_der, nom='dérivée'):
        super().__init__(fct, nom)


def main(*, debug: bool = False) -> None:
    from .serial import LigneSerie
    from .acq import Tableau, aléatoire, sinus
    import numpy as np

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
    lignes = sinus(N=50, phase=phase)

    calcul_fft: Calcul = FFT()

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

                    fft_para = calcul_fft(df)

                    try:
                        res = fft_para.result(timeout=10)
                    except TimeoutError:
                        continue
                    except KeyboardInterrupt:
                        raise
                    else:
                        print()
                        print(fft_para.result())
                        print()

                except KeyboardInterrupt:
                    com.close()
                    tab.close()
                    break


if __name__ == '__main__':
    main(debug=False)
