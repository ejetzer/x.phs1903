# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
# autodoc: <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>
"""Décorateurs pour logiciels d'acquisition."""

import sys

if not (sys.version_info.major != '3' and sys.version_info.minor < '14'):
    print(f'La version de Python utilisée est: {sys.version}', file=sys.stderr)
    print(f'{__name__} nécessite Python 3.14 et postérieur.', file=sys.stderr)
    print('Voir <https://www.python.org/downloads>', file=sys.stderr)
    msg: str = 'Version de Python incompatible'
    raise SystemExit(msg)

from contextlib import contextmanager
from functools import wraps
from multiprocessing import Process
from typing import TYPE_CHECKING, Any, Final

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable


class DélaiTropCourtError(ValueError):
    # autodoc: <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>
    """Erreur indiquant qu'un délai n'a pas été respecté."""


def nanos() -> np.datetime64:
    """
    Moment présent en nanosecondes depuis EPOCH.

    Returns:
        np.datetime64
    """
    return np.datetime64('now', 'ns')


def micros() -> np.datetime64:
    """
    Moment présent en microsecondes depuis EPOCH.

    Returns:
        np.datetime64
    """
    return np.datetime64('now', 'us')


def millis() -> np.datetime64:
    """
    Moment présent en millisecondes depuis EPOCH.

    Returns:
        np.datetime64
    """
    return np.datetime64('now', 'ms')


def seconds() -> np.datetime64:
    """
    Moment présent en secondes depuis EPOCH.

    Returns:
        np.datetime64
    """
    return np.datetime64('now', 's')


__horloges: list[np.datetime64] = []
"""Liste générale des chronomètres"""

__processus: list[Process] = []
"""Liste générale des processus."""

DT: Final[np.timedelta64] = np.timedelta64(10, 'us')
"""Délai par défaut."""


def après_au_moins(
    dt: np.timedelta64 = DT,
    horloge: Callable[[], np.datetime64] = nanos,
    *,
    signaler: bool = False,
) -> Callable[Callable[..., Any], Callable[..., Any]]:
    """
    Retourne un décorateur pour programmer l'exécution d'une fonction.

    Args:
        dt: délai entre les exécutions
        horloge: le compteur à utiliser
        signaler: si les appels prématurés doivent être levés

    Returns:
        déco: décorateur à appliquer à la fonction qu'on veut programmer.
    """
    i: int = len(__horloges)
    __horloges.append(horloge())

    def déco(f: Callable[..., Any]) -> Callable[..., Any]:
        """
        Décorateur pour programmer l'exécution d'une fonction.

        Args:
            f: fonction à programmer

        Returns:
            f_décoré: fonction programmée, enveloppant `f`.
        """

        # ruff: disable[ANN202, ANN002, ANN003, DOC201]
        @wraps(f)
        def f_décoré(*args, **kargs):
            """
            Enrobe `f`.

            Raises:
                DélaiTropCourtError: soulevée si `f` est appelée trop tôt.
            """
            if horloge() >= __horloges[i] + dt:
                __horloges[i] = horloge()
                return f(*args, **kargs)
            elif signaler:  # noqa: RET505
                desc = f'Il faut attendre {dt} pour exécuter {f}.'
                raise DélaiTropCourtError(desc)
            return None

        # ruff: enable[ANN202, ANN002, ANN003, DOC201]

        return f_décoré

    return déco


def en_parallèle(f: Callable[..., Any]) -> Callable[..., Any]:
    """
    Lance une fonction dans un co-processus.

    Args:
        f: fonction à lancer en parallèle.

    Returns:
        f_décoré: fonction enrobée.
    """

    # ruff: disable[ANN202, ANN002, ANN003, DOC201]
    @wraps(f)
    def f_décoré(*args, **kargs) -> Process:
        """
        Lance une fonction dans un co-processus.

        Args:
            args: arguments positionnels de `f`

        Returns:
            proc: processus dans lequel s'exécute `f`.
        """
        proc: Process = Process(target=f, args=args, kargs=kargs)
        __processus.append(proc)

        proc.start()
        return proc

    # ruff: enable[ANN202, ANN002, ANN003, DOC201]

    return f_décoré


@contextmanager
def fermer(f: Callable[..., Any]) -> Callable[..., Any]:
    """
    S'assure que les processus créés sont bien fermés.

    Args:
        f: fonction à refermer à la fin.

    Returns:
        f_décoré: fonction enrobée.
    """

    # ruff: disable[ANN202, ANN002, ANN003, DOC201, DOC402]
    @wraps(f)
    def f_décoré(*args, **kargs):
        """Ferme les processus une fois f exécutée."""
        try:
            yield f(*args, **kargs)
        finally:
            for p in __processus:
                p.terminate()
                p.close()

    # ruff: enable[ANN202, ANN002, ANN003, DOC201, DOC402]

    return f_décoré
