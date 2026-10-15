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

import contextlib
import multiprocessing
import queue
import time
import typing

import numpy as np
import serial

from .dummy import signal as dummy_signal
from .exceptions import (
    CouldNotConnectToSerialPortError,
    WrongSerialInputTypeError,
)
from .logging import DEBUG, WithLogger, basicConfig, info
from .multiprocessing import Synchronisateur, Processus

if typing.TYPE_CHECKING:
    from types import TracebackType
    from typing import Final, Self

type BaudRateType = typing.Literal[9600, 115_200, 1_000_000]
"""Valeurs permises pour les débits de communication série.

Il s'agit toujours de la valeur maximale à laquelle un système s'attends à
recevoir de l'information. Les débits de 9600 et 115200 sont les plus répandus.
Un débit de 1000000 ne devrait pas être utilisé en dehors d'application
nécessitant un échantillonage à haute fréquence.
"""

TIMEOUT: Final[int] = 1
"""Valeur globale des délais maximaux pour la communication."""

KEY_VAL_SEP = ":"
"""Séparateur entre clé et valeur dans la notation série Arduino."""

VAL_SEP = "\t"
"""Séparateur en les valeurs dans la notation série Arduino."""


class LigneSerie(Processus):
    """Classe de lien série."""

    def __init__(
        self,
        port: str = "loop://",
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
        self.__timeout = TIMEOUT
        self.__open = False
        super().__init__(stop_event=stop_event, lock=lock)

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

    def print(
        self,
        data: str | list[dict[str, int | str]],
        *,
        end: str = "\n",
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
        >>> com.print("allo monde")

        >>> com.print([{"A2": 120, "13": 255}])

        """  # noqa: DOC502
        if (
            isinstance(data, list)
            and all(isinstance(x, dict) for x in data)
            and all(all(isinstance(x, str) for x in d) for d in data)
        ):
            data = end.join(
                "\t".join(f"{k}:{v}" for k, v in d.items()) for d in data
            )

        super().print(data, end=end, block=block)

    def open(self) -> None:
        """Ouvre la connexion série."""
        self.start(
            name=self.__port,
            args=(self.__port, self.__baudrate, self.__timeout),
        )
        self.__open = True

    @classmethod
    def setup(
        cls: type[LigneSerie],
        port: str,
        baudrate: BaudRateType,
        timeout: float,  # noqa: ARG003
        sync: Synchronisateur,
    ) -> (serial.Serial, bytes):
        """Initialise la communication série.

        Returns
        --------------
        ser: serial.Serial, b""
            La connexion série et la valeur initiale.
        """
        ser = serial.serial_for_url(port, do_not_open=True)
        ser.baudrate = baudrate
        ser.timeout = TIMEOUT

        with sync, contextlib.suppress(Exception):
            ser.open()

        if not ser.is_open:
            err = CouldNotConnectToSerialPortError(port)
            sync.logqueue.put(err)
            sync.stop()
        else:
            ser.read_until(b"\n")

        return ser, b""

    @staticmethod
    def write_out(
        ser: serial.Serial,
        sync: Synchronisateur,
    ) -> None:
        """Envoie un message de la file d'entrée à la ligne série."""
        try:
            cmd: bytes = sync.inqueue.get()
        except ValueError as e:
            sync.logqueue.put(e)
            sync.stop()
        else:
            with sync:
                ser.write(cmd)
            sync.inqueue.task_done()

    @staticmethod
    def send_out(
        val: bytes,
        sync: Synchronisateur,
    ) -> bytes:
        """Rend un message reçu disponible pour next.

        Returns
        -------------
        b""
            Une valeur vierge pour val dans loop.
        """
        try:
            sync.outqueue.put(val)
        except (ValueError, queue.Full) as e:
            sync.logqueue.put(e)
            sync.stop()

        return b""

    @staticmethod
    def read_in(ser: serial.Serial, sync: Synchronisateur) -> bytes:
        """Lire une valeur de la ligne série.

        Returns
        ---------
        val: bytes
            La valeur lue.
        """
        with sync:
            val = ser.read_until(b"\n")

        return val  # noqa: RET504

    @classmethod
    def loop(
        cls: type[Self],
        ser: serial.Serial,
        val: bytes,
        sync: Synchronisateur,
    ) -> bytes:
        """Exécute une itération de suivi de la ligne série.

        Parameters
        ------------
        ser: serial.Serial
            Objet de connexion série.
        val: bytes
            Dernière valeur.
        sync: Synchronisateur
            Objet de communication et synchronisation.

        Returns
        ------------
        val: bytes
            La valeur lue dans cette itération.
        """
        if not sync.inqueue.empty() and not ser.out_waiting:
            cls.write_out(ser, sync)

        if len(val) > 0:
            val = cls.send_out(val, sync)

        if not sync.outqueue.full() and ser.in_waiting:
            val = cls.read_in(ser, sync)

        return val

    @classmethod
    def run(
        cls: type[Self],
        port: str,
        baudrate: BaudRateType,
        timeout: float,
        sync: Synchronisateur,
    ) -> None:
        """Gère la connexion série dans un autre processus."""
        # Normalement les modules sont importés dans l'espace de nom
        # global en début de fichier. serial est importé ici pour
        # réduire les possibilités de problèmes avec multiprocessing
        # en exécutant l'entièreté du code concernant serial dans le
        # même processus.
        ser, val = cls.setup(
            port,
            baudrate,
            timeout,
            sync,
        )

        with contextlib.suppress(KeyboardInterrupt):
            while not sync.is_stopped:  # pylint: disable=W0149
                val = cls.loop(ser, val, sync)

        ser.close()

    @property
    def is_open(self) -> bool:
        """Vérifie si la connexion est ouverte.

        Returns
        ---------------
        self.__open: bool
            Variable indiquant si la connexion est ouverte.
        """
        self.checkin()

        return self.__open and self.is_alive

    def next(
        self,
        *,
        block: bool = True,
        timeout: float = TIMEOUT,
        parse: bool = False,
    ) -> str | dict:
        """Retourne le prochain élément reçu.

        Parameters
        --------------
        block: bool = True
            Si on attend le prochain élément, ou si on retourne None.
        parse: bool = False
            Analyse le résultat et retourne le dictionnaire.

        Returns
        ----------
        str
            Les données en UTF-8.
        dict
            Les données en format tabulaire.
        """
        self.checkin()

        val = super().next(block=block, timeout=timeout)
        self.debug("val = %r", val)

        if not parse:
            return val

        if val is None:
            return {}

        d = {}
        if VAL_SEP in val:
            items = val.split(VAL_SEP)

            if all((KEY_VAL_SEP in mot) for mot in items):
                for k, v in (mot.split(KEY_VAL_SEP) for mot in items):
                    if k.isprintable():
                        try:
                            res = float(v)
                        except ValueError:
                            d[k] = np.nan
                        else:
                            d[k] = res

        return d

    def close(self) -> None:
        """Fermer la connexion série."""
        self.__open = False
        super().close()

    def parse(self, *, block: bool = True) -> dict[str, float]:
        """Renvoie un dictionnaire par ligne au format du traceur Arduino.

        Prends une ligne de texte au format ``A1:244 A2:32`` et retourne
        un dictionnaire :code:`{'A1': 244, 'A2': 32}`.

        Parameters
        ---------------
        block: bool = False
            Si on attend chaque ligne.

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

        while True:  # pylint: disable=W0149
            yield self.next(block=block, parse=True)

    def __repr__(self) -> str:
        """Retourne une description d'un :class:LigneSerie.

        Returns
        ---------------
        str
            Sommaire de la connexion.
            ``LigneSerie<<id>> to <port> [on <thread>]
        """
        self.checkin()

        if self.is_open:
            return f"LigneSerie<{hex(id(self))}> to {self.__port} (active)"

        return f"LigneSerie<{hex(id(self))}> to {self.__port}"


class Appareil(LigneSerie):
    """Classe abstraite permettant de se connecter automatiquement."""

    @property
    def APPAREIL(self) -> str:  # noqa: N802  # pylint: disable=C0103
        """Addresse utilisée pour l'appareil.

        Returns
        ---------------
        'hwgrep://&skip_busy'
            Adresse indiquant n'importe quel appareil disponible.
        """
        return "hwgrep://&skip_busy"

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
        ...     APPAREIL = "hwgrep://Arduino&skip_busy"
        >>> with Arduino() as ard:
        ...     ard.print("allo")
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

    @property
    def APPAREIL(self) -> str:  # noqa: N802
        """Addresse utilisée pour l'appareil.

        Returns
        ---------------
        'hwgrep://Arduino Nano Every&skip_busy'
            Adresse indiquant n'importe quel appareil disponible.
        """
        import platform  # noqa: PLC0415

        if platform.system() == "Windows":
            return "hwgrep://&skip_busy"

        return "hwgrep://Arduino Nano Every&skip_busy"


def print_ports() -> None:
    """Affiche les ports série disponibles."""
    from serial.tools.list_ports import (  # noqa: PLC0415
        comports,
    )  # pylint: disable=C0415

    for p in comports():
        print(p.device, p.description, p.hwid, sep="\t")


def no_op(*, debug: bool = False) -> None:
    """Ouvre et referme une connexion locele.

    Parameters
    ---------------
    debug: bool = False
        Si la journalisation de débogage est activée.
    """
    if debug:
        basicConfig(DEBUG)

    with LigneSerie() as com:
        info("Connecté à %r.", com)
        time.sleep(1)

    info("Fin.")


def echo(*, debug: bool = False) -> None:
    """Envoie et reçoit du texte sans connexion externe.

    Parameters
    ---------------
    debug: bool = False
        Si la journalisation de débogage est activée.
    """
    if debug:
        basicConfig(DEBUG)

    with LigneSerie() as com:
        info("Connecté à %r.", com)
        while True:  # pylint: disable=W0149
            try:  # pylint: disable=W0717
                com.print(input(">>>"))
                print(com.next(block=True))
            except KeyboardInterrupt:
                break

    info("Fin.")


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
        basicConfig(DEBUG)

    with ArduinoNanoEvery(baudrate=9600) as com:
        info("Connecté à %r.", com)
        while True:  # pylint: disable=W0149
            try:  # noqa: W0717
                com.print(input(">>>"))
                print(com.next(block=True))
            except KeyboardInterrupt:
                break

    info("Fin.")


def echodata(*, debug: bool = False) -> None:
    """Envoie et reçoit un signal simulé.

    Parameters
    ---------------
    debug: bool = False
        Si la journalisation de débogage est activée.
    """
    if debug:
        basicConfig(DEBUG)

    with LigneSerie() as com:
        info("Connecté à %r.", com)
        for sig in dummy_signal():
            try:  # noqa: W0717
                com.print(sig)
                print(com.next(block=True, parse=True))
            except KeyboardInterrupt:
                break

    info("Fin.")


def arddata(*, debug: bool = False) -> None:
    """Reçoit des données depuis un Arduino Nano Every.

    Parameters
    ---------------
    debug: bool = False
        Si la journalisation de débogage est activée.
    """
    if debug:
        basicConfig(DEBUG)

    with ArduinoNanoEvery(baudrate=9600) as com:
        info("Connecté à %r.", com)
        while True:  # pylint: disable=W0149
            try:
                print(com.next(block=True, parse=True))
            except KeyboardInterrupt:
                break

    info("Fin.")


__all__ = ["Appareil", "ArduinoNanoEvery", "LigneSerie"]
