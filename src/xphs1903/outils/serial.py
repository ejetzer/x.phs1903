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

import multiprocessing
import queue
import time
import typing

from .dummy import signal as dummy_signal
from .exceptions import (
    ParsableArduinoSerialDataError,
    WrongSerialInputTypeError,
)
from .functools import staticproperty
from .logging import WithLogger

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


class LigneSerie(WithLogger):
    """Classe de lien série."""

    def __init__(
        self,
        port: str = 'loop://',
        baudrate: BaudRateType = 115_200,
        *,
        stop_event: multiprocessing.Event | None = None,
        lock: multiprocessing.Lock | None = None,
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
        self.checkin()

        self.__port = port
        self.__baudrate = baudrate
        self.__timeout = 0.005

        self.__arret: multiprocessing.Event = (
            multiprocessing.Event() if stop_event is None else stop_event
        )
        """Signal d'arrêt pour la ligne série."""

        self.debug('%s', self.__arret)

        self.__loquet: multiprocessing.Lock = (
            multiprocessing.Lock() if lock is None else lock
        )
        """Loquet de synchronisation pour la ligne série."""

        self.debug('%s', self.__loquet)

        self.__reset()

    @property
    def device(self) -> str:
        """Retourne le port série."""
        self.checkin()
        return self.__port

    @property
    def port(self) -> str:
        """Retourne le port série."""
        self.checkin()
        return self.__port

    @property
    def baudrate(self) -> int:
        """Retourne le débit maximal de communication attendu."""
        self.checkin()
        return self.__baudrate

    @property
    def sending(self) -> bool:
        """Vérifie s'il reste des données à envoyer."""
        self.checkin()
        return not self.__input.empty()

    @property
    def holding(self) -> bool:
        """Vérifie s'il reste des données à lire."""
        self.checkin()
        return not self.__output.empty()

    def print(
        self,
        data: str | list[dict[str, int | str]],
        *,
        end: str = '\n',
        block: bool = True,
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
        WrongSerialInputTypeError(data)
            Quand :obj:`!data` n'est pas du bon type.

        Examples
        ------------------
        >>> com.print('allo monde')

        >>> com.print([{'A2': 120, '13': 255}])

        """  # noqa: DOC502
        self.checkin()
        self.debug('len(data) = %s, type(data) = %s', len(data), type(data))

        if (
            isinstance(data, list)
            and all(isinstance(x, dict) for x in data)
            and all(all(isinstance(x, str) for x in d) for d in data)
        ):
            data = end.join(
                '\t'.join(f'{k}:{v}' for k, v in d.items()) for d in data
            )

        if isinstance(data, str):
            try:
                self.__input.put((data + end).encode('utf-8'), block=block)
            except queue.Full as err:
                self.debug(
                    'input.full()=%s', self.__input.full(), exc_info=err
                )
        else:
            raise WrongSerialInputTypeError(data)

    @staticmethod
    def ligne_serie_run(  # noqa: PLR0917, PLR0913
        port: str,
        baudrate: BaudRateType,
        timeout: float,
        arret: multiprocessing.Event,
        input: multiprocessing.Queue,  # noqa: A002
        output: multiprocessing.Queue,
        loquet: multiprocessing.Lock,
    ) -> None:
        """Fonction exécutée dans un autre fil.

        Raises
        ----------------------
        RuntimeError
            Si le contenu reçu n'a pas la bonne longueur.
        """
        import serial  # noqa: PLC0415

        ser = serial.serial_for_url(port, do_not_open=True)
        """Objet :class:`serial.Serial` propre à cette ligne série."""

        ser.baudrate = baudrate
        ser.timeout = timeout

        with loquet:
            ser.open()

        temp_val: bytes = b''
        val: bytes = b''

        while not arret.is_set():
            if not input.empty() and not ser.out_waiting:
                try:
                    cmd: bytes = input.get()
                except ValueError:
                    break
                else:
                    with loquet:
                        ser.write(cmd)
                    input.task_done()

            if len(val) > 0:
                try:
                    output.put(val, block=False)
                except ValueError:
                    break
                else:
                    val = b''
            elif not output.full() and ser.in_waiting:
                max_size: int = 100
                with loquet:
                    val = ser.read_until(b'\n', size=max_size)

                if val.endswith(b'\n'):
                    val = temp_val + val
                    temp_val = b''
                elif len(val) == max_size:
                    temp_val += val
                    val = b''

        ser.close()

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
        self.checkin()

        self.__input: multiprocessing.Queue = multiprocessing.JoinableQueue()
        self.__output: multiprocessing.Queue = multiprocessing.JoinableQueue()

        self.__thread: multiprocessing.Process = multiprocessing.Process(
            group=None,
            target=self.ligne_serie_run,
            args=(
                self.__port,
                self.__baudrate,
                self.__timeout,
                self.__arret,
                self.__input,
                self.__output,
                self.__loquet,
            ),
            name=f'{self.__port}',
            daemon=True,
        )
        """Objet :class:`threading.Thread` propre à cette ligne série."""

        self.__thread.start()
        self.debug('%s', self.__thread)
        self.__open = True

    @property
    def is_open(self) -> bool:
        """Vérifie si la connexion est ouverte.

        Returns
        ---------------
        self.__open: bool
            Variable indiquant si la connexion est ouverte.
        """
        self.checkin()

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
        self.checkin()

        if typ is not None:
            self.warning('', exc_info=exc)

        self.close()

        return False  # Re-raise the exception please

    def close(self) -> None:
        """Ferme la connexion série."""
        self.checkin()
        self.debug('%s', self.__open)

        if self.__open:
            self.__arret.set()
            self.debug('%s', self.__arret)

            self.__input.close()
            self.__output.close()

            self.__thread.join(timeout=0.005)
            self.debug('%s', self.__thread)

            if self.__thread.is_alive():
                self.__thread.interrupt()

            self.__open = False

        self.debug('%s', self.__open)
        self.__reset()

    def wait(self) -> None:
        self.checkin()

        while self.sending:
            continue

        while self.holding:
            continue

    def __reset(self) -> None:
        self.checkin()

        self.__open = False
        self.__temp_val = b'\n'

        if self.__arret.is_set():
            self.__arret.clear()
        self.debug('%s', self.__arret)

    def __next__(self) -> str:
        """Renvoie l'élément suiant reçu sur la ligne série."""  # noqa: DOC201
        return self.next()

    def next(
        self,
        *,
        block: bool = True,
        timeout: float | None = None,
        parse: bool = False,
    ) -> str | dict[str, float]:
        """Renvoie l'élément suiant reçu sur la ligne série.

        Parameters
        ---------------
        block: bool = True
            Si on attend la ligne suivante.
        timeout: float | None = None
            Combien de temps attendre une ligne.
        parse: bool = False
            Si on essait de convertir le résultat.

        Returns
        ---------------
        val: str
            Chaîne de caractères reçus.
        val: dict[str, float]
            Valeurs reçues.

        Raises
        ---------------
        ParsableArduinoSerialDataError(val)
            Si les données reçues n'ont pas le bon format.
        """  # noqa: DOC502
        self.checkin()

        try:
            val: bytes = self.__output.get(block=block, timeout=timeout)
        except queue.Empty:
            return None
        except ValueError:
            return None

        try:
            val: str = val.decode('utf-8')
        except UnicodeDecodeError:
            res = ''
            for c in val:
                try:
                    c = c.decode('utf-8')
                except UnicodeDecodeError:
                    c = '▮'
                finally:
                    res += c
            val = res
        else:
            val = val.strip()

        if not parse:
            return val

        if '\t' in val:
            items = val.split('\t')

            if all((':' in mot) for mot in items):
                return {
                    k: float(v) for k, v in (mot.split(':') for mot in items)
                }

        raise ParsableArduinoSerialDataError(val)

    def __iter__(self) -> iter:
        """Retourne un itérateur sur l'entrée série."""  # noqa: DOC201
        return self.iter()

    def iter(self, *, block: bool = False, timeout: int | None = None) -> str:
        """Retourne un itérateur sur série.

        Parameters
        ---------------
        block: bool = False
            Si on attend chaque ligne.
        timeout: float | None = None
            Combien de temps attendre une ligne.

        Yields
        ---------------
        val : str
            Valeur suivante reçue sur la ligne série.
            Convertie en chaîne sans caractère de fin de ligne.
        None
            Valeur retournée si il n'y a plus de valeurs à lire,
            mais que la ligne série est encore ouverte.

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
        self.checkin()

        while True:
            yield self.next(block=block, timeout=timeout)

    def parse(
        self, *, block: bool = True, timeout: int | None = 0.001
    ) -> dict[str, float]:
        """Renvoie un dictionnaire par ligne au format du traceur Arduino.

        Prends une ligne de texte au format ``A1:244 A2:32`` et retourne
        un dictionnaire :code:`{'A1': 244, 'A2': 32}`.

        Parameters
        ---------------
        block: bool = False
            Si on attend chaque ligne.
        timeout: float | None = None
            Combien de temps attendre une ligne.

        Yields
        ---------------
        dict[str, float]
            Un dictionnaire correspondant aux valeurs renvoyées par le
            micro-contrôleur sur la ligne série.

        Examples
        ---------------
        >>> df = pandas.DataFrame()
        >>> for l in com.parse():
        ...     df = pandas.concat(df, pandas.Series(l))
        >>> print(df.head())
        """
        self.checkin()

        while True:
            yield self.next(block=block, timeout=timeout, parse=True)

    def __repr__(self) -> str:
        """Retourne une description d'un :class:LigneSerie."""  # noqa: DOC201
        self.checkin()

        if self.is_open:
            return (
                f'LigneSerie<{hex(id(self))}> '
                f'to {self.__port} running on {self.__thread}'
            )

        return f'LigneSerie<{hex(id(self))}> to {self.__serial}'


class Appareil(LigneSerie):
    """Classe abstraite permettant de se connecter automatiquement."""

    @staticproperty
    def APPAREIL() -> str:  # noqa: N802
        """Addresse utilisée pour l'appareil.

        Returns
        ---------------
        'hwgrep://&skip_busy'
            Adresse indiquant n'importe quel appareil disponible.
        """
        return 'hwgrep://&skip_busy'

    def __init__(
        self,
        port: str | None = None,
        baudrate: BaudRateType = 115_200,
        *,
        stop_event: multiprocessing.Event | None = None,
        lock: multiprocessing.Lock | None = None,
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

        super().__init__(
            port, baudrate=baudrate, stop_event=stop_event, lock=lock
        )


class ArduinoNanoEvery(Appareil):
    """Classe pour la connexion automatique à un Arduino Nano Every.

    Basée sur :class:`Appareil`. Se connecte automatiquement au
    prochain Arduino Nano Every disponible.
    """

    @staticproperty
    def APPAREIL() -> str:  # noqa: N802
        """Addresse utilisée pour l'appareil.

        Returns
        ---------------
        'hwgrep://Arduino Nano Every&skip_busy'
            Adresse indiquant n'importe quel appareil disponible.
        """
        return 'hwgrep://Arduino Nano Every&skip_busy'


def no_op(*, debug: bool = False) -> None:
    """Ouvre et referme une connexion locele.

    Parameters
    ---------------
    debug: bool = False
        Si la journalisation de débogage est activée.
    """
    if debug:
        from .logging import DEBUG, config  # noqa: PLC0415

        config(__name__, level=DEBUG)

    with LigneSerie():
        time.sleep(1)


def echo(*, debug: bool = False) -> None:
    """Envoie et reçoit du texte sans connexion externe.

    Parameters
    ---------------
    debug: bool = False
        Si la journalisation de débogage est activée.
    """
    if debug:
        from .logging import DEBUG, config  # noqa: PLC0415

        config(__name__, level=DEBUG)

    with LigneSerie() as com:
        while True:
            try:
                com.print(input('>>>'))
                print(com.next(block=True))
            except KeyboardInterrupt:
                break


def ardecho(*, debug: bool = False) -> None:
    """Envoie et reçoit d'un Arduino en vérifiant l'écho.

    La fonction vérifie à chaque itération que la valeur
    transmise et la valeur reçue sont égales.

    Parameters
    ---------------
    debug: bool = False
        Si la journalisation de débogage est activée.
    """
    if debug:
        from .logging import DEBUG, config  # noqa: PLC0415

        config(__name__, level=DEBUG)

    with ArduinoNanoEvery(baudrate=9600) as com:
        while True:
            try:
                com.print(input('>>>'))
                print(com.next(block=True))
            except KeyboardInterrupt:
                break


def echodata(*, debug: bool = False) -> None:
    """Envoie et reçoit un signal simulé.

    Parameters
    ---------------
    debug: bool = False
        Si la journalisation de débogage est activée.
    """
    if debug:
        from .logging import DEBUG, config  # noqa: PLC0415

        config(__name__, level=DEBUG)

    with LigneSerie() as com:
        for sig in dummy_signal():
            try:
                com.print(sig)
                print(com.next(block=True, parse=True))
            except KeyboardInterrupt:
                break


def arddata(*, debug: bool = False) -> None:
    """Reçoit des données depuis un Arduino Nano Every.

    Parameters
    ---------------
    debug: bool = False
        Si la journalisation de débogage est activée.
    """
    if debug:
        from .logging import DEBUG, config  # noqa: PLC0415

        config(__name__, level=DEBUG)

    with ArduinoNanoEvery(baudrate=9600) as com:
        while True:
            try:
                print(com.next(block=True, parse=True))
            except KeyboardInterrupt:
                break


__all__ = ['Appareil', 'ArduinoNanoEvery', 'LigneSerie']
