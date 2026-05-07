# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Outils de communication par ligne série."""

import logging
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from serial import Serial  # ! La classe du module pyserial

from .definitions import ObjetImmuable
from .exceptions import ChoixInvalideError, PasUnNombreEntierError

logging.getLogger(__name__).addHandler(logging.NullHandler())
if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from serial.tools.list_ports_common import ListPortInfo

    from .definitions import GenericKArgsType


class LigneSérieImmuable(ObjetImmuable):
    """Ligne série immuable après l'initialisation."""

    def __init__(
        self,
        port: str | None,
        baudrate: int = 115_200,
        bytesize: int = 8,
        **kargs: GenericKArgsType,
    ) -> None:
        """Ligne série immuable après l'initialisation."""
        super().__init__(Serial)

        # Les attributs de la ligne série sont fixés
        # après l'initialisation pour forcer l'ouverture
        # de la communication à un moment ultérieur.
        kargs |= {'port': port, 'baudrate': baudrate, 'bytesize': bytesize}
        for k, v in kargs.items():
            setattr(self._object, k, v)


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


def sélection_appareil() -> LigneSérieImmuable:
    """Facilite la sélection d'un appareil.

    Affiche un invite pour la sélection d'un appareil
    auquel se connecter.

    Returns:
        La ligne de communication série avec l'appareil

    Raises:
        PasUnNombreEntierError: si la sélection n'est pas un nombre entier
        ChoixInvalideError: si la sélection est autrement invalide
    """
    from serial.tools.list_ports import comports  # noqa: PLC0415

    ports: list[ListPortInfo] = comports()

    for i, port in enumerate(ports):
        print(
            f'[{i + 1}]\t{port.name}\t{port.device}\t{port.description}',
            file=sys.stderr,
        )
    sel: str | int = input('Quel port? >>> ')

    if sel.isdigit():
        sel: int = int(sel) - 1
    else:
        raise PasUnNombreEntierError(sel)

    port: None | ListPortInfo = None
    if sel < len(ports):
        port = ports[sel]
        print(f'[{sel + 1}]\t{port.name}\t{port.device}\t{port.description}')
    else:
        raise ChoixInvalideError(sel, list(range(1, len(ports)+1)))

    return LigneSérieImmuable(port=port.device, baudrate=115_200, timeout=2)
