# (c) Copyright 2026 Émile Jetzer. All Rights Reserved.
"""Outils de communication par ligne série."""

import logging
import sys
import typing
from collections.abc import Callable
from dataclasses import dataclass
from queue import Queue, ShutDown
from threading import Thread
from typing import TYPE_CHECKING

from serial import Serial  # ! La classe du module pyserial
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo

from .data import Datum
from .definitions import ObjetImmuable
from .exceptions import (
    AppareilInexistantOuInvalideError,
    ChoixInvalideError,
    PasUnNombreEntierError,
    StopLigneDeCommande,
    ValuePHS1903Error,
)

logging.getLogger(__name__).addHandler(logging.NullHandler())
if TYPE_CHECKING:
    from collections.abc import Callable
    from types import TracebackType
    from typing import Any, Final, Self

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
        cond: Callable[ListPortInfo, bool] = bool,
        order: Callable[ListPortInfo, int] = lambda x: int.from_bytes(
            bytes(x.device, encoding='utf-8')
        ),
    ) -> list[str] | str:
        """Liste les ports série disponibles.

        Liste les ports série disponibles, ou, dans un environnement
        interactif, avec la condition ``:var:choice == :bool:True``,
         demande une entrée à l'utilisateur.

         Arguments
             choice: False pour obtenir la liste complète des ports disponibles
             cond: condition que les ports doivent satisfaire

         Returns
             ports: liste des ports série disponibles
             ports[sel]: port sélectionné par l'utilisateur

        Raises
             PasUnNombreEntierError: si la sélection n'est pas un entier
             ChoixInvalideError: si la sélection de l'utilisateur est invalide3
        """  # noqa: D401
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

            if sel >= len(ports):
                raise ChoixInvalideError(sel, list(range(1, len(ports) + 1)))

            return ports[sel]

        return ports

    @property
    def in_waiting(self) -> bool:
        """Indique si il y a des octets à lire."""
        return self._object.in_waiting

    @property
    def out_waiting(self) -> bool:
        """Indique s'il y a des octets à envoyer."""
        return self._object.out_waiting

    def write(self, msg: str | bytes, encoding: str = 'utf-8') -> int:
        """Envoie une série d'octets sur la ligne série.

        Arguments
            msg: message à envoyer. Si isinstance(msg, str), il sera converti
                selon la valeur d'encoding
            encoding: encodage à utiliser pour les conversions de str à bytes

        Returns
            n: nombre d'octets écrits
        """
        n: int = 0

        if isinstance(msg, str):
            msg = bytes(msg, encoding=encoding)

        for c in msg:
            n += self._object.write(c)

        return n

    def read(self, *, n: int | None = None, d: bytes | None = None) -> bytes:
        """Lis une série d'octets de la ligne série.

        Arguments
            n: nombre d'octets à lire
            d: délimiteur de fin de lecture

        Returns
            msg: message lu en octets
        """
        'Message lu en octets'
        msg: bytes

        if d is not None:
            msg = self._object.read_until(d, size=n)
        elif n is not None:
            msg = self._object.read(n)
        else:
            msg = b''
            while self._object.in_waiting:
                msg += self._object.read()

        return msg

    def open(self) -> None:
        """Ouvre la connexion série."""
        self._object.open()

    def close(self) -> None:
        """Ferme la connexion série."""
        self._object.close()

    def __enter__(self) -> Self:
        """Ouvre la connexion et retourne self comme gestionnaire de contexte.

        Returns
            self
        """
        self._object.open()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """Ferme la connexion et retransmet les erreurs s'étant produites.

        Returns
            :bool:True si aucune exception n'a été soulevée.
        """
        self._object.close()
        return exc_type is None


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

    def __repr__(self) -> str:
        """Retourne une représentation de l'objet.

        Returns
            Une représentation de l'objet
        """
        return f'<{type(self)} {self.cmd} ({self.name})>'

    def __str__(self) -> str:
        """Retourne la commande sous forme de chaîne.

        Returns
            :var:cmd sous forme de chaîne
        """
        return str(self.cmd, encoding='utf-8')

    def __bytes__(self) -> bytes:
        """Retourne la commande sous forme d'octets.

        Returns
            :var:cmd
        """
        return self.cmd

    def __iter__(self) -> iter:
        """Retourne les différents paramètres en ordre."""
        return iter((
            self.name,
            self.description,
            self.cmd,
            self.rep_size,
            self.end,
            self.conv,
        ))


'Commande à utiliser pour les instructions nulles/vides.'
CommandeNulle: Final[Commande] = Commande(
    'nulle',
    cmd=None,
    conv=lambda x: None,  # noqa: ARG005
)
# La fonction conv doit avoir une signature spécifique, ce
# qui cause l'erreur ARG005 dans le vérificateur syntaxique.
#
# > error[ARG005]: Unused lambda argument: `x`
# >    --> {__file__}:{l}:{c}

'Commande pour terminer une communication ou un message.'
CommandeFinale: Final[Commande] = Commande('fin', cmd=bytes([0]), rep_size=0)


@dataclass
class Commandeln(Commande):
    """Commande attendant une ligne comme réponse."""

    'Séparateur de ligne standard "\\n"'
    end: Final[bytes] = b'\n'


@dataclass
class DemandeOctet(Commande):
    """Commande convertissant les octets en entier sans autre traitement."""

    "Convertisseur d'octets en entiers."
    conv: Callable[bytes, int] = int.from_bytes


def grapheurserie_à_pandasserie(data: bytes) -> Datum:
    """Converti les envois de données Arduino en données Pandas.

    Le traceur série Arduino accepte la syntaxe spéciale

    .. code::

        x:1234 y:235 z:13513

    pour afficher plusieurs courbes. Cette fonction permet au programme
    Python d'accepter la même syntaxe.

    Returns
        Datum(valeurs, noms): une série Pandas avec les valeurs reçues
    """
    "Paires 'nom:valeur'"
    paires: list[tuple[str, int]] = []

    'Nom de la série de données'
    nom_serie: bytes | None = None

    'Nom de chaque paire'
    nom: bytes = b''

    'Valeur de chaque paire'
    val: bytes = b''

    "Étape courante de l'analyse lexicale"
    état: int = 0

    for car in data:
        if état == 0:
            if car == b':':
                état += 1
            elif car == ' ':
                nom_serie = nom
                nom = b''
            else:
                nom += car
        elif état == 1:
            if car == b' ':
                paires.append((str(nom, encoding='utf-8'), int(val)))
                nom, val, état = b'', b'', 0
            else:
                val += car

    "Séparation des paires en une liste d'index et une de valeurs."
    index, valeurs = zip(*paires, strict=True)

    return Datum(valeurs, index=index, name=nom_serie)


@dataclass
class DemandeDonnées(Commande):
    """Commande compatible avec le traceur série Arduino."""

    "Séparateur de messsages, caractère standartd de fin de ligne '\\n'"
    end: Final[bytes] = b'\n'

    'Fonction de conversion en données Pandas'
    conv: Callable[bytes, Datum] = grapheurserie_à_pandasserie


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
        """Retourne le résultat converti en chaîne.

        Returns
            str(res): le résultat converti, converti en chaîne
        """
        return str(self.res)

    def __bytes__(self) -> bytes:
        """Retourne la réponse brute en octets.

        Returns
            rep: la réponse brute en octets
        """
        return self.rep

    def __iter__(self) -> iter:
        """Retourne les différents paramètres en ordre."""
        return iter((
            self.cmd,
            self.rep,
            self.res,
        ))


"Réponse nulle pour les programmes n'attendant aucune réponse"
RéponseNulle: Final[Réponse] = Réponse(CommandeNulle, b'', None)


class FileCommandes(Queue):
    """File (queue) contenant des commandes à envoyer."""

    def __init__(self, item_type: type[Commande] = Commande) -> None:
        """File (queue) contenant des commandes à envoyer.

        Raises
            ValuePHS1903Error: si item_type n'est pas un héritier de Commande
        """
        if not issubclass(item_type, Commande):
            raise ValuePHS1903Error

        'Classe à utiliser pour créer les nouveaux éléments de la file'
        self.usine: type[Commande] = item_type

        super().__init__()

    @typing.override
    def put(
        self,
        name: str,
        description: str = '',
        cmd: bytes | None = None,
        rep_size: int | None = None,
        end: bytes | None = None,
        conv: Callable[bytes, Any] = lambda x: x,
    ) -> Commande:
        """Ajoute un nouvel élément à la file.

        Returns
            nouv: nouvelle commande ajoutée à la file
        """
        nouv: Commande = self.usine(
            name, description, cmd, rep_size, end, conv
        )
        super().put(nouv)
        return nouv


class FileCommandesln(FileCommandes):
    """File contenant des Commandeln à envoyer."""

    def __init__(self) -> None:
        """File contenant des Commandeln à envoyer."""
        super().__init__(Commandeln)

    @typing.override
    def put(
        self,
        name: str,
        description: str = '',
        cmd: bytes | None = None,
        rep_size: int | None = None,
        end: bytes | None = b'\n',
        conv: Callable[bytes, Any] = lambda x: x,
    ) -> Commandeln:
        """Ajoute une nouvelle Commandeln à la file.

        Returns
            Commandeln: la nouvelle commande
        """
        return super().put(name, description, cmd, rep_size, end, conv)


class FileDemandesOctets(FileCommandes):
    """File contenant des commandes à envoyer."""

    def __init__(self) -> None:
        """File contenant des commandes à envoyer."""
        super().__init__(DemandeOctet)

    @typing.override
    def put(
        self,
        name: str,
        description: str = '',
        cmd: bytes | None = None,
        rep_size: int | None = None,
        end: bytes | None = None,
        conv: Callable[bytes, Any] = int.from_bytes,
    ) -> DemandeOctet:
        """Ajoute une nouvelle DemandeOctet à la liste.

        Returns
            DemandeOctet: la nouvelle demande
        """
        return super().put(name, description, cmd, rep_size, end, conv)


class FileDemandesDonnées(FileCommandes):
    """File contenant des DemandeDonnées."""

    def __init__(self) -> None:
        """Initialise une file contenant des instances DemandeDonnées."""
        super().__init__(DemandeDonnées)

    @typing.override
    def put(
        self,
        name: str,
        description: str = '',
        cmd: bytes | None = None,
        rep_size: int | None = None,
        end: bytes | None = b'\n',
        conv: Callable[bytes, Any] = grapheurserie_à_pandasserie,
    ) -> DemandeDonnées:
        """Ajoute une nouvelle DemandeDonnées à la file.

        Returns
            DemandeDonnées: la nouvelle commande
        """
        return super().put(name, description, cmd, rep_size, end, conv)


class FileRéponses(Queue):
    """File de Réponses."""

    def __init__(self, item_type: type[Réponse] = Réponse) -> None:
        """Initialise une file contenant des instances de Réponse.

        Raises
            ValuePHS1903Error: si item_type n'hérite pas de Réponse
        """
        if not issubclass(item_type, Réponse):
            raise ValuePHS1903Error

        'Classe à utiliser pour créer les nouveaux éléments de la file'
        self.usine: type[Réponse] = item_type

        super().__init__()

    @typing.override
    def put(self, cmd: Commande, rep: bytes) -> Réponse:
        """Ajoute une nouvelle Réponse à la file.

        Returns
            nouv: nouvelle réponse ajoutée à la file
        """
        nouv: Réponse = self.usine(cmd, rep, cmd.conv(rep))
        super().put(nouv)
        return nouv


class FilAppelReponse(Thread):
    """Fil d'exécution pour la communication série."""

    def __init__(
        self,
        appareil: LigneSérieImmuable | ListPortInfo | str,
        commandes: FileCommandes | None = None,
        resultats: FileRéponses | None = None,
    ) -> None:
        """Initialise un fil d'exécution pour la ligne série.

        Raises
            AppareilInexistantOuInvalideError: si l'appareil n'est pas joignable
        """
        'Appareil avec lequel la communication se fera'
        self.appareil: LigneSérieImmuable

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
            raise AppareilInexistantOuInvalideError(
                repr(appareil), type(appareil)
            )

        super().__init__(
            target=self, daemon=False, name=f'{__name__}.{self.appareil.port}'
        )

        if commandes is None:
            commandes = FileCommandes()

        "File de commandes à envoyer à l'appareil"
        self.commandes: FileCommandes = commandes

        if resultats is None:
            resultats = FileRéponses()

        "File de réponses reçues de l'appareil"
        self.resultats: FileRéponses = resultats

    def __call__(self) -> None:
        """Exécute la boucle de communication."""
        _c: Commande
        _r: Réponse
        for _c, _r in self:
            logging.getLogger(__name__).debug('>>> %s\n%s\n', _c, _r)
            continue

    def __iter__(self) -> Self:
        """Retourne l'itérateur self.

        Returns
            self
        """
        return self

    def __next__(self) -> Réponse:
        """Retourne la commande et réponse suivantes.

        La fonction peut bloquer

            - en attendant qu'une commande soit disponible
            - et en attendant qu'une réponse soit reçue.

        Returns
            com: commande envoyée à l'appareil
            rep: réponse reçue de l'appareil
        """
        com: Commande = self.send()
        rep: Réponse = self.receive(com)
        return com, rep

    def receive(self, com: Commande) -> Réponse:
        """Reçoit une réponse de l'appareil.

        Returns
            res: la réponse reçue
        """
        'La réponse brute reçue'
        ret: bytes

        if com.end is not None:
            ret = self.appareil.read_until(com.end, com.size)
        elif com.size is not None:
            ret = self.appareil.read(com.size)
        else:
            ret = self.appareil.read_all()

        res = self.resultats.put(com, ret)
        self.commandes.task_done()
        return res

    def send(self) -> Commande:
        """Envoie une commande à l'appareil.

        Raises
            StopLigneDeCommande: si la file est fermée et vide

        Returns
            com: commande envoyée
        """
        try:
            com: Commande = self.commandes.get()
        except ShutDown as err:
            raise StopLigneDeCommande(self.commandes, self.resultats) from err

        if com.cmd is not None:
            self.appareil.write(com.cmd)

        return com

    def __enter__(self) -> Self:
        """Ouvre la connexion et démarre le fil d'exécution.

        Returns
            self
        """
        if not self.appareil.is_open:
            self.appareil.open()

        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """Ferme le fil et la connexion.

        Returns
            False si il y a eu une erreur
        """
        self.join()

        return exc_type is None

    def join(self, timeout: float | None = TIMEOUT) -> None:
        """Vide les files et ferme le fil."""
        self.commandes.put(*CommandeFinale)
        self.commandes.shutdown()
        # On assume que pour chaque commande, il
        # est pertinent d'attendre TIMEOUT pour l'envoi
        # puis pour la réponse de chaque commande.
        super().join(timeout=timeout * 2 * self.commandes.size())
        self.appareil.close()
        self.resultats.shutdown()

    def __str__(self) -> str:
        """Affiche le dernier résultat reçu.

        Returns
            str(res): dernier résultat reçu
        """
        res = self.resultats.get()
        self.resultats.task_done()
        return str(res)

    def write(
        self, msg: bytes | str, encoding: str = 'utf-8', nom: str | None = None
    ) -> None:
        """Ajoute une Commande à la file."""
        if isinstance(msg, str):
            msg: bytes = bytes(msg, encoding=encoding)

        if nom is None:
            nom: str = str(msg, encoding=encoding)

        self.commandes.put(nom, cmd=msg)

    def read(self) -> str:
        """Retourne le dernier résultat reçu.

        Returns
            str(self): le dernier résultat reçu
        """
        return str(self)

    def rep(self) -> None:
        """Read, Evaluate, Print."""
        self.write(input('>>>'))
        print(self)

    def repl(self) -> None:
        """Read, Evaluate, Print, Loop."""
        while True:
            self.rep()


class FileCommandesNulles(FileCommandes):
    def put(self, *args, **kargs) -> None:
        super().put(*CommandeNulle)


class FileRéponsesNulles(FileRéponses):
    def put(self, *args, **kargs) -> None:
        super().put(*RéponseNulle)


class FilEcoute(FilAppelReponse):
    def __init__(
        self,
        appareil: LigneSérieImmuable | ListPortInfo | str,
        resultats: FileRéponses | None = None,
    ):

        commandes: FileCommandes = FileCommandesNulles()
        super().__init__(appareil, commandes, resultats)


class FilAnnonce(FilAppelReponse):
    def __init__(
        self,
        appareil: LigneSérieImmuable | ListPortInfo | str,
        commandes: FileCommandes | None = None,
    ):
        resultats: FileRéponses = FileRéponsesNulles()
        super().__init__(appareil, commandes, resultats)


class Arduino(FilAppelReponse):
    __devname__: str = 'Arduino'

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


class ArduinoNano(Arduino):
    __devname__: str = 'Arduino Nano'


class ArduinoNanoEvery(ArduinoNano):
    __devname__: Final[str] = 'Arduino Nano Every'
