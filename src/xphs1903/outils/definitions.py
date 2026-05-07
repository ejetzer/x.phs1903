# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Définitions de base pour les autres modules du paquet xphs1903."""

import logging
from functools import partial
from typing import TYPE_CHECKING

from ..outils.exceptions import AttributNonModifiableError, ItemNonModifiableError

logging.getLogger(__name__).addHandler(logging.NullHandler())
if TYPE_CHECKING:
    from collections.abc import Hashable
    from types import TracebackType
    from typing import Any, Final, Self, TypeAlias

    'Type générique pour les arguments énumérés comme *args'
    GenericArgsType: type = TypeAlias(Any)

    'Type générique pour les arguments nommés comme **kargs'
    GenericKArgsType: type = TypeAlias(Any)

    'Type générique pour une clé de dictionnaire'
    GenericKeyType: type = Hashable

    "Type générique pour une valeur d'attribut ou d'item"
    GenericValueType: type = TypeAlias(Any)


class ObjetImmuable:
    """Capsule pour rendre la modification d'un objet peu praticable.

    Attributes:
        _fixed: indique et détermine si _object peut être modifié
        _object: l'objet à protéger
    """

    def __init__(
        self, cls: type, *args: GenericArgsType, **kargs: GenericKArgsType
    ) -> None:
        """Encapsule un objet pour rendre sa modification impraticable.

        C'est une classe de convenance pour plus facilement gérer des objets
        dont certains paramètres ne devraient pas être modifiés sans grande
        considération. Le cas d'utilisation précis qui a mené à la création
        de la classe est celui des lignes de communication série, qui une fois
        créées, ne devraient pas voir leurs paramètres modifiés sans un
        changement équivalent pour l'interlocuteur. La solution simple est
        d'empêcher toute modification après l'initialisation.
        """  # noqa: D401
        self._fixed: bool = False
        self._object: Final[cls] = cls(*args, **kargs)
        self.fixer()

    def fixer(self) -> None:
        """Rend l'objet immuable."""
        super().__setattr__('_fixed', True)

    def libérer(self) -> None:
        """Rend l'objet muable."""
        super().__setattr__('_fixed', False)

    def __enter__(self) -> Self:
        """Rend l'objet temporairement muable.

        Returns:
            L'objet immuable, pour son utilisation.
        """
        self.libérer()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """Assure l'immuabilité de l'objet.

        Returns:
            True pour propager les erreurs
        """
        self.fixer()
        return True

    def __repr__(self) -> str:
        """Affiche repr(_object) avec un '*' quand l'objet est immuable.

        Returns:
            repr(_object)
        """
        return ('', '*')[self._fixed] + repr(self._object)

    def __str__(self) -> str:
        """Retransmets le résultat de la méthode sur _object.

        Returns:
            La chaîne d'affichage d'_object
        """
        return str(self._object)

    def __getattr__(self, attr: str) -> GenericValueType:
        """Obtiens un attribut de l'objet encapsulé.

        Si self n'a pas l'attribut recherché, on regarde l'objet
        encapsulé pour le même attribut. Il n'y a aucune prévention
        de collision de noms autre que l'utilisation de sous-trait.

        Returns:
            str(_object)
        """
        # On utilise la méthode __getattribute__ de la classe parente
        # pour éviter de se retrouver dans une boucle avec les modifications
        # faites à __getattr__.
        return getattr(super().__getattribute__('_object'), attr)

    def __getitem__(self, key: GenericKeyType) -> GenericValueType:
        """Retourne key de _object.

        Returns:
            La valeur de key de _object
        """
        return self._object[key]

    def __setattr__(self, attr: str, val: GenericValueType) -> None:
        """Règle attr de _object à val si pas _fixed.

        Raises:
            AttributNonModifiable: Si l'objet ne peut pas être modifié
        """
        if attr == '_fixed' or not self._fixed:
            super().__setattr__(attr, val)
        else:
            raise AttributNonModifiable(self, attr)

    def __setitem__(self, key: GenericKeyType, val: GenericValueType) -> None:
        """Règle key de _object à val si pas _fixed.

        Raises:
            ItemNonModifiable: Si l'objet ne peut pas être modifié
        """
        if not self._fixed:
            self._object[key] = val
        else:
            raise ItemNonModifiable(self, key)

    def __delattr__(self, attr: str) -> None:
        """Retire attr de _object si pas _fixed.

        Raises:
            AttributNonModifiable: Si l'objet ne peut pas être modifié
        """
        if attr != '_fixed' and not self._fixed:
            super().__delattr__(attr)
        else:
            raise AttributNonModifiable(self, attr)

    def __delitem__(self, key: GenericKeyType) -> None:
        """Retire key de _object si pas _fixed.

        Raises:
            ItemNonModifiable: Si l'objet ne peut pas être modifié
        """
        if not self._fixed:
            del self._object[key]
        else:
            raise ItemNonModifiable(self, key)


def immuable(cls: type) -> type:
    """Retourne une usine d'une version immuable d'un type.

    Returns:
        Une fonction-usine initialisant une version immuable de cls
    """
    return partial(ObjetImmuable, cls)


def estimmuable(obj: ObjetImmuable) -> bool:
    """Retourne si un objet est actuellement immuable.

    Returns:
        Si un objet est actuellement immuable
    """
    return hasattr(obj, '_fixed') and obj._fixed
