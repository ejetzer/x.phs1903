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
    ParsableArduinoSerialDataError,
    WrongSerialInputTypeError,
)
from .functools import staticproperty
from .logging import DEBUG, WithLogger, basicConfig, info

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


class Processus(WithLogger):
    def __init__(
        self,
        *,
        stop_event: multiprocessing.Event | None = None,
        lock: multiprocessing.Lock | None = None,
    ) -> None:
        """Initialise le processus."""
        self.checkin()

        self.__arret: multiprocessing.Event = (
            multiprocessing.Event() if stop_event is None else stop_event
        )
        """Signal d'arrêt pour la ligne série."""

        self.debug("%s", self.__arret)

        self.__loquet: multiprocessing.Lock = (
            multiprocessing.Lock() if lock is None else lock
        )
        """Loquet de synchronisation pour la ligne série."""

        self.debug("%s", self.__loquet)

        self.reset()

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
        """Ouverture naïve, à surclasser."""
        self.start()

    @classmethod
    def run(
        cls: type[Self],
        arret: multiprocessing.Event,
        input_: multiprocessing.Queue,  # noqa: ARG003
        output: multiprocessing.Queue,  # noqa: ARG003
        loquet: multiprocessing.Lock,  # noqa: ARG003
        log_queue: multiprocessing.Queue,  # noqa: ARG003
    ) -> None:
        """Fonction à exécuter très simple, à surclasser."""
        cls.setup()

        while not arret.is_set():
            cls.loop()

    @classmethod
    def setup(cls: type[Self]) -> None:
        """Rien, à surclasser."""

    @classmethod
    def loop(cls: type[Self]) -> None:
        """Rien, à surclasser."""

    def start(self, name: str | None = None, *, args: tuple = ()) -> None:
        """Ouvre la connexion série."""
        self.checkin()

        self.__ctx: multiprocessing.Context = multiprocessing.get_context(
            method="spawn"
        )
        self.__input: multiprocessing.Queue = self.__ctx.JoinableQueue()
        self.__output: multiprocessing.Queue = self.__ctx.JoinableQueue()
        self.__log_queue: multiprocessing.Queue = self.__ctx.JoinableQueue()

        self.__thread: multiprocessing.Process = self.__ctx.Process(
            group=None,
            target=self.run,
            args=args
            + (
                self.__arret,
                self.__input,
                self.__output,
                self.__loquet,
                self.__log_queue,
            ),
            name=name,
            daemon=True,
        )
        """Objet :class:`threading.Thread` propre à cette ligne série."""

        self.__thread.start()
        self.debug("%s", self.__thread)

    @property
    def is_alive(self) -> bool:
        """Si le processus est actif."""
        return self.__thread.is_alive()

    def print(self, data: str, *, end: str = "\n", block: bool = True) -> None:
        """Envoie un message au processus."""
        self.checkin()
        self.debug("len(data) = %s, type(data) = %s", len(data), type(data))

        if isinstance(data, str):
            try:
                self.__input.put((data + end).encode("utf-8"), block=block)
            except queue.Full as err:
                self.debug(
                    "input.full()=%s", self.__input.full(), exc_info=err
                )
        else:
            raise WrongSerialInputTypeError(data)

    @property
    def serial_log(self) -> multiprocessing.Queue:
        """Les messages d'erreur du processus parallèle.

        Returns
        -------------
        multiprocessing.Queue
            La file contenant les messages d'erreur.
        """
        return self.__log_queue

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

        while not self.serial_log.empty():
            err = self.serial_log.get()
            self.warning("Erreur dans le processus parallèle:", exc_info=err)

        if typ is not None:
            self.warning("", exc_info=exc)

        self.close()

        return False  # Re-raise the exception please

    def close(self) -> None:
        """Ferme le processus."""
        self.checkin()

        if self.is_alive:
            self.__arret.set()
            self.debug("%s", self.__arret)

            self.__input.close()
            self.__output.close()
            self.__log_queue.close()

            self.__thread.join(timeout=0.005)
            self.debug("%s", self.__thread)

            if self.__thread.is_alive():
                self.__thread.interrupt()

        self.reset()

    def reset(self) -> None:
        """Réinitialise le processus."""
        self.checkin()

        if self.__arret.is_set():
            self.__arret.clear()

        self.__thread = None
        self.__ctx = None
        self.__input = None

        self.debug("%s", self.__arret)

    def wait(self) -> None:
        """Attends d'avoir vidé les files."""
        self.checkin()

        while self.sending:
            continue

        while self.holding:
            continue

    def __next__(self) -> str:
        """Renvoie l'élément suiant reçu sur la ligne série.

        Returns
        ---------------
        str
            Le résultat par défaut d'une itération:
                - Bloque l'exécution en attendant un item
                - Retourne le texte, pas les valeurs numériques.
        """
        return self.next()

    def next(
        self,
        *,
        block: bool = True,
        timeout: float | None = None,
    ) -> str | dict[str, float]:
        """Renvoie l'élément suiant reçu sur la ligne série.

        Parameters
        ---------------
        block: bool = True
            Si on attend la ligne suivante.
        timeout: float | None = None
            Combien de temps attendre une ligne.

        Returns
        ---------------
        val: str
            Chaîne de caractères reçus.

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
        else:
            self.__output.task_done()

        try:
            val: str = val.decode("utf-8")
        except UnicodeDecodeError:
            # Les erreurs d'encodage peuvent arriver quand le
            # débit de communication est mal réglé ou si les
            # interlocuteurs sont désynchronisés. Plutôt que
            # d'ignorer les caractères erronés silencieusement,
            # on les remplace ici par un caractère reconnaissable
            # comme indicateur de problème.

            res = ""

            # Ci-dessous, la variable c est redéfinie à l'intérieur de
            # la boucle. C'est un idiome fréquent en Python pour des
            # cas simples, il s'agit ici d'une boucle très simple
            # où les modifications n'ont pas d'effets secondaires
            # ou externes.
            for c in val:
                try:
                    c = bytes([c]).decode("utf-8")  # noqa: PLW2901
                except UnicodeDecodeError:
                    c = "▮"  # noqa: PLW2901
                finally:
                    res += c

            val = res
        finally:
            val = val.strip()

        return val

    def __iter__(self) -> iter:
        """Retourne un itérateur sur l'entrée série.

        Returns
        ---------------
        iter
            Un itérateur avec les paramètres par défaut:
                - Non bloquant, donc retourne parfois None.
        """
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
        self.__timeout = 0.005
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
    def setup(  # noqa: PLR0917, PLR0913
        cls: type[LigneSerie],
        port: str,
        baudrate: BaudRateType,
        timeout: float,
        arret: multiprocessing.Event,
        loquet: multiprocessing.Lock,
        log_queue: multiprocessing.Queue,
    ) -> (serial.Serial, bytes):
        """Initialise la communication série.

        Returns
        --------------
        ser: serial.Serial, b""
            La connexion série et la valeur initiale.
        """
        ser = serial.serial_for_url(port, do_not_open=True)
        ser.baudrate = baudrate
        ser.timeout = timeout

        with loquet, contextlib.suppress(Exception):
            ser.open()

        if not ser.is_open:
            err = CouldNotConnectToSerialPortError(port)
            log_queue.put(err)
            arret.set()

        ser.read_until(b"\n")

        return ser, b""

    @staticmethod
    def write_out(
        ser: serial.Serial,
        input_: multiprocessing.Queue,
        arret: multiprocessing.Event,
        loquet: multiprocessing.Lock,
        log_queue: multiprocessing.Queue,
    ) -> None:
        """Envoie un message de la file d'entrée à la ligne série."""
        try:
            cmd: bytes = input_.get()
        except ValueError as e:
            log_queue.put(e)
            arret.set()
        else:
            with loquet:
                ser.write(cmd)
            input.task_done()

    @staticmethod
    def send_out(
        val: bytes,
        output: multiprocessing.Queue,
        arret: multiprocessing.Event,
        log_queue: multiprocessing.Queue,
    ) -> bytes:
        """Rend un message reçu disponible pour next.

        Returns
        -------------
        b""
            Une valeur vierge pour val dans loop.
        """
        try:
            output.put(val)
        except (ValueError, queue.Full) as e:
            log_queue.put(e)
            arret.set()

        return b""

    @staticmethod
    def read_in(ser: serial.Serial, loquet: multiprocessing.Lock) -> bytes:
        """Lire une valeur de la ligne série.

        Returns
        ---------
        val: bytes
            La valeur lue.
        """
        with loquet:
            val = ser.read_until(b"\n")

        return val  # noqa: RET504

    @classmethod
    def loop(  # noqa: PLR0917, PLR0913
        cls: type[Self],
        ser: serial.Serial,
        val: bytes,
        arret: multiprocessing.Event,
        input_: multiprocessing.Queue,
        output: multiprocessing.Queue,
        loquet: multiprocessing.Lock,
        log_queue: multiprocessing.Queue,
    ) -> bytes:
        """Exécute une itération de suivi de la ligne série.

        Returns
        ------------
        val: bytes
            La valeur lue dans cette itération.
        """
        if not input_.empty() and not ser.out_waiting:
            cls.write_out(ser, input_, arret, loquet, log_queue)

        if len(val) > 0:
            val = cls.send_out(val, output, arret, log_queue)

        if not output.full() and ser.in_waiting:
            val = cls.read_in(ser, loquet)

        return val

    @classmethod
    def run(  # noqa: PLR0917, PLR0913
        cls: type[Self],
        port: str,
        baudrate: BaudRateType,
        timeout: float,
        arret: multiprocessing.Event,
        input_: multiprocessing.Queue,
        output: multiprocessing.Queue,
        loquet: multiprocessing.Lock,
        log_queue: multiprocessing.Queue,
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
            arret,
            loquet,
            log_queue,
        )

        with contextlib.suppress(KeyboardInterrupt):
            while not arret.is_set():
                val = cls.loop(
                    ser, val, arret, input_, output, loquet, log_queue
                )

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

    def next(self, *, block: bool = True, parse: bool = False) -> str | dict:
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

        Raises
        ---------
        ParsableArduinoSerialDataError
            Quand les données ne peuvent pas être analysées.
        """  # noqa: DOC502
        val = super().next(block=block)

        if not parse:
            return val

        if "\t" in val:
            items = val.split("\t")

            if all((":" in mot) for mot in items):
                d = {}

                for k, v in (mot.split(":") for mot in items):
                    if k.isprintable():
                        try:
                            res = float(v)
                        except ValueError:
                            d[k] = np.nan
                        else:
                            d[k] = res

                return d

        raise ParsableArduinoSerialDataError(val)

    def close(self) -> None:
        """Fermer la connexion série."""
        self.__open = False
        super().close()

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
        """Retourne une description d'un :class:LigneSerie.

        Returns
        ---------------
        str
            Sommaire de la connexion.
            ``LigneSerie<<id>> to <port> [on <thread>]
        """
        self.checkin()

        if self.is_open:
            return (
                f"LigneSerie<{hex(id(self))}> "
                f"to {self.__port} running on {self.__thread}"
            )

        return f"LigneSerie<{hex(id(self))}> to {self.__port}"


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

    @staticproperty
    def APPAREIL() -> str:  # noqa: N802
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
    from serial.tools.list_ports import comports  # noqa: PLC0415

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
        while True:
            try:
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
        while True:
            try:
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
            try:
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
        while True:
            try:
                print(com.next(block=True, parse=True))
            except KeyboardInterrupt:
                break

    info("Fin.")


__all__ = ["Appareil", "ArduinoNanoEvery", "LigneSerie"]
