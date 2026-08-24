# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Définitions d'execptions et erreurs précises."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any


class BaseXPHS1903Exception(BaseException):
    pass


class WrongSerialInputTypeError(TypeError, BaseXPHS1903Exception):
    """Entrée fournie du mauvais type ou format."""

    def __init__(self, obj: Any) -> None:
        """Crée le message d'erreur.

        Parameters
        ----------------
        obj: Any
            L'objet du mauvais type.
        """
        msg = f'Expected str or list[dict] but got {type(obj)}.'
        super().__init__(msg)


class ParsableArduinoSerialDataError(ValueError, BaseXPHS1903Exception):
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


class NoiseTypeError(TypeError, ValueError, BaseXPHS1903Exception):
    """Mauvais type ou format pour une définition de bruit sur un signal."""

    def __init__(self, noise: Any, args: tuple[Callable]) -> None:
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


class WrongWindowTypeError(TypeError, BaseXPHS1903Exception):
    def __init__(self, val: Any) -> None:
        msg = f'Expected int or numpy.ndarray, but got {type(val)}.'
        super().__init__(msg)


class WrongCanvasTypeError(TypeError, BaseXPHS1903Exception):
    def __init__(self, val: Any) -> None:
        msg = f'Expected FigureCanvasAgg but got {type(val)}'
        super().__init__(msg)


class UpdatedPropertyTypeError(TypeError, BaseXPHS1903Exception):
    def __init__(self, val: Any) -> None:
        msg = f'updated can only be boolean, not {type(val)}'
        super().__init__(msg)


class WrongArtistTypeError(TypeError, BaseXPHS1903Exception):
    def __init__(self, val: Any) -> None:
        msg = f'Expected instance of matplotlib.artist.Artist but got {type(val)}.'
        super().__init__(msg)


class NotLine2DTypeError(TypeError, BaseXPHS1903Exception):
    def __init__(self, val: Any) -> None:
        msg = f'Expected matplotlib.lines.Line2D but got {type(val)}.'
        super().__init__(msg)


class NotAxesTypeError(TypeError, BaseXPHS1903Exception):
    def __init__(self, val: Any) -> None:
        msg = f'Expected matplotlib.axes.Axes but got {type(val)}.'
        super().__init__(msg)


class NotFigureTypeError(TypeError, BaseXPHS1903Exception):
    def __init__(self, val: Any) -> None:
        msg = f'Expected matplotlib.figure.Figure but got {type(val)}.'
        super().__init__(msg)


class IncorrectFormatTypeError(TypeError, BaseXPHS1903Exception):
    def __init__(self, obj: BaseFormat, oth: Any) -> None:
        msg = f'Expected dict or {type(obj).__name__} but got {type(oth)}.'
        super().__init__(msg)


class CanvasAlreadySetError(RuntimeError, BaseXPHS1903Exception):
    def __init__(self, canvas: FigureCanvasAgg) -> None:
        msg = f'canvas is already set to {canvas} and cannot be changed.'
        super().__init__(msg)


class IncorrectFormatKeyError(KeyError, BaseXPHS1903Exception):
    def __init__(self, obj: BaseFormat, key: str) -> None:
        msg = f'{key!r} is not in the allowed keys. Allowed keys are: {obj.SETTINGS}.'
        super().__init__(msg)


class InvalidCommandTypeError(TypeError, BaseXPHS1903Exception):
    def __init__(self, val: Any) -> None:
        msg = f'Expected str but got {type(val)}.'
        super().__init__(msg)
