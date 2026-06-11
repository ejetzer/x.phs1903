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


class FilCopie[A, B](Thread):
    """Fil copiant les éléments d'une file vers d'autres.

    Parameters
    -----------
    orig: queue.Queue[A]
        File d'origine, à copier.
    dest: list[queue.Queue[B]]
        Files vers lesquelles copier les éléments de :py:data:`orig`.
    conv: list[typing.Callable[[A], B]]
        Fonctions de conversion à utiliser.

    Attributes
    -----------
    orig: queue.Queue[A]
        File d'origine, à copier.
    dest: list[queue.Queue[B]]
        Files vers lesquelles copier :py:attr:`FilCopie.orig`.
    conv: list[typing.Callable[[A], B]]
        Fonctions de conversion de :py:attr:`FilCopie.orig`
        vers :py:attr:`FilCopie.dest`.

    Methods
    --------
    start()
        Démarre l'exécution du fil, et donc la copie d'une file
        aux autres. Héritée de :py:class:`threading.Thread`.

    Notes
    ------
    Cette classe est destinée à être utilisée quand les différentes
    files se trouvent dans différents fils d'exécution, avec normalement
    aucune file traitée uniquement dans le fil principal. En particulier,
    cette classe résout le problème d'envoyer un message d'un fil
    d'exécution à plusieurs autres fils.

    Par exemple, dans un programme de communication et affichage de base
    du cours PHS1903, on peut vouloir afficher et traiter les mêmes données
    de manières différentes et simultanées. On peut donc relier la file de
    sortie du fil de prise de données aux files d'entrée des fils de traitement
    et d'affichage.

    See also
    ---------
    threading.Thread: Classe de fil d'exécution en parallèle
    queue.Queue: Classe de file partagée entre fils
    itertools.tee: Fonction similaire mais pour des itérateurs

    Examples
    ----------
    Un exemple simplifié à en être inutile et trivial serait le suivant.
    Rien n'est fait avec les données, mais on peut voir qu'elles ont
    été copiées vers les deux files de sortie.

    >>> with FilCopie(
    ...     queue.Queue(), [queue.Queue(), queue.Queue()], lambda x: x
    ... ) as fil:
    ...     for i in range(10):
    ...         fil.orig.put(1)
    >>>  while (res := fil.dest[0].get()):
    ...     print(res)
    ...
    0
    1
    2
    3
    4
    5
    6
    7
    8
    9
    >>> while res := fil.dest[1].get():
    ...     print(res)
    0
    1
    2
    3
    4
    5
    6
    7
    8
    9

    """

    def __init__(
        self,
        orig: Queue[A],
        dest: list[Queue[B]],
        conv: list[Callable[[A], B]],
    ) -> None:
        """Fil copiant les éléments d'une file vers d'autres.

        Parameters
        -----------
        orig: queue.Queue[A]
            File d'origine, à copier.
        dest: list[queue.Queue[B]]
            Files vers lesquelles copier les éléments de :py:data:`orig`.
        conv: list[Callable[[A], B]]
            Fonctions de conversion à utiliser.
        """
        self.orig: Queue[A] = orig
        self.dest: list[Queue[B]] = dest.copy()
        self.conv: list[Callable[[A], B]] = conv.copy()

        # Pas besoin de modifier les valeurs par défaut
        # Sauf pour la démonisation
        super().__init__(daemon=True)

    def shutdown(self) -> None:
        """Termine le fil d'exécution.

        Appelle :py:meth:`threading.Thread.shutdown` sur
        :py:attr:`FilCopie.orig` et sur les
        files listées dans :py:attr:`FilCopie.dest`. Termine ensuite le fil
        d'exécution.
        """
        for q in self.dest:
            q.shutdown()
        super().shutdown()

    def join(self) -> None:
        """Termine le fil d'exécution.

        Attend que la file :py:attr:`FilCopie.orig` soit vide, puis celles
        listées dans :py:attr:`FilCopie.dest`. Termine ensuite le fil
        d'exécution.
        """
        for q in self.dest:
            q.join()
        super().join()

    def __enter__(self) -> Self:
        """Démarre le fil d'exécution.

        Returns
        --------
        Self
        """
        self.start()
        return self

    def __exit__(self, *exc) -> bool:
        """Termine le fil d'exécution.

        Parameters
        -----------
        *exc
            Description de l'exception ou :py:obj:None.

        Returns
        --------
        True
            Si il n'y a aucune exception
        False
            Relève toutes les exceptions sans les gérer.
        """
        self.shutdown()
        return exc[0] is None

    def run(self) -> None:
        """Copie les éléments de :py:attr:`FilCopie.orig` vers :py:attr:`FilCopie.dest`."""
        while True:
            try:
                x = self.orig.get()

                for q, conv in zip(self.dest, self.conv, strict=True):
                    q.put(conv(x))
                self.orig.task_done()
            except ShutDown:
                self.shutdown()
                break


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
