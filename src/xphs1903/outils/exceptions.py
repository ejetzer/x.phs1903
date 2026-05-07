# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Exceptions et erreurs du module xphs1903."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .definitions import ObjetImmuable


class BasePHS1903Error(Exception):
    """Erreur de base du module xphs1903."""

    def __init__(self, msg: str) -> None:
        """Erreur de base du module xphs1903."""
        super().__init__(f'[{type(self).__name__}] {msg}')


class RuntimePHS1903Error(BasePHS1903Error): ...  # noqa: D101


class AttributePHS1903Error(BasePHS1903Error): ...  # noqa: D101


class KeyPHS1903Error(BasePHS1903Error): ...  # noqa: D101


class ValuePHS1903Error(BasePHS1903Error): ...  # noqa: D101


class ObjetImmuableError(RuntimePHS1903Error):
    """Erreur indiquant un accès non-autorisé à un objet immuable.

    Attributes:
        obj: l'objet immuable lié à l'erreur
    """

    def __init__(self, obj: ObjetImmuable) -> None:
        """Décrit l'erreur impliquant obj."""
        self.obj: ObjetImmuable = obj

        msg: str = f'{obj:r} est immuable.'
        super().__init__(msg)


class AttributNonModifiableError(AttributePHS1903Error, ObjetImmuableError):
    """Erreur indiquant un accès non-autorisé à un objet immuable.

    Attributes:
        obj: l'objet immuable
        attr: l'attribut
    """

    def __init__(self, obj: ObjetImmuable, attr: str) -> None:
        """Erreur indiquant un accès non-autorisé à un objet immuable."""
        self.obj: ObjetImmuable = obj
        self.attr: str = attr

        super().__init__(f"L'attribut {attr:r} de {obj:r} est immuable.")


class ItemNonModifiableError(KeyPHS1903Error, ObjetImmuableError):
    """Erreur indiquant un accès non-autorisé à un objet immuable.

    Attributes:
        obj: l'objet immuable
        key: clé
    """

    def __init__(self, obj: ObjetImmuable, key: str) -> None:
        """Erreur indiquant un accès non-autorisé à un objet immuable."""
        self.obj: ObjetImmuable = obj
        self.key: str = key

        super().__init__(f"L'élément {key:r} de {obj:r} est immuable.")


class ChoixInvalideError(ValuePHS1903Error):
    """Erreur indiquant un choix invalide.

    Attributes:
        sel: sélection invalide
        choix: liste des options valides
    """

    def __init__(self, selection: int, choix_possibles: list[int]) -> None:
        """Erreur indiquant un choix invalide."""
        self.sel: int = selection
        self.choix: list[int] = choix_possibles

        super().__init__(
            f"La sélection {selection:r} n'est pasdans {{choix_possibles:s}}."
        )


class PasUnNombreEntierError(ValuePHS1903Error):
    """Erreur indiquant qu' une valeur n'est pas un nombre entier.

    Attributes:
        sel: sélection invalide
    """

    def __init__(self, selection: str) -> None:
        """Erreur indiquant qu' une valeur n'est pas un nombre entier."""
        self.sel: str = selection

        super().__init__(
            f'La sélection {selection:r} ne représentepas un nombre entier.'
        )
