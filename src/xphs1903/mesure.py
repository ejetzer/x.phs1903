# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Prise de mesures dans plusieurs fils d'exécution."""

import sys
import threading
from logging import getLogger
from typing import TYPE_CHECKING

from pandas import DataFrame

if TYPE_CHECKING:
    from serial import Serial

logging = getLogger(__name__)


class FilLectureOctets(threading.Thread):
    """Fil de lecture d'octets."""

    def __init__(self, res: DataFrame, ser: Serial) -> None:
        """Fil de lecture de données."""
        self.res = res
        self.ser = ser
        super().__init__(name=f'lectureoctets-{ser.device}', daemon=True)
        self.start()

    def run(self) -> None:
        """Lecture en continu."""
        while True:
            lire_octets(self.res, self.ser)


def lire_octets[R: DataFrame](res: R, ser: Serial) -> (R, Serial):
    """Lecture d'un octet."""
    bloc: bytearray = bytearray(len(res.columns) * 255)
    ser.readinto(bloc)

    for i, b in enumerate(bloc):
        r, c = divmod(i, len(res.columns))
        res.loc[r, c] = int.from_bytes(b, byteorder=sys.byteorder)

    return res, ser


class FilPriseMesure(threading.Thread):
    """Fil d'envoi de commande et lecture de réponse."""

    def __init__(self, res: DataFrame, ser: Serial) -> None:
        """Fil d'envoi de commande et lecture de réponse."""
        self.res = res
        self.ser = ser
        super().__init__(name=f'prisemesure-{ser.device}', daemon=True)
        self.start()

    def run(self) -> None:
        """Prise de mesures en continu."""
        while True:
            prendre_mesure(self.res, self.ser)


def prendre_mesure[R: DataFrame](res: R, ser: Serial) -> (R, Serial):
    """Prise d'une mesure.

    prendre_mesure, pour chaque liste de mesures contenues dans ``res``,
    envoie une requête à l'Arduino puis lit la valeur reçue.

    Parameters
    ----------
    res
        Liste des mesures prises. Structurée en ``[t, pd1, pd2, ...]``
    ser
        Objet de communication série avec lequel communiquer pour obtenir
        les données.

    Returns
    ----------
    res
        Avec les nouvelles valeurs.
    """
    # Mesure du temps auquel la mesure est prise
    lignes: list[bytes] = ser.readlines()
    logging.debug('lignes=%s', lignes)
    for ligne in lignes:
        logging.debug('ligne = %r', ligne)
        if b'\t' not in ligne:
            logging.error('Cette ligne est incorrecte:\t%s', ligne)
        else:
            n: int = res.t.size
            i: int
            w: float
            for i, w in enumerate(map(float, ligne.split())):
                res.loc[n, res.columns[i]] = w

    return res
