# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Outils de communication par ligne série."""

import logging
import sys
from collections import nomedtuple
from collections.abc import Callable
from dataclasses import dataclass
from queue import Queue, Shutdown
from threading import Thread
from typing import TYPE_CHECKING

from serial import Serial  # ! La classe du module pyserial
from serial.tools.list_ports import comports

from .definitions import ObjetImmuable
from .exceptions import ChoixInvalideError, PasUnNombreEntierError

logging.getLogger(__name__).addHandler(logging.NullHandler())
if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from serial.tools.list_ports_common import ListPortInfo

    from .definitions import GenericKArgsType


BAUDRATE: Final[int] = 9600
TIMEOUT: Final[float] = 2.0
BYTESIZE: Final[int] = 8


class LigneSérieImmuable(ObjetImmuable):
    """Ligne série immuable après l'initialisation."""

    def __init__(
        self,
        port: str | None,
        baudrate: int = BAUDRATE,
        bytesize: int = BYTESIZE,
        timeout: float = TIMEOUT,
        **kargs: GenericKArgsType,
    ) -> None:
        """Ligne série immuable après l'initialisation."""
        super().__init__(Serial)

        if port is None:
            port = self.comports(choice=True)

        # Les attributs de la ligne série sont fixés
        # après l'initialisation pour forcer l'ouverture
        # de la communication à un moment ultérieur.
        kargs |= {
            'port': port,
            'baudrate': baudrate,
            'bytesize': bytesize,
            'timeout': timeout,
        }
        for k, v in kargs.items():
            setattr(self._object, k, v)

    @classmethod
    def comports(
        cls,
        *,
        choice: bool = False,
        cond: Callable = bool,
        order: Callable = lambda x: x.device,
    ) -> list[str]:
        ports: list[str] = [
            x.device for x in sorted(filter(cond, comports()), key=order)
        ]

        if choice:
            for i, port in enumerate(ports):
                print(
                    f'[{i + 1}]\t{port.device}\n\t{port.description}',
                    file=sys.stderr,
                )
            sel: str = input('Quel port? Entrez un nombre. >>> ')

            if sel.isdigit():
                sel: int = int(sel) - 1
            else:
                raise PasUnNombreEntierError(sel)

            port: None | ListPortInfo = None
            if sel < len(ports):
                port = ports[sel]
                return port
            else:
                raise ChoixInvalideError(sel, list(range(1, len(ports) + 1)))
        else:
            return ports

    @property
    def in_waiting(self) -> bool:
        return self._object.in_waiting

    @property
    def out_waiting(self) -> bool:
        return self._object.out_waiting

    def write(self, msg: str | bytes, encoding: str = 'utf-8') -> int:
        n: int = 0

        if isinstance(msg, str):
            msg = bytes(msg, encoding=encoding)

        for c in msg:
            n += self._object.write(c)

        return n

    def read(self, *, n: int | None = None, d: bytes | None = None) -> bytes:
        if d is not None:
            msg: bytes = self._object.read_until(d, size=n)
        elif n is not None:
            msg: bytes = self._object.read(n)
        else:
            msg: bytes = b''
            while self._object.in_waiting:
                msg += self._object.read()

        return msg

    def open(self) -> None:
        self._object.open()

    def close(self) -> None:
        self._object.close()

    def __enter__(self) -> Self:
        self._object.open()
        return self

    def __exit__(self, *exc) -> bool:
        self._object.close()
        return exc[0] is None


@dataclass
class Commande:
    """Décrit une commande à envoyer sur la ligne série."""

    'Le nom court de la commande'
    name: str

    'Une description plus longue de la commande'
    description: str = ''

    'Les octets à transmettre'
    cmd: bytes | None = None

    'La taille attendue de la réponse'
    rep_size: int | None = None

    'Le caractère de fin de commande et de réponse'
    end: bytes | None = None

    'La fonction à utiliser pour convertir la réponse'
    conv: Callable[bytes, Any] = lambda x: x

    @property
    def size(self) -> int:
        """Calcule la longueur de la réponse.

        Returns:
            La longueur de la réponse en octets
        """
        return len(self.cmd)

    def __len__(self) -> int:
        """Calcule la longueur de la réponse.

        Returns:
            La longueur de la réponse en octets
        """  # noqa: D401
        return len(self.cmd)


class FileCommandes(Queue):
    def put(
        self,
        name: str,
        description: str = '',
        cmd: bytes | None = None,
        rep_size: int | None = None,
        end: bytes | None = None,
        conv: Callables[bytes, Any] = lambda x: x,
    ) -> None:
        super().put(Commande(name, description, cmd, rep_size, end, conv))


@dataclass
class Réponse:
    """Décrit une réponse reçue sur la ligne série."""

    'La commande de laquelle on attend la réponse'
    cmd: Commande

    'La réponse brute en octets'
    rep: bytes

    'Le résultat de la conversion de rep'
    res: Any

    @property
    def size(self) -> int:
        """Calcule la longueur de la réponse.

        Returns:
            La longueur de la réponse en octets.
        """
        return len(self.rep)

    def __len__(self) -> int:
        """Calcule la longueur de la réponse.

        Returns:
            La longueur de la réponse en octets
        """  # noqa: D401
        return len(self.rep)

    def __str__(self) -> str:
        return str(self.res)


class FileRéponses(Queue):
    def put(self, cmd: Commande, rep: bytes) -> None:
        super().put(Réponse(cmd, rep, cmd.conv(rep)))


class FilAppelReponse(Thread):
    def __init__(
        self,
        appareil: LigneSérieImmuable | ListPortInfo | str,
        commandes: FileCommandes | None = None,
        resultats: FileRéponses | None = None,
    ):
        if isinstance(appareil, LigneSérieImmuable):
            self.appareil = appareil
        elif isinstance(appareil, ListPortInfo):
            self.appareil = LigneSérieImmuable(
                port=appareil.device, baudrate=BAUDRATE, timeout=TIMEOUT
            )
        elif isinstance(appareil, str):
            self.appareil = LigneSérieImmuable(
                port=appareil, baudrate=BAUDRATE, timeout=TIMEOUT
            )
        else:
            raise AppareilInexistantOuInvalide(repr(appareil), type(appareil))

        super().__init__(target=self, daemon=False, name=self.appareil.port)

        if commandes is None:
            commandes = FileCommandes()
        self.commandes = commandes

        if resultats is None:
            resultats = FileRéponses()
        self.resultats = resultats

    def __call__(self) -> None:
        for c, r in self:
            continue

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> Réponse:
        com = self.send()
        rep = self.receive(com)
        return com, rep

    def receive(self) -> Réponse:
        ret: bytes | None = None
        com: Commande = self.commandes.get()
        if com.end is not None:
            ret = self.appareil.read_until(commande.end, commande.size)
        elif com.size is not None:
            ret = self.appareil.read(commande.size)
        else:
            ret = self.appareil.read_all()

        self.resultats.put(com, ret)
        self.commandes.task_done()
        return rep

    def send(self) -> Commande:
        try:
            com = self.commandes.get()
        except ShutDown:
            raise StopLigneDeCommande(self.commandes, self.resultats)

        if com.cmd is not None:
            self.appareil.write(com.cmd)

        return com

    def __enter__(self) -> Self:
        if not self.appareil.is_open:
            self.appareil.open()
        self.start()
        return self

    def __exit__(self, *exc) -> bool:
        self.join()

        if issubclass(exc[0], (RuntimeError, KeyboardInterrupt)):
            return False
        else:
            return True

    def join(self, timeout: float | None = None):
        self.commandes.shutdown()
        super().join(timeout=timeout)
        self.appareil.close()
        self.resultats.shutdown()

    def __str__(self):
        res = self.resultats.get()
        self.resultats.task_done()
        return str(res)

    def write(
        self, msg: bytes | str, encoding: str = 'utf-8', nom: str | None = None
    ):
        if isinstance(msg, str):
            msg = bytes(msg, encoding=encoding)

        if nom is None:
            nom = str(msg, encoding=encoding)

        self.commandes.put(nom, cmd=msg)

    def read(self):
        return str(self)

    def rep(self):
        self.write(input('>>>'))
        print(self)

    def repl(self):
        while True:
            self.rep()
