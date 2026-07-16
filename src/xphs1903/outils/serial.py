# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Utilitaires de communication série.

``xphs1903.outils.serial``
===============================

Ce module contient des utilitaires de communication avec la ligne série.
Le module est basé sur les modules :py:mod:`threading` et
:external+serial:mod:`serial`. La classe principale :class:`LigneSerie` permet
d'ouvrir une ligne série avec un bloc :code:`with` (gestionnaire de contexte).

Connexion à un port série
----------------------------

    :class:`LigneSerie`

Connexion à un Arduino Nano Every
---------------------------------------

    :class:`ArduinoNanoEvery`

See also
------------------
serial.Serial : Classe de communication série de base.
threading.Thread : Classe d'exécution en parallèle.
queue.Queue : Classe de communication entres fils d'exécution.

Examples
------------------
Ouvrir une ligne série en mode *loopback* ou *écho*. Tout ce qui est
envoyé à :class:`LigneSerie` avec :func:`LigneSerie.print` peut
immédiatement être lu avec la fonction :func:`next`.

>>> with xphs1903.outils.serial.LigneSerie() as com:
...     for i in range(10):
...         com.print(str(i))
...         print(next(com))
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

import logging
import queue
import threading
import typing

import serial

__logger = logging.getLogger(__name__)
"""Journal de débogage interne du module.

Utile pour le débogage, ne devrait être obtenu qu'avec
:func:`logging.getLogger`.
"""

__logger.addHandler(logging.NullHandler())

if typing.TYPE_CHECKING:
    from types import TracebackType
    from typing import Self

type BaudRateType = typing.Literal[9600, 115_200, 1_000_000]
"""Valeurs permises pour les débits de communication série.

Il s'agit toujours de la valeur maximale à laquelle un système s'attends à
recevoir de l'information. Les débits de 9600 et 115200 sont les plus répandus.
Un débit de 1000000 ne devrait pas être utilisé en dehors d'application
nécessitant un échantillonage à haute fréquence.
"""


class LigneSerie:
    """Classe de lien série."""

    __logger = logging.getLogger(f'{__name__}.LigneSerie')
    """Journal de débogage pour les objets de classe LigneSerie."""

    __logger.addHandler(logging.NullHandler())

    def __init__(
        self,
        port: str = 'loop://',
        baudrate: BaudRateType = 115_200,
        *,
        stop_event: threading.Event | None = None,
    ) -> None:
        """Initialise un lien série.

        Ouvre une connexion à une ligne série au port :obj:`!port` et
        débit :obj:`!baudrate`.

        Parameters
        ------------------
        port
            Port auquel se connecter. Voir :external+serial:ref:`URLs`.
        baudrate
            Débit maximal attendu pour la communication.
        stop_event
            Un objet :class:`threading.Event` permettant de signaler
            l'arrêt de la communication et de fermer la connexion.
        """
        thread_name = str(port) if port is not None else None

        self.__thread: threading.Thread = threading.Thread(
            group=None,
            target=self.__run,
            name=f'{thread_name}',
            daemon=None,
            context=None,
        )
        """Objet :class:`threading.Thread` propre à cette ligne série."""

        self.__logger.debug('%s', self.__thread)

        self.__serial: serial.Serial = serial.serial_for_url(
            port, do_not_open=True
        )
        """Objet :class:`serial.Serial` propre à cette ligne série."""

        self.__serial.baudrate = baudrate
        self.__serial.timeout = 1.0
        self.__logger.debug('%s', self.__serial)

        self.__input: queue.Queue = queue.Queue()
        """File :class:`queue.Queue` d'entrée."""

        self.__logger.debug('%s', self.__input)

        self.__output: queue.Queue = queue.Queue()
        """File :class:`queue.Queue` de sortie."""

        self.__logger.debug('%s', self.__output)

        self.__arret: threading.Event = (
            threading.Event() if stop_event is None else stop_event
        )
        """Signal d'arrêt pour la ligne série."""

        self.__logger.debug('%s', self.__arret)

        self.__loquet: threading.Lock = threading.Lock()
        """Loquet de synchronisation pour la ligne série."""

        self.__logger.debug('%s', self.__loquet)

    def print(
        self, data: str | list[dict[str, int | str]], *, end: str = '\n'
    ) -> None:
        """Envoyer :obj:`!data` via la ligne série.

        Permet d'envoyer des données selon deux formats, soit un
        :class:`str`, soit une liste de dictionnaires, dont les clés
        sont des :class:`str` et les éléments sont des :class:`int`.

        Parameters
        ------------------
        data
            Les informations à transmettre.
        end
            Le caractère de fin d'instruction à envoyer.

        Raises
        ------------------
        TypeError
            Quand :obj:`!data` n'est pas du bon type.

        Examples
        ------------------
        >>> com.print('allo monde')

        >>> com.print([{'A2': 120, '13': 255}])

        """
        self.__logger.debug('%s (%s)', repr(data), type(data))
        if isinstance(data, list):
            self.__logger.debug('data is list')
            if all(isinstance(x, dict) for x in data):
                self.__logger.debug('data is list[dict]')
                if all(all(isinstance(x, str) for x in d) for d in data):
                    self.__logger.debug('data is list[dict[str]]')
                    data = '\n'.join(
                        '\t'.join(f'{k}:{v}' for k, v in d.items())
                        for d in data
                    )

        if isinstance(data, str):
            self.__logger.debug('Queueing %r', data)
            self.__input.put((data + end).encode('utf-8'))
        else:
            msg: str = f'Expected {str} or {list[dict]} but got {type(data)}.'
            raise TypeError(msg)

    def __run(self) -> None:
        """Fonction exécutée dans un autre fil."""
        self.__logger.debug('')
        while True:
            # Si l'événement d'arrêt a été déclenché, on sort de la boucle.
            if self.__arret.is_set():
                self.__logger.debug('%s', self.__arret)
                return

            # Si on a:
            #  - quelque chose à lire
            #  - et rien en attente d'être envoyé
            # on peut envoyer la ligne suivante.
            if not self.__input.empty() and not self.__serial.out_waiting:
                try:
                    cmd: bytes = self.__input.get()
                    self.__logger.debug('%r', cmd)
                except queue.ShutDown as err:
                    self.__arret.set()
                    self.__logger.debug('%s', self.__arret, exc_info=err)
                except KeyboardInterrupt as err:
                    self.__arret.set()
                    self.__logger.debug('%s', self.__arret, exc_info=err)
                else:
                    with self.__loquet:
                        self.__serial.write(cmd)
                        self.__input.task_done()

            # Si on a:
            #  - de la place dans la file de sortie
            #  - et des données à lire
            # on lit la ligne suivante.
            if not self.__output.full() and self.__serial.in_waiting:
                with self.__loquet:
                    val: bytes = self.__serial.read_until(b'\n')
                    self.__logger.debug('%s', val)

                try:
                    self.__output.put(val)
                except queue.ShutDown as err:
                    self.__arret.set()
                    self.__logger.debug('%s', self.__arret, exc_info=err)
                except KeyboardInterrupt as err:
                    self.__arret.set()
                    self.__logger.debug('%s', self.__arret, exc_info=err)

    def __enter__(self) -> Self:
        """Ouvre la ligne série et démarre l'exécution du fil parallèle.

        Returns
        ---------------
        self
            Les objets :class:`LigneSerie` sont des gestionnaires de contexte.

        See Also
        ---------------
        with : gestion de contexte, :keyword:`with`
            (:external+python:ref:`context-managers`).
        __exit__ : sortie de contexte.

        Examples
        ---------------
        >>> with LigneSerie() as com:
        ...     pass

        """
        self.__serial.open()
        self.__logger.debug('%s', self.__serial)
        self.__thread.start()
        self.__logger.debug('%s', self.__thread)
        return self

    def __exit__(
        self,
        typ: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        """Ferme les files, fils et ligne série.

        Returns
        ---------------
        None
            Si aucune exception n'a été passée en argument.
        True
            Pour indiquer qu'il faut re-soulever l'erreur quand il y en a
            une.

        See Also
        ---------------
        with : gestion de contexte, :keyword:`with`
            (:external+python:ref:`context-managers`).
        __enter__ : entrée de contexte.

        Examples
        ---------------
        >>> with LigneSerie as com:
        ...     pass

        """
        if typ is not None:
            self.__logger.warning('', exc_info=exc)

        self.__input.shutdown()
        self.__logger.debug('%s', self.__input)

        self.__thread.join(timeout=1.0)
        self.__logger.debug('%s', self.__thread)

        if self.__thread.is_alive():
            self.__arret.set()
            self.__logger.debug('%s', self.__arret)

        self.__thread.join()
        self.__logger.debug('%s', self.__thread)

        self.__serial.close()
        self.__logger.debug('%s', self.__serial)

        self.__output.shutdown()
        self.__logger.debug('%s', self.__output)

        return None if typ is None else True

    def __next__(self) -> str:
        """Retourne l'élément suivant reçu sur la ligne série.

        Returns
        ---------------
        val : str
            Valeur suivante reçue sur la ligne série.
            Convertie en chaîne sans caractère de fin de ligne.
        None
            Valeur retournée si il n'y a plus de valeurs à lire,
            mais que la ligne série est encore ouverte.

        Raises
        ---------------
        StopIteration
            Quand il n'y a plus rien à retourner et que la ligne série
            est fermée.

        See Also
        ---------------
        next : Fonction d'itération
        iter : Pour obtenir l'itérateur d'un objet.
        for : Boucles :keyword:`for`.

        Examples
        ---------------
        >>> next(com)
        '{"14":255}'

        >>> for l in com:
        ...     print(l)
        {'13': 255}
        {'13': 0}
        {'13': 255}
        {'13': 0}

        """
        try:
            val: bytes = self.__output.get(block=True)
        except queue.ShutDown as err:
            self.__logger.warning('Stopping iteration.', exc_info=err)
            raise StopIteration from err
        except queue.Empty as err:
            self.__logger.warning('Nothing received.', exc_info=err)
            return None
        else:
            self.__logger.info('%s', val)
            self.__output.task_done()
            val: str = val.decode('utf-8').strip()
            return val

    def __iter__(self) -> Self:
        """Retourne self."""  # noqa: DOC201
        return self

    def parse(self) -> iter[dict[str, float]]:
        """Renvoie un dictionnaire par ligne au format du traceur Arduino.

        Prends une ligne de texte au format ``A1:244 A2:32`` et retourne
        un dictionnaire :code:`{'A1': 244, 'A2': 32}`.

        Yields
        ---------------
        : dict[str, float]
            Un dictionnaire correspondant aux valeurs renvoyées par le
            micro-contrôleur sur la ligne série.

        Examples
        ---------------
        >>> df = pandas.DataFrame()
        >>> for l in com.parse():
        ...     df = pandas.concat(df, pandas.Series(l))
        >>> print(df.head())
        """
        yield from (
            {k: float(v) for k, v in (w.split(':') for w in ligne.split('\t'))}
            for ligne in self
            if ligne is not None
        )

    def close(self):
        self.__arret.set()
        self.__input.shutdown()

    def __str__(self) -> str:
        """Retourne une :class:`str` représentant l'objet."""  # noqa: DOC201
        return str(self.__serial)

    def __repr__(self) -> str:
        """Retourne une description d'un :class:LigneSerie."""  # noqa: DOC201
        return f'LigneSerie<{hex(id(self))}>({self.__serial}, {self.__thread})'


class Appareil(LigneSerie):
    """Classe abstraite permettant de se connecter automatiquement."""

    APPAREIL: str = 'hwgrep://&skip_busy'
    """URL de connexion désignant le prochain port série libre."""

    def __init__(
        self,
        port: str | None = None,
        baudrate: BaudRateType = 115_200,
        *,
        stop_event: threading.Event | None = None,
    ) -> None:
        """Classe abstraite pour la connexion automatique à un appareil.

        .. warning::

            Cette classe ne devrait pas être utilisée directement.
            Utilisez une sous-classe comme :class:`ArduinoNanoEvery`.

        See Also
        ---------------
        LigneSerie : classe parente.
        ArduinoNanoEvery : classe concrète pour le Arduino Nano Every.
        serial.Serial : Voir :external+serial:ref:`URLs`.

        Examples
        ---------------
        >>> class Arduino(Appareil):
        ...     APPAREIL = 'hwgrep://Arduino&skip_busy'
        >>> with Arduino() as ard:
        ...     ard.print('allo')
        ...     print(next(ard))

        """
        if port is None:
            port: str = self.APPAREIL

        super().__init__(port, baudrate=baudrate, stop_event=stop_event)


class ArduinoNanoEvery(Appareil):
    """Classe pour la connexion automatique à un Arduino Nano Every.

    Basée sur :class:`Appareil`. Se connecte automatiquement au
    prochain Arduino Nano Every disponible.
    """

    APPAREIL: str = 'hwgrep://Arduino Nano Every&skip_busy'
    """URL de connexion désignant le prochain Arduino Nano Every disponible."""

    def __init__(
        self,
        port: str | None = None,
        baudrate: BaudRateType = 115_200,
        *,
        stop_event: threading.Event | None = None,
    ) -> None:
        """Classe pour la connexion automatique à un Arduino Nano Every.

        Basée sur :class:`Appareil`. Se connecte automatiquement au
        prochain Arduino Nano Every disponible.

        See Also
        ---------------
        LigneSerie : classe parente.
        Appareil : classe abstraite pour la connexion automatique à un
            appareil.
        serial.Serial : Voir :external+serial:ref:`URLs`.

        Examples
        ---------------
        >>> with ArduinoNanoEvery() as ard:
        ...     ard.print('allo')
        ...     print(next(ard))
        """
        super().__init__(port, baudrate, stop_event=stop_event)


def main(*, debug: bool = False) -> None:
    """Exemple d'écho série.

    Crée une ligne série avec les valeurs par défaut de :class:`LigneSerie`.
    Les données sont envoyées avec :func:`LigneSerie.print`, et lues
    avec :func:`LigneSerie.parse`.
    """
    from pprint import pprint  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415

    if debug:
        __logger.setLevel(logging.DEBUG)
        __handler = logging.StreamHandler()
        fmt: str = (
            '%(levelname)s\t'
            '%(threadName)s\t'
            '%(funcName)s (%(lineno)s)\t'
            '%(message)s'
        )
        __formatter = logging.Formatter(fmt)
        __handler.setFormatter(__formatter)
        __logger.addHandler(__handler)

    seed = 1903
    gna = np.random.default_rng(seed=seed)

    N: int = 10
    incert: float = 0.001
    ts = np.arange(N) + gna.normal(0, incert, N)
    xs = np.arange(N) + gna.normal(0, incert, N)
    ys = (np.arange(N) + gna.normal(0, incert, N))**2
    zs = (np.arange(N) + gna.normal(0, incert, N))**2
    lignes = [{'t': t, 'x': x, 'y': y, 'z': z} for t, x, y, z in zip(ts, xs, ys, zs)]
    __logger.debug('%s', lignes)

    with LigneSerie() as com:
        com.print(lignes)

    data = list(com.parse())
    print('Position')
    print('===========================')
    print()
    pprint(data)
    print()


if __name__ == '__main__':
    main(debug=True)
