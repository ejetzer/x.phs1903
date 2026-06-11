# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Classes pour l'exécution en parallèle.

Les classes définient ici permettent de facilement exécuter
différentes fonctions en parallèle, en mettant bout à bout
leurs entrées et sorties.
"""

import typing
from collections.abc import (
    Callable,
    Collection,  #: Types de base abstraits pour les vérifications
)
from threading import (
    Event,  #: Objet de signal entre fils
    Thread,  #: Objet de base de parallélisme
)
from typing import AnyStr

# import matplotlib #: Affichage graphique
import matplotlib.axes

from .queue import (  #: Classes de files pour la communication entre fils
    QueueBase,
    queue,
)

type ActionFil[A, B] = Callable[[QueueBase[A], QueueBase[B], Event, ...], None] | None
"""La signature d'une fonction pouvant être exécutée dans un fil parallèle avec ce module."""

type AnimateAction[A] = Callable[[A, ...], matplotlib.axes.Axes]
"""La signature d'une fonction générant des cadres d'animation pour l'affichage graphique."""


class FilBase[A, B](Thread):
    """Classe de fil de base avec files d'entrée et sortie et signal d'arrêt."""

    def __init__(
        self,
        group: None = None,  #: Argument bidon pour implémentation future.
        target: ActionFil[A, B] = None,  #: Fonction à exécuter en parallèle.
        name: str | None = None,  #: Nom du fil d'exécution.
        args: tuple[Any] = tuple(),  #: Arguments positionnels pour target
        kargs: dict[str, Any] = {},  #: Arguments nommés pour target
        *,
        daemon: bool | None = None,  #: True si le fil doit se fermer automatiquement
        context: Context | None = None,  #: Contexte d'exécution, voir :mod:Threads.
        arrêt: Event | None = None,  #: Événement d'arrêt de l'exécution.
        entrée: QueueBase[A] | None = None,  #: File d'objets en entrée.
        sortie: QueueBase[B] | None = None,  #: File d'objets en sortie.
        atype: type[A] = str,  #: Type des objets en entrée.
        btype: type[B] = str  #: Type des objets en sortie.
    ) -> None:
        self._action: ActionFil = target
        """Fonction exécutée en parallèle."""

        self._arrêt: Event = arrêt if arrêt is not None else Event()
        """Signal d'arrêt de l'exécution."""

        self._entrée: QueueBase = queue(atype)
        """File d'entrée pour self._action."""

        self._sortie: QueueBase = queue(btype)
        """File de sortie pour self._action."""

        #: Initialisation de l'objet Thread
        #: avec les paramètres par défaut
        #: adéquats. Spécifiquement,
        #: target=None pour permettre la redéfinition
        #: de la méthode run.
        super().__init__(
            group=group,
            target=None,
            name=name,
            args=args,
            kargs=kargs,
            daemon=daemon,
            context=context
        )

    def run(self, *args: Any, **kargs: Any):
        """Fonction exécutée en parallèle."""
        if self._action is not None:
            while not self._arret.is_set():
                self._action(self._entrée, self._sortie, self._arrêt, *args, **kargs)

    def arrêter(self) -> None:
        self._entrée.shutdown()
        self._arrêt.set()

    def put(self, item: A, block: bool = True, timeout: float | None = None) -> None:
        self._entrée.put(item, block, timeout)

    def get(self, block: bool = True, timeout: float | None = None) -> B:
        return self._sortie.get(block, timeout)

    def envoyer_à(self, autre: Self[B] | QueueBase[B]) -> None:
        if isinstance(autre, type(self)):
            self._sortie.envoyer_à(autre._sortie)
        elif isinstance(autre, QueueBase):
            self._sortie.envoyer_à(autre)
        else:
            raise TypeError

    def recevoir_de(self, autre: Self | QueueBase[A]) -> None:
        pass

    def join(self, timeout: float | None = None):
        super().join(timeout)

        if not self.is_alive():
            self._entrée.shutdown(immediate=True)
            self._sortie.shutdown(immediate=False)


class Fil[A](FilBase[A, A]):
    pass


# eg: pour l'entrée standard
class FilEntrée(FilBase[None, AnyStr]):
    pass


# eg: pour la sortie standard
class FilSortie(FilBase[AnyStr, None]):
    pass


# eg: pour la ligne série
class FilIO(Fil[AnyStr]):
    pass


# eg: conversion de chaîne à pandas.Series
class FilConversion[A, B](FilBase[A, B]):
    pass


# eg: de pandas.Series à pandas.DataFrame
class FilTab[A](FilBase[A, Collection[A]]):
    pass


# eg: pour mettre une matplotlib.figure.Figure à jour
# - Utiliser FuncAnimation pour ne pas avoir besoin d'une boucle
# - Utiliser un timeout pour ne pas bloquer l'exécution
# - les cadres sont les items obtenus de _entrée
class PseudoFilTrace[A](FilBase[Collection[A], matplotlib.axes.Axes]):

    @typing.override
    def __init__(self,
        group: None = None,
        target: AnimateAction = None,
        name: str | None = None,
        args: tuple[Any] = tuple(),
        kargs: dict[str, Any] = {},
        *,
        daemon: bool | None = None,
        context: Context | None = None,
        arrêt: Event | None = None,
        entrée: QueueBase[A] | None = None,
        sortie: QueueBase[matplotlib.axes.Axes] | None = None,
        atype: type[A] = str,
        btype: type[matplotlib.axes.Axes] = matplotlib.axes.Axes
    ):
        pass

    def __next__(self):
        pass

    def __iter__(self) -> Self:
        return self

    def start():
        pass

    def pause():
        pass

    def resume():
        pass
