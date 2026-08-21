# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Définitions d'execptions et erreurs précises."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any


class WrongSerialInputTypeError(TypeError):
    """Entrée fournie du mauvais type ou format."""

    def __init__(self, obj: Any) -> None:  # noqa: ANN401
        """Crée le message d'erreur.

        Parameters
        ----------------
        obj: Any
            L'objet du mauvais type.
        """
        msg = f'Expected str or list[dict] but got {type(obj)}.'
        super().__init__(msg)


class ParsableArduinoSerialDataError(ValueError):
    """Données reçues non-interprétables."""

    def __init__(self, data: str) -> None:
        """Crée le message d'erreur.

        Parameters
        ----------------
        data: str
            Les données invalides.
        """
        msg = (
            'Expected data of format '
            "'t:val\tf:val[...]' but "
            f'got {data!r} instead.'
        )
        super().__init__(msg)


class NoiseTypeError(TypeError, ValueError):
    """Mauvais type ou format pour une définition de bruit sur un signal."""

    def __init__(self, noise: Any, args: tuple[Callable]) -> None:  # noqa: ANN401
        """Crée le message d'erreur.

        Parameters
        ----------------
        noise: Any
            La définition de bruit incorrecte.
        args: tuple[Callable]
            Les fonctions pour lesquelles ont défini du bruit.
        """
        msg = (
            'Expected data of type NoneType, '
            f'Callable or a list of length {len(args)} '
            f'but got {noise!r} instead.'
        )
        super().__init__(msg)

class WrongWindowTypeError(TypeError):

    def __init__(self, val: Any) -> None:
        msg = f'Expected int or numpy.ndarray, but got {type(val)}.'
        super().__init__(msg)
