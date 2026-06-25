# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Fonctionnalités de base.

Le module xphs1903.outils contient les classes n'étant pas
spécifiques à un projet en particulier. Elles sont utiles
si vous voulez étendre les capacités du code que vous écrivez
pour votre projet.
"""

# Activer la journalisation
import logging
from functools import partial
from queue import ShutDown
from threading import RLock, Thread
from typing import TYPE_CHECKING

from ..outils.exceptions import (
    AttributNonModifiableError,
    ItemNonModifiableError,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Hashable
    from queue import Queue
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

logging.getLogger(__name__).addHandler(logging.NullHandler())


import logging
import time
from queue import Empty, Queue, ShutDown
from threading import Thread

import numpy
from matplotlib import pyplot as plt
from serial import Serial

logging.basicConfig(level=logging.ERROR)

PORT = '/dev/cu.usbmodemFA13101'
FIGNAME = 'test_fig.pdf'

commandes = Queue()
proxy = Queue()
réponses = Queue()
data = Queue()

files = [commandes, proxy, réponses, data]

ser = Serial(PORT, 115_200)
plt.ion()
ligne1, *_ = plt.plot([], [])
ligne2, *_ = plt.plot([], [])
plt.ylim(0, 5000)
plt.xlim(auto=True)
plt.show()
plt.pause(0.001)


def serie(commandes, ser, proxy):
    while True:
        try:
            com = commandes.get(timeout=0.01)
        except ShutDown:
            proxy.shutdown()
            ser.close()
            break
        except Empty:
            if ser.in_waiting:
                rep = str(ser.readline(), encoding='utf-8')
                try:
                    proxy.put(rep)
                except ShutDown:
                    ser.close()
                    break
        else:
            ser.write(bytes(com, encoding='utf-8'))
            commandes.task_done()
        time.sleep(0.001)

class Appareil(FilAppelReponse):
    __devname__: str

    def __init__(self, dev: ListPortInfo | str | int | None = None) -> None:
        appareil: ListPortInfo
        ports: list[ListPortInfo]
        if isinstance(dev, ListPortInfo):
            appareil = dev
        elif dev is None:
            ports = [d for d in list_ports.grep(self.__devname__)]
            if len(ports) == 1:
                appareil = ports[0]
            else:
                raise AppareilsTropNombreuxError(self.__devname__, ports)
        elif isinstance(dev, str):
            ports = [d for d in list_ports.grep(dev)]
            if len(ports) == 1:
                appareil = ports[0]
            else:
                raise AppareilIntrouvableError(dev, ports)
        elif isinstance(dev, int):
            ports = [d for d in list_ports.grep(self.__devname__)]
            if len(ports) >= dev:
                appareil = ports[dev]
            else:
                raise PasAssezAppareilsError(dev, ports)
        else:
            raise SelectionAppareilTypeError(dev, ListPortInfo, str, int, None)

        super().__init__(appareil)

    def __enter__(self):
        self.start()

    def __exit__(self, *exc):
        if exc[0] is not None:
            self.shutdown()
            return False
        else:
            self.join()
            return True

    def start(self):
        pass

    def join(self):
        pass

    def shutdown(self):
        pass

class Arduino(Appareil):
    __devname__: str = 'Arduino'

class ArduinoNanoEvery(Arduino):
    __devname__: str = 'Arduino Nano Every'

def parse(x):
    cols = x.split()
    vals = [int(c.split(':')[1]) for c in cols]
    return vals


def copie(proxy, réponses, data):
    while True:
        try:
            x = proxy.get()
        except ShutDown:
            réponses.shutdown()
            data.shutdown()
            break
        else:
            réponses.put(x)
            try:
                x = parse(x)
            except Exception:
                continue
            else:
                data.put(x)
            finally:
                proxy.task_done()
        time.sleep(0.001)


def clavier(commandes):
    while True:
        com = input('>>>')

        try:
            commandes.put(com)
        except ShutDown:
            break
        time.sleep(0.001)


def sortie(réponses):
    while True:
        try:
            rep = réponses.get().strip()
        except ShutDown:
            break
        else:
            print(rep)
            réponses.task_done()
        time.sleep(0.001)


fs = (serie, copie, clavier, sortie)
fils = [
    Thread(target=serie, args=(commandes, ser, proxy)),
    Thread(target=copie, args=(proxy, réponses, data)),
#    Thread(target=clavier, args=(commandes,), daemon=True),
    Thread(target=sortie, args=(réponses,), daemon=True),
]

for fil in fils:
    fil.start()

while all(fil.is_alive() for fil in fils):
    try:
        ds = data.get()
        logging.info('ds = %s', ds)
        logging.info('xdata = %s', ligne1.get_xdata())
        logging.info('ydata = %s', ligne1.get_ydata())
        logging.info('xdata = %s', ligne2.get_xdata())
        logging.info('ydata = %s', ligne2.get_ydata())
        ligne1.set_xdata(numpy.append(ligne1.get_xdata(), ds[0]))
        ligne1.set_ydata(numpy.append(ligne1.get_ydata(), ds[1]))
        ligne2.set_xdata(numpy.append(ligne2.get_xdata(), ds[0]))
        ligne2.set_ydata(numpy.append(ligne2.get_ydata(), ds[2]))
        data.task_done()
        plt.xlim(0, ds[0])
        plt.pause(0.001)
        time.sleep(0.001)
    except KeyboardInterrupt:
        commandes.shutdown()
        proxy.shutdown()
        réponses.shutdown()
        data.shutdown()
        break
    except ShutDown:
        break

for f in files:
    f.shutdown()

for f in fils:
    f.join(timeout=1)


class ObjetImmuable:
    """Capsule pour rendre la modification d'un objet peu praticable.

    C'est une classe de convenance pour plus facilement gérer des objets
    dont certains paramètres ne devraient pas être modifiés sans grande
    considération. Le cas d'utilisation précis qui a mené à la création
    de la classe est celui des lignes de communication série, qui une fois
    créées, ne devraient pas voir leurs paramètres modifiés sans un
    changement équivalent pour l'interlocuteur. La solution simple est
    d'empêcher toute modification après l'initialisation.

    Parameters
    ------------
    cls: type
        Type d'objet immuable à créer.
    *args: GenericArgsType
    **kargs: GenericKArgsType

    Attributes
    -----------
    _fixed: bool, default=True
        Drapeau indiquant si l'objet est mutable ou non.
    _object: Final[cls]
        Objet de type ``cls`` créé à l'initialisation.
    _lock: RLock
        Cadenas pour limiter la modification à un seul
        fil d'exécution à la fois.

    Notes
    ------
    Cette classe ne devrait pas être instanciée directement. La
    fonction-usine :py:func:`xphs1903.outils.immuable` devrait être utilisée
    pour créer des variantes immuables de types.

    Les capacités de cette classe sont limitées, et ne sont testées que dans
    le contexte de son utilisation pour des lignes séries. C'est un contexte
    particulier, où les objets :py:class:`serial.Serial` ne sont pas conçus
    pour être utilisés à travers plusieurs fils. Par précaution, je rends
    l'objet immuable pour les fils qui en ont besoin, sans affecter son
    fonctionnement interne.

    .. warning::

        Ne pas utiliser cette classe sur des types internes de Python, ou en
        général s'il existe déjà une variante immuable ou hashable
        d'une classe.

    Python offre déjà des séquences de types mutables et immuables [2]_ et des
    variantes d'objets pouvant être passées d'un fil d'exécution à un autre.
    D'autres modules font de même, ça vaut la peine de lire la documentation
    avant d'improviser avec la classe :py:class:`xphs1903.outils.ObjetImmuable`
    pour encapsuler une nouvelle classe. D'ailleurs, même la documentation de
    PySerial offre une alternative, avec :py:mod:`serial.threaded`. Les objets
    :py:mod:`pandas` sont un bon exemple d'objets avec lesquels il faut aussi
    faire attention dans les fils d'exécution. [3]_ [4]_

    References
    -----------

    .. [2] https://docs.python.org/3/reference/datamodel.html#immutable-sequences

    .. [3] https://pandas.pydata.org/docs/user_guide/gotchas.html#gotchas-thread-safety

    .. [4] https://stackoverflow.com/questions/13592618/python-pandas-dataframe-thread-safe

    See Also
    ---------
    serial.threaded: module d'exécution en parallèle de PySerial.
    threading: module d'exécution en parallèle de Python.
    queue: module de communication entre fils de Python.
    asyncio: module d'exécution asynchrone en Python.

    Examples
    ---------
    L'objet devrait être créé via :py:func:`xphs1903.outils.immuable`.

    >>> int_i = immuable(int)
    >>> int_i(35)
    35

    À l'intérieur d'un bloc ``with`` l'objet devient modifiable:

    >>> with int_i:
    ...     int_i += 1
    ...
    >>> int_i
    36

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
        """
        self._fixed: bool = False
        self._object: Final[cls] = cls(*args, **kargs)
        self._lock: RLock = RLock()

        self.fixer()

    def fixer(self) -> None:
        """Rend l'objet immuable."""
        super().__setattr__('_fixed', True)

    def libérer(self) -> None:
        """Rend l'objet muable."""
        super().__setattr__('_fixed', False)

    def __enter__(self) -> Self:
        """Rend l'objet temporairement muable.

        Returns
        --------
        Self
            L'objet immuable, pour son utilisation.
        """
        self._lock.acquire()
        self.libérer()
        self._object.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """Assure l'immuabilité de l'objet.

        Returns
        ---------
        True
            True pour propager les erreurs
        """
        self.fixer()
        self._lock.release()
        return self._object.__exit__(exc_type, exc_val, exc_tb)

    def __repr__(self) -> str:
        """Affiche repr(_object) avec un '*' quand l'objet est immuable.

        Returns
        --------
        str
            repr(_object)
        """
        return ('', '*')[self._fixed] + repr(self._object)

    def __str__(self) -> str:
        """Retransmets le résultat de la méthode sur _object.

        Returns
        --------
        str
            La chaîne d'affichage d'_object
        """
        return str(self._object)

    def __getattr__(self, attr: str) -> GenericValueType:
        """Obtiens un attribut de l'objet encapsulé.

        Si self n'a pas l'attribut recherché, on regarde l'objet
        encapsulé pour le même attribut. Il n'y a aucune prévention
        de collision de noms autre que l'utilisation de sous-trait.

        Returns
        ---------
        _object.attr
        """
        # On utilise la méthode __getattribute__ de la classe parente
        # pour éviter de se retrouver dans une boucle avec les modifications
        # faites à __getattr__.
        return getattr(super().__getattribute__('_object'), attr)

    def __getitem__(self, key: GenericKeyType) -> GenericValueType:
        """Retourne key de _object.

        Returns
        --------
        La valeur de key de _object
        """
        return self._object[key]

    def __setattr__(self, attr: str, val: GenericValueType) -> None:
        """Règle attr de _object à val si pas _fixed.

        Raises
        --------
        AttributNonModifiableError: Si l'objet ne peut pas être modifié
        """
        if attr == '_fixed' or not self._fixed:
            super().__setattr__(attr, val)
        else:
            raise AttributNonModifiableError(self, attr)

    def __setitem__(self, key: GenericKeyType, val: GenericValueType) -> None:
        """Règle key de _object à val si pas _fixed.

        Raises
        -------
        ItemNonModifiableError: Si l'objet ne peut pas être modifié
        """
        if not self._fixed:
            self._object[key] = val
        else:
            raise ItemNonModifiableError(self, key)

    def __delattr__(self, attr: str) -> None:
        """Retire attr de _object si pas _fixed.

        Raises
        -------
        AttributNonModifiableError: Si l'objet ne peut pas être modifié
        """
        if attr != '_fixed' and not self._fixed:
            super().__delattr__(attr)
        else:
            raise AttributNonModifiableError(self, attr)

    def __delitem__(self, key: GenericKeyType) -> None:
        """Retire key de _object si pas _fixed.

        Raises
        -------
        ItemNonModifiableError: Si l'objet ne peut pas être modifié
        """
        if not self._fixed:
            del self._object[key]
        else:
            raise ItemNonModifiableError(self, key)


def immuable(cls: type) -> type:
    """Retourne une usine d'une version immuable d'un type.

    Returns
    --------
    Une fonction-usine initialisant une version immuable de cls
    """
    return partial(ObjetImmuable, cls)


def estimmuable(obj: ObjetImmuable) -> bool:
    """Retourne si un objet est actuellement immuable.

    Returns
    --------
    bool
        Si un objet est actuellement immuable
    """
    return hasattr(obj, '_fixed') and obj._fixed


def paires[A](x: iter[A], n: int = 2) -> tuple[A]:
    """Retourne des tranches de x de taille n.

    Ce générateur est basé sur une réponse StackOverflow
    de Nadia Alramli [1]_

    Parameters
    -----------
    x : iter[A]
        Objet itérable retournant des objets de type A.
    n : int, default=2
        Taille des sous-ensembles à produire

    Yields
    -------
    tuple[A]
        Un tuple de n éléments de x

    See Also
    ----------
    itertools : Module de fonctions pour manipuler des itérateurs
    itertools.batched : Fonction une fonctionalité similaire
    itertools.zip_longest : Fonction alternative à ``zip``.

    Notes
    -------
    L'énoncé ``zip(*((iter(x),)*n))`` est équivalent
    à ``zip(iter(x), iter(x), ...)``
    avec :math:`n` arguments.

    References
    -----------

    .. [1] Nadia Alramli, https://stackoverflow.com/a/1335618
        Retrieved 2026-05-14, License - CC BY-SA 2.5

    Examples
    ---------
    Si :math:`n` divise ``len(x)``, on obtient ``len(x)/n`` tuples
    de longueur :math:`n`.

    >>> list(paires(range(10)))
    [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)]

    En général, on obtient ``len(x)//n`` de longueur :math:`n`. Quand
    :math:`n` ne divise pas ``len(x)`` les ``len(x) % n`` derniers éléments
    sont ignorés. Une implémentation de la fonction
    utilisant :py:func:`itertools.zip_longest`
    n'a pas ce problème et agit plus comme :py:func:`itertools.batched`.

    >>> list(paires(range(10), 3))
    [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    """
    # Source - https://stackoverflow.com/a/1335618
    # Posted by Nadia Alramli, modified by community.
    # See post 'Timeline' for change history
    # Retrieved 2026-05-14, License - CC BY-SA 2.5
    yield from zip(*((iter(x),) * n), strict=True)


def se_tourner_les_pouces(
    sieste: float = 0.1, fils: list[Thread] | None = None
) -> None:
    """Une fonction qui ne fait rien en attendant que des fils se terminent.

    L'usage de cette fonction est minimal. Si vous avez plusieurs fils
    d'exécution, vous pouvez utiliser le motif suivant:

    .. code:: python

        fil.start()
        se_tourner_les_pouces()
        fil.join()

    pour continuer l'exécution de ``fil`` jusqu'à ce que l'utilisateur tape
    :kbd:`Control-C` ou que fil signale :py:obj:`KeyboardInterrupt`. Une autre
    forme d'appel est:

    .. code:: python

        fil1.start()
        fil2.start()
        se_tourner_les_pouces(fils=(fil1, fil2))
        fil1.join()
        fil2.join()

    pour sortir du programme quand ``fil1, fil2`` ont terminé de
    s'exécuter.

    Parameters
    -----------
    sieste: float, default=0.1
        Le temps de chaque pause du programme principal.
    fils: list[threading.Thread], optional
        Une liste de fils d'exécution à surveiller.

    Notes
    ------
    Cette fonction peut aussi être utilisée avec les objets de
    type :py:class:`xphs1903.outils.para.FilBase`.

    .. code:: python

        with FilBase() as fil1, FileBase(), fil2:
            se_tourner_les_pouces(fils=(fil1, fil2))

    """
    from time import sleep

    def cond() -> bool:
        """Retourne :py:obj:`True`."""
        return True

    if fils is not None:

        def cond() -> bool:
            """Vérifie si il reste des fils actifs."""
            return any(map(Thread.is_alive, fils))

    while cond():  # Pour toujours!
        try:
            sleep(sieste)  # Dormir un petit peu
        except KeyboardInterrupt:  # Quitter si l'utilisateur le demande
            logging.getLogger(__name__).info('Sortie par KeyboardInterrupt.')
            break  # On sort de la boucle sans réémettre l'interruption
