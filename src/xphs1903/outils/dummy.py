# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Fonctions et classes de simulations simples."""

from typing import TYPE_CHECKING

import numpy as np

from .exceptions import NoiseTypeError

if TYPE_CHECKING:
    from collections.abc import Callable


def signal(
    *args: Callable,
    t_0: float = 0,
    dt: float = 0.01,
    noise: Callable | None | list[Callable] = None,
    bunch: int = 1,
) -> list[dict[str, float]]:
    """Génère un signal simulé dans le format du moniteur série Arduino.

    Parameters
    ----------------
    t_0: float = 0
        Valeur initiale de variable dépendante.
    dt: float = 0.01
        Espacement entre les valeurs.
    noise: Callable | None | list[Callable] = None
        Paramètres de bruit à ajouter aux données.

        Une liste de fonctions doit respecter ``len(args) == len(noise)``
        ou ``2 * len(args) == len(noise)``. Les fonctions ne se font
        transmettre aucun argument.
    bunch: int = 1
        Combien de lignes envoyer d'un coup.

    Yields
    ----------------
    yel: list[dict[str, float]]
        Une liste de :obj:`bunch` lignes.

    Raises
    ----------------
    NoiseTypeError(noise, args)
        Si :obj:`noise` n'est pas du bon type ou format.
    """  # noqa: DOC502
    if len(args) == 0:
        args = (np.sin,)

    _float = np.float128

    _0 = _float(0)
    t_noise = [lambda: _0 for x in args]
    if noise is None:
        noise = [lambda: _0 for x in args]
    elif callable(noise):
        noise = [noise for x in args]
    elif len(noise) == 2 * len(args):
        t_noise = noise[::2]
        noise = noise[1::2]
    elif len(noise) != len(args):
        raise NoiseTypeError(noise, args)

    t = _float(t_0)
    while True:
        yel = []
        for _ in range(bunch):
            res = {}
            for i, f in enumerate(args):
                tn = t_noise[i]()
                fn = noise[i]()
                res |= {f"t_{i}": t + tn, f"f_{i}": f(t + tn) + fn}
            yel.append(res)
            t += dt
        yield yel


def noise(
    *,
    d: int = 1,
    incert: float = 0.001,
    mean: float = 0,
    seed: int | None = None,
) -> list[Callable]:
    """Bruit normal pour :func:`signal`.

    Parameters
    ----------------
    d: int = 1
        Nombre de dimensions.
    incert: float = 0.001
        Écart-type.
    mean: float = 0
        Valeur moyenne.
    seed: int | None = None
        Valeur de départ pour le générateur de nombres aléatoires.

    Returns
    ----------------
    list[Callable]
        Une liste de fonctions de génération de bruit normal.
    """
    gna = np.random.default_rng(seed=seed)

    def f() -> np.number:
        return gna.normal(mean, incert)

    return [f for _ in range(d)]


def concat(*args: Callable) -> list[dict[str, float]]:
    """Concatène des itérateurs de lignes de données.

    Yields
    ----------------
    list[dict[str, float]]
        Les groupes de lignes des itérateurs.
    """
    for ls in zip(*args, strict=True):
        yel = []
        for l_ in ls:
            yel += l_
        yield yel


__all__ = ["noise", "signal"]
