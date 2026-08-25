# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Outils de manipulation de fonctions."""

# ruff: noqa: ANN401

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

# Source - https://stackoverflow.com/a/76453871
# Posted by sam2426679
# Retrieved 2026-08-14, License - CC BY-SA 4.0


class StaticPropertyClass(property):
    """Propriété statique."""

    def __get__[A](
        self, owner_self: A, owner_cls: type[A] | None = None
    ) -> Any:
        """Exécute la fonction enveloppée sans arguments self ou cls.

        Returns
        ------------------------
        Any
            La valeur de la propriété de classe.
        """
        return self.fget()


staticproperty = StaticPropertyClass


class ClassPropertyClass(property):
    """Propriété de classe."""

    def __get__[A](
        self, owner_self: A, owner_cls: type[A] | None = None
    ) -> Any:
        """Exécute la fonction enveloppée avec un argument cls.

        Returns
        ------------------------
        Any
            La valeur de la propriété de classe.
        """
        return self.fget(owner_cls)


classproperty = ClassPropertyClass

__all__ = []
