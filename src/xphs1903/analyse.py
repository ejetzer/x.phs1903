from logging import getLogger

from numpy import array, mean, zeros
from numpy.fft import rfft, rfftfreq
from pandas import DataFrame, Series
from scipy.signal import get_window

logging = getLogger(__name__)

# ==================================
# = Fonctions d'analyse de données =
# ==================================


def fft(
    res: DataFrame, N_max: int = 1700, nom_cadre: str = 'hann'
) -> tuple[array, ...]:
    """Retourne la transformée de Fourier des données contenues dans :py:data:`res`.

    C'est une bonne idée de personnaliser cette fonction selon
    vos besoins. Pour bien comprendre ce que fait la fonction, vous devriez
    consulter :py:func:`scipy.signal.get_window`, :py:func:`numpy.fft.rfft` et
    :py:func:`numpy.fft.rfftfreq`. Pour les mathématiques derrière, consultez
    dans un premier lieu votre chargé de groupe.

    Parameters
    ------------
    nom_cadre
    res
        Liste des mesures, au format ``[t, pd1, pd2, ...]``
    N_max
        Nombre de mesures à utiliser

    Returns
    -------------
    fs
        Fréquences associées à la transformée
    ys
        Transformées.
    """
    N: int = min(res.index.size, N_max)  # Nombre de valeurs à considérer

    # Estimation de l'espacement, basé sur les mesures
    ts: Series = res.t.to_numpy()
    # noinspection PyTypeChecker
    d: float = mean(ts[1:] - ts[:-1])

    ys = []
    cadre = get_window(nom_cadre, N)
    signal = zeros(N)
    for sigcol in res.columns[1:]:
        sig = res[sigcol].to_numpy()
        if len(sig) < N:
            logging.error('Données mal acquises...:\n\tsig = %r', sig)
        else:
            signal = sig[-N:] * cadre
            ys.append(abs(rfft(signal)))

    fs = rfftfreq(signal.size, d=d)

    # Équivalent à
    # return fs, ys[0], ys[1], ...
    return fs, *ys
