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

type ActionFil[A, B] = Callable[[FileBase[A], FileBase[B], Event, ...], None] | None
"""La signature d'une fonction pouvant être exécutée dans un fil parallèle avec ce module."""

type AnimateAction[A] = Callable[[A, ...], matplotlib.axes.Axes]
"""La signature d'une fonction générant des cadres d'animation pour l'affichage graphique."""

class FileBase[A](Queue):
    def __init__(
        self,
        maxsize: int = 0,
        _cls: type[A] | Callable[..., A] = lambda x: x,
        aval: list[Self] | None = None,
        parent: FilBase | None = None,
    ) -> None:
        self._cls: type[A] = _cls
        self._aval: list[Self] = [] if aval is None else aval
        self._parent: FilBase | None = parent
        super().__init__(maxsize=maxsize)

    def _avaliser(self, fct: str, *args: Any, **kargs: Any) -> None:
        _file: Self
        for _file in self._aval:
            fct: Callable[..., None] = getattr(_file, fct)
            fct(*args, **kargs)

    def put(
        self,
        item: A,
        block: bool = True,
        timeout: float | None = None
    ) -> None:
        item: A = self._cls(item)
        try:
            super().put(item, block=block, timeout=timeout)
        except Full:
            logging.getLogger(__name__).exception()
            raise
        except ShutDown:
            logging.getLogger(__name__).exception()
            raise
        else:
            self._avaliser('put', item)

    def put_nowait(self, item: A) -> None:
        self.put(item, block=False)

    def shutdown(self, immediate: bool = False) -> None:
        self._avaliser('shutdown', immediate=immediate)
        super().shutdown()

    def join(self) -> None:
        self._avaliser('join')
        super().join()

    def envoyer_à(self, autre: Self) -> None:
        self._aval.append(autre)

    def recevoir_de(self, autre: Self) -> None:
        autre.envoyer_à(self)

    def get(self, block: bool = True, timeout: float | None = None) -> A:
        return super().get(block, timeout)

    def get_nowait(self) -> A:
        return super().get_nowait()

    def __lshift__(self, other: Self):
        if isinstance(self, FileBase):
            self.recevoir_de(other)
        else:
            return NotImplemented

    def __rshift__(self, other: Self):
        if isinstance(self, FileBase):
            self.envoyer_à(other)
        else:
            return NotImplemented

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
        entrée: FileBase[A] | None = None,  #: File d'objets en entrée.
        sortie: FileBase[B] | None = None,  #: File d'objets en sortie.
        atype: type[A] = str,  #: Type des objets en entrée.
        btype: type[B] = str  #: Type des objets en sortie.
    ) -> None:
        self._action: ActionFil = target
        """Fonction exécutée en parallèle."""

        if arrêt is None:
            arrêt: Event = Event()

        self._arrêt: Event = arrêt
        """Signal d'arrêt de l'exécution."""

        if entrée is None:
            entrée: FileBase = FileBase(atype)

        self._entrée: FileBase = entrée
        """File d'entrée pour self._action."""

        if sortie is None:
            sortie: FileBase = FileBase(btype)

        self._sortie: FileBase = sortie
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
            self._sortie.envoyer_à(autre._entrée)
        elif isinstance(autre, FileBase):
            self._sortie.envoyer_à(autre)
        else:
            raise TypeError

    def recevoir_de(self, autre: Self | QueueBase[A]) -> None:
        if isinstance(autre, type(self)):
            self._entrée.recevoir_de(autre._sortie)
        elif isinstance(autre, FileBase):
            self._entrée.recevoir_de(autre)

    def join(self, timeout: float | None = None):
        super().join(timeout)

        if not self.is_alive():
            self._entrée.shutdown(immediate=True)
            self._sortie.shutdown(immediate=False)

    def __or__(self, other):
        if isinstance(other, FilBase):
            self.envoyer_à(other)
            return other
        else:
            return NotImplemented

    def __ror__(self, other):
        if isinstance(other, FilBase):
            self.recevoir_de(other)
            return self
        else:
            return NotImplemented

    def __rrshift__(self, other):
        if isinstance(other, (FilBase, FileBase)):
            self.recevoir_de(other)
        else:
            return NotImplemented

    def __lshift__(self, other):
        if isinstance(other, (FilBase, FileBase)):
            self.recevoir_de(other)
        else:
            return NotImplemented


class Fil[A](FilBase[A, A]):
    def __init__(
        self,
        group: None = None,  # Argument bidon pour implémentation future.
        target: ActionFil[A, B] = None,  # Fonction à exécuter en parallèle.
        name: str | None = None,  # Nom du fil d'exécution.
        args: tuple[Any] = tuple(),  # Arguments positionnels pour target
        kargs: dict[str, Any] = {},  # Arguments nommés pour target
        *,
        daemon: bool | None = None,  # True si le fil doit se fermer automatiquement
        context: Context | None = None,  # Contexte d'exécution, voir :py:class:threading.Threads.
        arrêt: Event | None = None,  # Événement d'arrêt de l'exécution.
        entrée: FileBase[A] | None = None,  # File d'objets en entrée.
        sortie: FileBase[A] | None = None,  # File d'objets en sortie.
        atype: type[A] = str,  # Type des objets en entrée.
    ) -> None:
        super().__init__(
            group=group,
            target=target,
            name=name,
            args=args
            kargs=kargs,
            daemon=daemon,
            context=context,
            arrêt=arrêt,
            entrée=entrée
            sortie=sortie,
            atype=atype,
            btype=atype
        )

class FilConversion[A, B](FilBase[A, B]):

    @typing.override
    def __init__(
        self,
        cible: ActionFil[A, B],
        atype: type[A],
        btype: type[B]
    ):
        super().__init__(
            group=None,
            target=cible,
            name=None,
            args=tuple(),
            kargs={},
            daemon=True,
            arrêt=None,
            entrée=None,
            sortie=None,
            atype=atype,
            btype=btype
        )

class FilConversionDict(FilConversion[bytes, dict[str, float]]):

    @typing.override
    def __init__(self):
        super().__init__(self._conv, bytes, dict[str, float])

    def _conv(self, a: bytes) -> dict[str, float]:
        ligne = str(a, encoding='utf-8')
        champs = ligne.split('\t')
        cles_valeurs = [champ.split() for champ in champs]
        b = {c: float(v) for c, v in cles_valeurs}
        return b

class FilConversionSeries(FilConversion[dict[str, float], pandas.Series]):

    @typing.override
    def __init__(self):
        super().__init__(self._conv, dict[str, float], pandas.Series)

    def _conv(self, a: dict[str, float]) -> pandas.Series:
        return pandas.Series(a)


class FilDataframe(FilConversion[pandas.Series, pandas.Dataframe]):

    @typing.override
    def __init__(self):
        super().__init__(self._conv, pandas.Series, pandas.Dataframe)
        self._acc: pandas.Dataframe = pandas.Dataframe()

    def _conv(self, a: pandas.Series) -> pandas.Dataframe:
        self._acc = pandas.concat([self._acc, a])
        return self._acc

class FilCalcul(Fil[pandas.Dataframe]):

    @typing.override
    def __init__(self, calcul: Callable[pandas.Dataframe, pandas.Dataframe]):
        super().__init__(self._conv, pandas.Dataframe)
        self._calcul: Callable[pandas.Dataframe, pandas.Dataframe] = calcul

    def _conv(self, a: pandas.Dataframe) -> pandas.Dataframe:
        b = calcul(a)
        return b

class FilFFT(FilCalcul):

    @typing.override
    def __init__(self, tcol: str, xcol: str):
        super().__init__(calcul=self._fft)
        self.tcol: str = tcol
        self.xcol: str = xcol

    def _fft(self, a: pandas.Dataframe):
        ts: numpy.ndarray = a.loc[:, self.tcol].to_numpy()
        xs: numpy.ndarray = a.loc[:, self.xcol].to_numpy()
        Xs: numpy.ndarray = numpy.fft.rfft(xs)

        n = ts.size
        d = (ts[:-1] - ts[1:]).mean()
        Fs: numpy.ndarray = numpy.fft.rfftfreq(n, d)
        return pandas.Dataframe({'F': Fs, 'X': Xs})

class Journal:

    def __init__(
        self,
        entrée,
    ):
        pass

    def start(self):
        pass

    def pause(self):
        pass

    def resume(self):
        pass

    def mute(self):
        pass

class Tableur(Journal):
    pass

# eg: pour mettre une matplotlib.figure.Figure à jour
# - Utiliser FuncAnimation pour ne pas avoir besoin d'une boucle
# - Utiliser un timeout pour ne pas bloquer l'exécution
# - les cadres sont les items obtenus de _entrée
class Traceur(Journal):

    def __init__(self):
        pass

    def start(self):
        pass

    def pause(self):
        pass

    def resume(self):
        pass
