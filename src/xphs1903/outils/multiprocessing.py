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

if typing.TYPE_CHECKING:
    from types import TracebackType
    from typing import Final, Self


class Synchronisateur(WithLogger):
    """Objet de synchronisation.

    Combine loquet, files d'entrée et sortie, journal d'erreur et
    événement d'arrêt.
    """

    def __init__(
        self,
        *,
        stop_event: multiprocessing.Event | None = None,
        lock: multiprocessing.Lock | None = None,
    ) -> None:
        """Initialise les événements d'arrêt et le loquet.

        Parameters
        ------------------
        stop_event: multiprocessing.Event | None = None
            Événement d'arrêt commun à un autre objet ou processus.
        lock: multiprocessing.Lock | None = None
            Loquet de synchronisation commun à un autre objet ou processus.
        """
        self.__stop_event = (
            multiprocessing.Event() if stop_event is None else stop_event
        )
        self.__loquet = multiprocessing.Lock() if lock is None else lock

    def reset(self) -> None:
        """Initialise le contexte d'exécution parallèle."""
        self.__ctx = multiprocessing.get_context(method="spawn")
        self.__in_queue = self.__ctx.JoinableQueue()
        self.__out_queue = self.__ctx.JoinableQueue()
        self.__log_queue = self.__ctx.JoinableQueue()

    @property
    def context(self) -> multiprocessing.Context:
        """Contexte d'exécution parallèle s'il est défini."""
        return self.__ctx

    @property
    def outqueue(self) -> multiprocessing.Queue:
        """File de sortie."""
        return self.__out_queue

    @property
    def inqueue(self) -> multiprocessing.Queue:
        """File d'entrée."""
        return self.__in_queue

    @property
    def logqueue(self) -> multiprocessing.Queue:
        """File d'erreurs."""
        return self.__log_queue

    @property
    def lock(self) -> multiprocessing.Lock:
        """Loquet de synchronisation."""
        return self.__loquet

    @property
    def is_stopped(self) -> bool:
        """Si l'événement d'arrêt est déclenché."""
        return self.__stop_event.is_set()

    @property
    def is_locked(self) -> bool:
        """Si le loquet est barré."""
        return self.__loquet.locked()

    def stop(self) -> None:
        """Déclenche l'événement d'arrêt."""
        if not self.__stop_event.is_set():
            self.__stop_event.set()

    def close(self) -> None:
        """Ferme les files."""
        self.__in_queue.close()
        self.__out_queue.close()
        self.__log_queue.close()

    def start(self) -> None:
        """Réinitialise l'événement d'arrêt."""
        if self.__stop_event.is_set():
            self.__stop_event.clear()

    def log(self, exc: Exception) -> None:
        """Ajoute une erreur à la file d'erreurs."""
        self.__log_queue.put(exc)

    def printout(self) -> None:
        """Envoie les erreurs à l'erreur standard."""
        while not self.logqueue.empty():
            err = self.logqueue.get()
            self.warning("Erreur dans le processus parallèle:", exc_info=err)

    def __enter__(self) -> Self:
        """Verrouille le loquet."""
        self.__loquet.acquire()

    def __exit__(
        self,
        typ: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        """Libère le loquet et resoulève l'erreur.

        Parameters
        ---------------
        typ: type[BaseException] | None
        exc: BaseException | None
        tb: TracebackType | None

        Returns
        ---------------
        False
        """
        self.__loquet.release()

        if typ is not None:
            self.warning("", exc_info=exc)

        return False


class Processus(WithLogger):
    """Objet abstrait de processus parallèle."""

    def __init__(
        self,
        *,
        stop_event: multiprocessing.Event | None = None,
        lock: multiprocessing.Lock | None = None,
    ) -> None:
        """Initialise le processus."""
        self.checkin()
        self.__sync: Synchronisateur = Synchronisateur(
            stop_event=stop_event, lock=lock
        )
        self.reset()

    @property
    def sending(self) -> bool:
        """Vérifie s'il reste des données à envoyer."""
        self.checkin()
        return not self.__sync.inqueue.empty()

    @property
    def holding(self) -> bool:
        """Vérifie s'il reste des données à lire."""
        self.checkin()
        return not self.__sync.outqueue.empty()

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
        sync: Synchronisateur,
        log_queue: multiprocessing.Queue,  # noqa: ARG003
    ) -> None:
        """Fonction à exécuter très simple, à surclasser."""
        cls.setup()

        while not sync.is_stopped():
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
        self.__sync.reset()

        self.__thread: multiprocessing.Process = self.__sync.context.Process(
            group=None,
            target=self.run,
            args=args + (self.__sync,),
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

        if not isinstance(data, str):
            raise WrongSerialInputTypeError(data)

        try:
            self.__sync.inqueue.put((data + end).encode("utf-8"), block=block)
        except queue.Full as err:
            self.warning(
                "input.full()=%s", self.__sync.inqueue.full(), exc_info=err
            )

    @property
    def serial_log(self) -> multiprocessing.Queue:
        """Les messages d'erreur du processus parallèle.

        Returns
        -------------
        multiprocessing.Queue
            La file contenant les messages d'erreur.
        """
        return self.__sync.logqueue

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

        self.__sync.printout()

        if typ is not None:
            self.warning("", exc_info=exc)

        self.close()

        return False  # Re-raise the exception please

    def close(self) -> None:
        """Ferme le processus."""
        self.checkin()

        if self.is_alive:
            self.__sync.stop()
            self.__sync.close()

            self.__thread.join(timeout=1)  # Pas un délai de communication
            self.debug("%s", self.__thread)

            if self.__thread.is_alive():
                self.__thread.terminate()

        self.reset()

    def reset(self) -> None:
        """Réinitialise le processus."""
        self.checkin()

        if self.__sync.is_stopped:
            self.__sync.start()

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

    def __semidecode(self, val: bytes) -> str:
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
                d = bytes([c]).decode("utf-8")
            except UnicodeDecodeError as err2:
                self.warning("inserting '▮'...", exc_info=err2)
                d = "▮"
            finally:
                res += d

        return res

    def next(
        self,
        *,
        block: bool = True,
        timeout: float | None = TIMEOUT,
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
            val: bytes = self.__sync.outqueue.get(block=block, timeout=timeout)
        except queue.Empty as err:
            self.debug("", exc_info=err)
            return None
        except ValueError as err:
            self.debug("", exc_info=err)
            return None
        else:
            self.debug("val=%r", val)
            self.__sync.outqueue.task_done()

        try:
            val: str = val.decode("utf-8")
        except UnicodeDecodeError as err:
            self.warning("", exc_info=err)
            val = self.__semidecode(val)
        finally:
            val = val.strip()

        self.debug("val = %r", val)
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

    def iter(
        self, *, block: bool = True, timeout: int | None = TIMEOUT
    ) -> str:
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
