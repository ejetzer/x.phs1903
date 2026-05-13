# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
# autodoc: <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>
"""Fonctions et classes pour faciliter les transformées de Fourier."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Self


class Cadre:
    pass


class Transformée:
    def __init__[R](self, nom: str, fonc: Callable[R, R], dom: tuple[type[R]]):
        self.nom = nom
        self.fonc = fonc
        self.dom = dom

    def __call__[R](
        self, nom: str, fonc: Callable[R, R], dom: tuple[type[R]]
    ) -> Self:
        return type(self)(nom, fonc, dom)

    def __matmul__(self, other):
        if isinstance(other, self.dom):
            return self.fonc(other)
        return NotImplemented


class Fenêtre(Transformée):
    def __init__(self, fwhm, forme):
        pass


class TransforméeFourier(Transformée):
    pass


class Filtre(Transformée):
    def __init__(self, f_c, Q=1):
        pass


class FiltrePasseBas(Filtre):
    pass


class FiltrePasseHaut(Filtre):
    pass


class FiltreCoupeBande(Filtre):
    def __init__(self, f_a, f_b, Q=1):
        pass


class FiltrePasseBande(Filtre):
    def __init__(self, f_a, f_b, Q=1):
        pass
