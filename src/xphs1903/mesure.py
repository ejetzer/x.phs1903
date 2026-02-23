from logging import getLogger

from pandas import DataFrame
from serial import Serial

logging = getLogger(__name__)


def prendre_mesure[R: DataFrame](res: R, ser: Serial) -> R:
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
