import sys
import threading

from logging import getLogger

from pandas import DataFrame
from serial import Serial

logging = getLogger(__name__)


class FilLectureOctets(threading.Thread):

    def __init__(self, res: DataFrame, ser: Serial):
        self.res = res
        self.ser = ser
        super().__init__(
            name=f'lectureoctets-{ser.device}',
            daemon=True
        )
        self.start()

    def run(self):
        while True:
            lire_octets(self.res, self.ser)
  
def lire_octets[R: DataFrame](res: R, ser: Serial) -> (R, Serial):
    bloc: bytearray = bytearray(len(res.columns) * 255)
    ser.readinto(bloc)
    
    for i, b in enumerate(bloc):
        r, c = divmod(i, len(res.columns))
        res.loc[r, c] = int.from_bytes(b, byteorder=sys.byteorder)
    
    return res, ser 

class FilPriseMesure(threading.Thread):

    def __init__(self, res: DataFrame, ser: Serial):
        self.res = res
        self.ser = ser
        super().__init__(
            name=f'prisemesure-{ser.device}',
            daemon=True
        )
        self.start()

    def run(self):
        while True:
            prendre_mesure(self.res, self.ser) 

def prendre_mesure[R: DataFrame](res: R, ser: Serial) -> (R, Serial):
    """Prise d'une mesure

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
    for l in lignes:
        logging.debug('l=%r', l)
        if b'\t' not in l:
            logging.error('Cette ligne est incorrecte:\t%s', l)
        else:
            n: int = res.t.size
            i: int
            w: float
            for i, w in enumerate(map(float, l.split())):
                res.loc[n, res.columns[i]] = w

    return res
