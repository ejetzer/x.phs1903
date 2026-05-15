# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Classes pour l'exécution en parallèle.

Les classes définient ici permettent de facilement exécuter
différentes fonctions en parallèle, en mettant bout à bout
leurs entrées et sorties.
"""
from threading import Thread
from threading import Event
from collections.abc import AnyStr, Collection
from .queue import queue, QueueBase
import matplotlib

type ActionFil[A,B] = Callable[[QueueBase[A], QueueBase[B], Event, ...], None] | None
type AnimateAction[A] = Callable[[A, ...], matplotlib.axes.Axes]

class FilBase[A, B](Thread)):
    def __init__(
        self,
        group: None = None,
        target: ActionFil[A,B] = None,
        name: str | None = None,
        args: tuple[Any] = tuple(),
        kargs: dict[str, Any] = {},
        *,
        daemon: bool | None = None,
        context: Context | None = None,
        arrêt: Event | None = None,
        entrée: QueueBase[A] | None = None,
        sortie: QueueBase[B] | None = None,
        atype: type[A] = str,
        btype: type[B] = str
    ) -> None:
        self._action: ActionFil = target
        self._arrêt: Event = arrêt if arrêt is not None else Event()
        self._entrée: QueueBase = queue(atype)
        self._sortie: QueueBase = queue(btype)
        args = (self._entrée, self._sortie, self._arrêt)
        super().__init__(
            group=group, target=None, name=name, args=args, kargs=kargs, daemon=daemon, context=context
        )

    def run(self, *args: Any, **kargs: Any):
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

    def envoyer_à(self, autre: Self[] | QueueBase[B]) -> None:
        if isinstance(autre, type(self)):
            self._sortie.envoyer_à(autre._sortie)
        elif isinstance(autre, QueueBase):
            self._sortie.envoyer_à(autre)
        else:
            raise TypeError

    def recevoir_de(self, autre: Self | QueueBase[A]) -> None:

    def join(self, timeout: float | qNone = None):
        super().join(timeout)

        if not self.is_alive():
            self._entrée.shutdown(immediate=True)
            self._sortie.shutdown(immediate=False)

class Fil[A](FilBase[A,A]):
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
class FilConversion[A, B](FilBase[A,B]):
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

