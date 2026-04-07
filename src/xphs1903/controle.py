# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
# https://stackoverflow.com/a/57387909
# https://stackoverflow.com/a/63967448
"""Fonctions de contrôle ordiné."""

import sys
import threading
import time
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from pandas import DataFrame
    from serial import Serial

logging = getLogger(__name__)


class EntreeClavier(threading.Thread):
    def __init__(self, action: Callable, invite: str = '>'):
        self.action = action
        self.invite = invite
        super().__init__(name=f'entreeclavier-{__name__}', daemon=True)
        self.start()

    def run(self):
        while True:
            self.action(input(self.invite))


class CommandeRetour(EntreeClavier):
    def __init__(self, ser: Serial, invite: str = '>'):
        self.ser = ser
        super().__init__(action=self.action, invite=self.invite)

    def action(self, entree: str) -> None:
        commande = bytes(map(int, entree))
        self.ser.write(commande)
        self.ser.read(1)
