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
        self.__port = port
        self.__baudrate = baudrate
        self.__timeout = 0.05

        self.__arret: threading.Event = (
            threading.Event() if stop_event is None else stop_event
        )
        """Signal d'arrêt pour la ligne série."""

        self.__logger.debug('%s', self.__arret)
        self.__loquet: threading.Lock = threading.Lock()
        """Loquet de synchronisation pour la ligne série."""

        self.__logger.debug('%s', self.__loquet)

        self.__reset()

    @property
    def device(self) -> str:
        """Retourne le port série."""
        return self.__serial.port

    @property
    def port(self) -> str:
        """Retourne le port série."""
        return self.__serial.port

    @property
    def baudrate(self) -> int:
        """Retourne le débit maximal de communication attendu."""
        return self.__serial.baudrate

    @property
    def sending(self) -> bool:
        """Vérifie s'il reste des données à envoyer."""
        return not self.__input.empty()

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
        self.__logger.debug(
            'len(data) = %s, type(data) = %s', len(data), type(data)
        )
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
            self.__input.put((data + end).encode('utf-8'))
        else:
            msg: str = f'Expected {str} or {list[dict]} but got {type(data)}.'
            raise TypeError(msg)

    def __run(self) -> None:
        """Fonction exécutée dans un autre fil."""
        self.__logger.debug('')
        while not self.__arret.is_set():
            # Si on a:
            #  - quelque chose à lire
            #  - et rien en attente d'être envoyé
            # on peut envoyer la ligne suivante.
            if not self.__input.empty() and not self.__serial.out_waiting:
                try:
                    cmd: bytes = self.__input.get()
                    self.__logger.debug('len(cmd) = %s', len(cmd))
                except queue.ShutDown as err:
                    self.__logger.debug('self.__input fermé', exc_info=err)
                    break
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
                    val: bytes = self.__serial.read_until(b'\n', size=100)
                    self.__logger.debug('len(val) = %s', len(val))

                if val.endswith(b'\n'):
                    val = self.__temp_val + val
                    self.__temp_val = b''
                else:
                    self.__temp_val += val
                    val = b''

                try:
                    if len(val) > 0:
                        self.__output.put(val)
                except queue.ShutDown as err:
                    self.__logger.debug('self.__output fermé', exc_info=err)
                    break

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
        self.open()
        return self

    def open(self) -> None:
        """Ouvre la connexion série."""
        self.__input: queue.Queue = queue.Queue()
        self.__output: queue.Queue = queue.Queue()
        self.__serial.open()
        self.__logger.debug('%s', self.__serial)
        self.__thread.start()
        self.__logger.debug('%s', self.__thread)
        self.__open = True

    @property
    def is_open(self) -> bool:
        """Vérifie si la connexion est ouverte.

        Returns
        ---------------
        self.__open: bool
            Variable indiquant si la connexion est ouverte.
        """
        return self.__open

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

        self.close()

        return False  # Re-raise the exception please

    def close(self) -> None:
        """Ferme la connexion série."""
        self.__logger.debug('')
        self.__logger.debug('%s', self.__open)

        if self.__open:
            self.__arret.set()
            self.__logger.debug('%s', self.__arret)

            self.__thread.join()
            self.__logger.debug('%s', self.__thread)

            del self.__thread

            self.__serial.close()
            self.__logger.debug('%s', self.__serial)
            del self.__serial

            self.__input.shutdown()
            self.__output.shutdown()
            self.__open = False

        self.__logger.debug('%s', self.__open)
        self.__reset()

    def __reset(self) -> None:
        self.__logger.debug('')

        self.__thread: threading.Thread = threading.Thread(
            group=None,
            target=self.__run,
            name=f'{self.__port}',
            daemon=None,
            context=None,
        )
        """Objet :class:`threading.Thread` propre à cette ligne série."""

        self.__logger.debug('%s', self.__thread)

        self.__serial: serial.Serial = serial.serial_for_url(
            self.__port, do_not_open=True
        )
        """Objet :class:`serial.Serial` propre à cette ligne série."""

        self.__serial.baudrate = self.__baudrate
        self.__serial.timeout = self.__timeout
        self.__logger.debug('%s', self.__serial)

        self.__open = False
        self.__temp_val = b'\n'

        if self.__arret.is_set():
            self.__arret.clear()
        self.__logger.debug('%s', self.__arret)

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
            val: bytes = self.__output.get(timeout=0.01)
        except queue.ShutDown as err:
            self.__logger.debug('self.__output fermé', exc_info=err)
            raise StopIteration from err
        except queue.Empty as err:
            self.__logger.debug('self.__output vide', exc_info=err)
            return None
        else:
            self.__logger.info('len(val) = %s', len(val))
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
        for ligne in self:
            if ligne is not None:
                if '\t' in ligne:
                    items = ligne.split('\t')

                    if all((':' in mot) for mot in items):
                        yield {
                            k: float(v)
                            for k, v in (mot.split(':') for mot in items)
                        }
                        continue

            yield None

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
        from .logging import DEBUG, config  # noqa: PLC0415

        config(__name__, level=DEBUG)

    seed = 1903
    gna = np.random.default_rng(seed=seed)

    n: int = 10
    incert: float = 0.001
    ts = np.arange(n) + gna.normal(0, incert, n)
    xs = np.arange(n) + gna.normal(0, incert, n)
    ys = (np.arange(n) + gna.normal(0, incert, n)) ** 2
    zs = (np.arange(n) + gna.normal(0, incert, n)) ** 2
    lignes = [
        {'t': t, 'x': x, 'y': y, 'z': z}
        for t, x, y, z in zip(ts, xs, ys, zs, strict=True)
    ]
    __logger.debug('len(lignes) = %s', len(lignes))

    with LigneSerie() as com:
        com.print(lignes)

        while com.sending:
            pass

    print()

    data = [x for x in com.parse() if x is not None]
    print('Position')
    print('===========================')
    print()
    pprint(data)
    print()


if __name__ == '__main__':
    main(debug=True)
