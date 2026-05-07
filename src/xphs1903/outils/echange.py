# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Prise de mesures dans plusieurs fils d'exécution."""

from collections import namedtuple
from collections.abc import Callable
from dataclasses import dataclass
from logging import getLogger
from queue import Queue, ShutDown
from threading import Thread
from typing import Any

from serial import LigneSérieImmuable

logging = getLogger(__name__)


class Échange(Thread):

    def __init__(self, appareil: LigneSérieImmuable, commandes: Queue = None, resultats: Queue = None):
        logging.debug(
            '%s.__init__ pour %r avec appareil=%r\n\tcommandes=%r\n\tresultats=%r',
            type(self).__name__,
            self,
            appareil,
            commandes,
            resultats
        )
        super().__init__(target=self)
        self.appareil = appareil

        if commandes is None:
            commandes = Queue()
        self.commandes = commandes

        if resultats is None:
            resultats = Queue()
        self.resultats = resultats

    def envoyer(self, cmd: str):
        logging.debug('%s.envoyer pour %r avec cmd=%r', type(self).__name__, self, cmd)
        bcmd = bytes(cmd, 'utf-8')
        cmd = Commande(
            name=cmd,
            cmd=bcmd,
            rep_size=len(bcmd)
        )
        self.commandes.put(cmd)

    def recevoir(self) -> str:
        logging.debug('%s.recevoir pour %r', type(self).__name__, self)
        ret = str(self.resultats.get().rep, 'utf-8')
        self.resultats.task_done()
        return ret

    def __enter__(self):
        logging.debug('%s.__enter__ pour %r', type(self).__name__, self)
        if not self.appareil.is_open:
            self.appareil.open()  # Ouvrir la connexion avec l'appareil
        self.start()  # Démarrer l'exécution en parallèle
        return self  # Retourner l'objet-même, pour continuer l'exécution dans le bloc with

    def __exit__(self, *exc):
        logging.debug('%s.__exit__ pour %r avec exc=%r', type(self).__name__, self, exc)
        self.join()

        if exc[0] is RuntimeError:
            logging.exception('erreur dans l\'execution')
            return False
        elif exc[0] is KeyboardInterrupt:
            logging.critical('fermeture initiée par l\'utilisateur')
            return False

        return True

    def join(self):
        logging.debug('%s.join pour %r', type(self).__name__, self)
        self.commandes.shutdown()
        while not self.commandes.empty():
            self._recevoir(self._envoyer())
        self.appareil.close()
        self.resultats.shutdown()
        super().join()

    def __call__(self):
        logging.debug('%s.__call__ pour %r', type(self).__name__, self)
        for s in self:
            continue

    def __iter__(self):
        logging.debug('%s.__iter__ pour %r', type(self).__name__, self)
        return self

    def _envoyer(self):
        try:
            commande = self.commandes.get()  # Attendre une instruction
        except ShutDown:
            raise StopIteration

        if commande.cmd is not None:
            self.appareil.write(commande.cmd)
        self.commandes.task_done()

        return commande

    def _recevoir(self, commande):
        ret: bytes | None = None
        if commande.end is not None:
            ret = self.appareil.read_until(commande.end, commande.size)
        elif commande.size is not None:
            ret = self.appareil.read(commande.size)
        else:
            ret = self.appareil.read_all()
        res = commande.conv(ret)

        rep = Réponse(commande, ret, res)

        self.resultats.put(rep)
        return rep

    def __next__(self):
        logging.debug('%s.__next__ pour %r', type(self).__name__, self)
        commande = self._envoyer()
        ret = self._recevoir(commande)
        return ret

    def loop(self, incmd: Callable = lambda: input('$ '), outcmd: Callable[str] = print):
        while True:
            self.envoyer(incmd())
            outcmd(self.recevoir())


class Auditeur(Échange):

    def __init__(self, appareil: LigneSérieImmuable, resultats: Queue = None):
        super().__init__(appareil, None, resultats)

    def envoyer(self):
        self.commandes.put(Commande('', b'', 0))

    def loop(self, outcmd: Callable[str] = print):
        super().loop(incmd=lambda: '', outcmd=outcmd)


class Émmetteur(Échange):

    def __init__(self, appareil: LigneSérieImmuable, commandes: Queue = None):
        super().__init__(appareil, commandes, None)

    def _recevoir(self, commande):
        rep = Réponse(commande, bytes([0]), None)
        self.resultats.put(rep)
        return rep
