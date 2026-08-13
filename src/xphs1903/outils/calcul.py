# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Utilitaires de calcul en parallèle."""

import logging
import typing
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor

import numpy as np
import pandas as pd

if typing.TYPE_CHECKING:
    from types import TracebackType
    from typing import Final, Self

    from .acq import Tableau

__logger = logging.getLogger(__name__)
"""Journal de débogage interne du module.

Utile pour le débogage, ne devrait être obtenu qu'avec
:func:`logging.getLogger`.
"""

__logger.addHandler(logging.NullHandler())

type FonctionCalcul = Callable[pd.DataFrame, pd.DataFrame]


class Calcul:
    """Calcul pré-enregistré pour exécution en parallèle."""

    __logger = logging.getLogger(f'{__name__}.Calcul')
    """Journal de débogage pour les objets de classe Calcul."""

    __logger.addHandler(logging.NullHandler())

    def __init__(
        self,
        fct: FonctionCalcul = lambda x: x,
        nom: str = '',
    ) -> None:
        """Initialisation du calcul."""
        self.__logger.debug('')
        self.__nom: Final[str] = str(nom)
        self.__fct: Final[FonctionCalcul] = fct
        self.__executor: ThreadPoolExecutor = ThreadPoolExecutor()
        self.__shutdown = False

    @property
    def nom(self) -> str:
        """Retourne le nom du calcul.

        Returns
        ---------------
        str
            Le nom du calcul.
        """
        self.__logger.debug('')
        return self.__nom

    @property
    def fct(self) -> Callable[pd.DataFrame, pd.DataFrame]:
        """Retourne la fonction sous-jacente.

        Returns
        ---------------
        Callable[pandas.DataFrame, pandas.DataFrame]
            La fonction sous-jacente.
        """
        self.__logger.debug('')
        return self.__fct

    def __call__(self, tab: Tableau) -> Future:
        """Appelle __run dans un fil parallèle.

        Returns
        ---------------
        Future
            Le processus en cours d'exécution.
        """
        self.__logger.debug('')
        if not self.__shutdown:
            future = self.__executor.submit(self.__run, tab)
        else:
            future = None
        self.__logger.debug('%s', future)
        return future

    def __repr__(self) -> str:
        """Représentation du calcul sous-jacent.

        Returns
        ---------------
        str
        """
        return repr(self.fct)

    def __run(self, tab: Tableau) -> pd.DataFrame:
        """Exécute self.fct avec l'argument tab.df.

        Returns
        ---------------
        pandas.DataFrame
            Résultat du calcul.
        """
        self.__logger.debug('')
        return self.fct(tab.df)

    def __enter__(self) -> None:
        """Ne fait rien."""
        self.__logger.debug('')
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        """Arrête les opérations de calcul.

        Returns
        ---------------
        False
            Soulève tout le temps l'erreur forçant la fin de l'exécution.
        """
        self.__logger.debug('')
        self.shutdown()
        return False  # Re-raise the exception please

    def shutdown(self) -> None:
        """Arrête les opérations de calcul."""
        self.__logger.debug('')
        self.__executor.shutdown(wait=False, cancel_futures=True)
        self.__shutdown = True

    @property
    def pending(self) -> int:
        return self.__executor._work_queue.qsize()

    @property
    def running(self) -> int:
        return len(self.__executor._threads)

    @property
    def computing(self) -> bool:
        return self.pending + self.running > 0

    def __matmul__(self, other: Self) -> Self:
        """Compose un calcul par un autre.

        L'opérateur fonctionne ainsi:

        .. code:: python

            (f @ g)(x)

        est équivalent à

        .. code:: python

            f(g(x))


        Returns
        ---------------
        Calcul
            L'objet Calcul résultant.
        """
        self.__logger.debug('')
        if not isinstance(other, Calcul):
            return NotImplemented

        def fct(df: pd.DataFrame) -> pd.DataFrame:
            self.__logger.debug('')
            return self.fct(other.fct(df))

        return type(self)(fct, f'{self.nom} @ {other.nom}')

    def __add__(self, other: Self) -> Self:
        """Additionne le résultat d'un calcul à celui d'un autre.

        Returns
        ---------------
        Calcul
            L'objet Calcul résultant.
        """
        self.__logger.debug('')
        if not isinstance(other, Calcul):
            return NotImplemented

        def fct(df: pd.DataFrame) -> pd.DataFrame:
            return self.fct(df) + other.fct(df)

        return type(self)(fct)

    def __mul__(self, other: Self) -> Self:
        """Multiplie le résultat d'un calcul par celui d'un autre.

        Returns
        ---------------
        Calcul
            L'objet Calcul résultant.
        """
        self.__logger.debug('')
        if not isinstance(other, Calcul):
            return NotImplemented

        def fct(df: pd.DataFrame) -> pd.DataFrame:
            return self.fct(df) * other.fct(df)

        return type(self)(fct)

    def __sub__(self, other: Self) -> Self:
        """Soustrait le résultat d'un calcul d'un autre.

        Returns
        ---------------
        Calcul
            L'objet Calcul résultant.
        """
        self.__logger.debug('')
        if not isinstance(other, Calcul):
            return NotImplemented

        def fct(df: pd.DataFrame) -> pd.DataFrame:
            return self.fct(df) - other.fct(df)

        return type(self)(fct)


def _i(df: pd.DataFrame) -> pd.DataFrame:
    """Retourne df.

    Returns
    ---------------
    df: pandas.DataFrame
        Aucune action.
    """
    __logger.debug('')
    return df


class Identite(Calcul):
    """Identité."""

    def __init__(
        self, fct: FonctionCalcul = _i, nom: str = 'identite'
    ) -> None:
        """Initialisation du calcul."""
        super().__init__(fct, nom)


def _moyenne(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule la moyenne de chaque colonne de df.

    Returns
    ---------------
    res: pandas.DataFrame
        La moyenne.
    """
    __logger.debug('')
    res: pd.Series = df.aggregate('mean', 'index')
    res.name = 'moyenne'
    res: pd.DataFrame = res.to_frame()
    return res


class Moyenne(Calcul):
    """Calcul de la moyenne d'une distribution."""

    def __init__(
        self, fct: FonctionCalcul = _moyenne, nom: str = 'moyenne'
    ) -> None:
        """Initialisation du calcul."""
        super().__init__(fct, nom)


def _describe(df: pd.DataFrame) -> pd.DataFrame:
    """Décrit la distribution de df.

    Returns
    ---------------
    res: pandas.DataFrame
        La description du DataFrame.
    """
    __logger.debug('')
    try:
        res: pd.DataFrame = df.describe()
    except ValueError:
        # Probablement un DataFrame vide.
        return df

    return res


class Description(Calcul):
    """Description statistique de données."""

    def __init__(
        self, fct: FonctionCalcul = _describe, nom: str = 'description'
    ) -> None:
        """Initialisation du calcul."""
        super().__init__(fct, nom)


def _fft(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule la transformée de Fourier de df[1:] en fonction de df[0].

    Returns
    ---------------
    df.copy(): pandas.DataFrame
        Copie du résultat du calcul.
    """
    __logger.debug('')

    items = df.items()

    try:
        _, index = next(items)
    except StopIteration:
        return df

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
    """Calcul de la transformée de Fourier de signaux."""

    def __init__(self, fct: FonctionCalcul = _fft, nom: str = 'fft') -> None:
        """Initialisation du calcul."""
        super().__init__(fct, nom)


def _pics(df: pd.DataFrame) -> pd.DataFrame:
    """Trouve les pics dans les fonctions df[1:] de df[0].

    Returns
    ---------------
    df.copy(): pandas.DataFrame
        Copie du DataFrame contenant le résultat du calcul.
    """
    import scipy.signal  # noqa: PLC0415

    __logger.debug('')

    items = df.items()

    try:
        _, fs = next(items)
    except StopIteration:
        return df

    fs = fs.to_numpy()
    cols = [v.to_numpy() for _, v in items]
    pics = [scipy.signal.find_peaks(c) for c in cols]
    pics = [p for p, _ in pics]
    max_len = max(map(len, pics))
    dico = {
        str(num + 1): [cols[num][p] for p in pic]
        + [None for n in range(max_len - len(pic))]
        for num, pic in enumerate(pics)
    }
    dico |= {
        f'f{num + 1}': [fs[p] for p in pic]
        + [None for n in range(max_len - len(pic))]
        for num, pic in enumerate(pics)
    }
    df = pd.DataFrame(dico)

    return df.copy()


class Pics(Calcul):
    """Calcul des pics d'une fonction."""

    def __init__(self, fct: FonctionCalcul = _pics, nom: str = 'fft') -> None:
        """Initialisation du calcul."""
        super().__init__(fct, nom)


def _der(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule la dérivé de df[1:] en fonction de df[0].

    Returns
    ---------------
    df.copy(): pandas.DataFrame
        Une copie du DataFrame contenant les résultats du calcul.
    """
    __logger.debug('')
    items = df.items()

    try:
        _, index = next(items)
    except StopIteration:
        return df

    index = index.to_numpy()
    cols = [v.to_numpy() for _, v in items]
    ders = [np.gradient(col, index) for col in cols]
    dico = {'t': index} | {(col + 1): der for col, der in enumerate(ders)}
    df = pd.DataFrame(dico)
    return df.copy()


class Derivee(Calcul):
    """Calcul de la dérivée par approximation de premier degré."""

    def __init__(
        self, fct: FonctionCalcul = _der, nom: str = 'dérivée'
    ) -> None:
        """Initialisation du calcul."""
        super().__init__(fct, nom)


def window(
    win: str = 'boxcar', n: int = 100, **kargs: str | float
) -> type[Calcul]:
    """Retourne une sous-classe de Calcul décrivant une fenêtre.

    Returns
    ---------------
    Window : type[Calcul]
    """
    __logger.debug('')

    import scipy.signal.windows  # noqa: PLC0415

    win = scipy.signal.get_window(win, n, **kargs)
    __logger.debug('len(win) = %s', len(win))

    def fct(df: pd.DataFrame) -> pd.DataFrame:
        __logger.debug('')
        __logger.debug('df.size = %s', df.size)
        __logger.debug('win.size = %s', win.size)

        tail = df.tail(n)
        items = tail.items()

        try:
            _, index = next(items)
        except StopIteration:
            return df

        index = index.to_numpy()

        __logger.debug('len(index) = %s', len(index))

        cols = [v.to_numpy() for _, v in items]

        __logger.debug('len(<cols>) = %s', list(map(len, cols)))

        mask = win[: len(index)]

        __logger.debug('len(mask) = %s', len(mask))

        masked = [np.multiply(col, mask) for col in cols]
        dico = {'t': index} | {(col + 1): m for col, m in enumerate(masked)}
        df = pd.DataFrame(dico)
        return df.copy()

    class Window(Calcul):
        """Fenêtre à appliqué sur des données."""

        def __init__(
            self, fct: FonctionCalcul = fct, nom: str = f'{win}<{n}>'
        ) -> None:
            """Initialisation de la fenêtre."""
            super().__init__(fct, nom)

    return Window


def rectangle(n: int = 100) -> type[Calcul]:
    """Retourne un Calcul appliquant une fenêtre rectangulaire.

    Returns
    ----------------------
    type[Calcul]
        Une fenêtre rectangulaire de longueur n
    """
    __logger.debug('')
    return window('rect', n)


def main(*, debug: bool = False) -> None:
    """Démonstration de calculs en parallèle."""
    from .acq import Tableau, sinus  # noqa: PLC0415
    from .serial import LigneSerie  # noqa: PLC0415

    if debug:
        from .logging import DEBUG, config  # noqa: PLC0415

        config(__name__, level=DEBUG)

    n = 50
    phase = 0
    lignes = sinus(n=50, phase=phase)

    fenetre: Calcul = rectangle(50)()
    calcul_fft: Calcul = FFT() @ fenetre
    calcul_moyenne: Calcul = Description() @ fenetre
    calcul_pics: Calcul = Pics() @ calcul_fft

    with LigneSerie() as com:
        __logger.debug('%s', com)
        com.print(lignes)

        with Tableau(com.parse()) as tab:
            __logger.debug('%s', tab)

            pending_moy, pending_fft, res = None, None, None
            while True:
                phase += n
                lignes = sinus(n=n, phase=phase)
                com.print(lignes)

                fft_para, pending_fft = pending_fft, None
                if fft_para is None:
                    fft_para = calcul_pics(tab)

                moy_para, pending_moy = pending_moy, None
                if moy_para is None:
                    moy_para = calcul_moyenne(tab)

                print(f'FFT: {calcul_pics.running} calculs en cours, {calcul_pics.pending} en attente.')
                print(f'Moyenne: {calcul_moyenne.running} calculs en cours, {calcul_moyenne.pending} en attente.')

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
