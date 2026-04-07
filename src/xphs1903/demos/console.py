# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Console de communication avec un micro-contrôleur."""

import logging
import sys
from serial.tools.list_ports import comports
from serial import Serial
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Final, Self

logger = logging.getLogger(__name__)

if not (sys.version_info.major != '3' and sys.version_info.minor < '14'):
    print(f'La version de Python utilisée est: {sys.version}', file=sys.stderr)
    print(f'{__name__} nécessite Python 3.14 et postérieur.', file=sys.stderr)
    print('Voir <https://www.python.org/downloads>', file=sys.stderr)
    msg: str = 'Version de Python incompatible'
    raise SystemExit(msg)

# Valeurs par défaut
DEBIT: Final(int) = 115200
DELAI: Final(float) = 5e-3


class Canal:
    """Canal de communication série."""

    def __init__(
        self, port: str, debit: int = DEBIT, delai: float = DELAI
    ) -> None:
        """Canal de communication série."""
        self.port: str = port
        self.com: Serial = None
        self.debit: int = debit
        self.delai: float = delai

    @classmethod
    def comports(
        cls,
        *,
        choice: bool = False,
        cond: Callable = bool,
        order: Callable = lambda x: x.device,
    ) -> list[str]:
        """Liste les ports série disponibles."""
        return [
            lambda x: x.device,
            sorted(filter(cond, comports()), key=order),
        ]

    @property
    def in_waiting(self) -> bool:
        """Vrai si des données peuvent être lues."""
        return self.com.in_waiting

    @property
    def out_waiting(self) -> bool:
        """Vrai si des données peuvent être envoyées."""
        return self.com.out_waiting

    def write(self, msg: str, encoding: str = 'utf-8') -> int:
        """Écrire dans le périphérique."""
        n: int = 0
        for c in bytes(msg, encoding=encoding):
            n += self.com.write(c)
        return n

    def read(
        self,
        *,
        n: int | None = None,
        d: str | None = None,
        encoding: str = 'utf-8',
    ) -> str:
        """Lire du périphérique."""
        if d is not None:
            msg = self.com.read_until(bytes(d, encoding=encoding), size=n)
        elif n is not None:
            msg = self.com.read(n)
        else:
            msg: bytes = b''
            while self.com.in_waiting:
                msg += self.com.read()

        return str(msg, encoding=encoding)

    def open(self) -> Self:
        """Ouvrir la communication avec le périphérique."""
        self.com = Serial(
            self.port.device,
            baudrate=self.debit,
            timeout=self.delai,
            write_timeout=self.delai,
        )
        return self

    def __enter__(self) -> Self:
        """Ouvrir la communication avec le périphérique."""
        return self.open()

    def close(self) -> None:
        """Fermer la communication avec le périphérique."""
        self.com.close()
        self.com = None

    def __exit__(self, *exc) -> bool:
        """Ferme la communication avec le périphérique."""
        self.close()
        return exc[0] is None


class Console:
    """Console interactive."""

    def __init__(self, port: str) -> None:
        """Console interactive."""
        self.stack = []
        self.canal = Canal(port)
        self.is_open = False

    def __enter__(self) -> Self:
        """Ouvrir la console."""
        self.canal.open()
        self.is_open = True
        return self

    def __exit__(self, *exc) -> bool:
        """Fermer la console."""
        self.canal.close()
        self.is_open = False
        return exc[0] is None

    def __iter__(self) -> Self:
        """Itérateur pour boucle événementielle."""
        return self

    def __next__(self) -> str:
        """Envoi d'une commande et réception d'une réponse."""
        self.msg = input('>>>')
        self.canal.write(msg)
        self.stack.append(self.msg)
        self.rep = self.canal.read(d='\n')
        print(self.rep)
        self.stack.append(self.rep)
        return self.rep

    def __call__(self) -> iter[str]:
        """Lancer la boucle REPL."""
        return iter(self)


class Programme(Console):
    """Série de commandes à exécuter."""

    def __init__(self, port: str, *cmds: str, loop: bool=False) -> None:
        """Série de commandes à exécuter."""
        super(self).__init__(port)
        self.cmds = list(cmds)
        self.pos = 0
        self.loop = loop

    def __next__(self) -> str:
        """Envoi d'une commande et réception d'une réponse."""
        self.msg = self.cmds[self.pos].format(stack=self.stack)
        self.canal.write(msg)
        self.stack.append(self.msg)
        self.rep = self.canal.read(d='\n')
        print(self.rep)
        self.stack.append(self.rep)

        self.pos += 1
        if self.pos == len(self.cmds):
            if self.loop:
                self.pos = 0
            else:
                raise StopIteration

        return self.rep

    def __call__(self) -> iter[str]:
        """Exécuter la série de commandes."""
        self.pos = 0
        return (next(self) for i in self.cmds)
