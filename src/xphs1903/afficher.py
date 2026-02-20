from logging import getLogger

from .analyse import fft
from .defs import BRUT, FFT

logging = getLogger(__name__)

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from pandas import DataFrame


def plot(res: DataFrame, fig: Figure) -> None:
    """Mise à jour du graphique avec de nouvelles données.

    Met les graphiques contenus dans fig à jour avec les données de res.

    Parameters
    ----------
    res
        Liste des mesures prises. Structurée en ``[t, pd1, pd2, ...]``
    fig
        Figure contenant les différents graphiques
    """
    fs, *fft_pd = fft(res)  # Calculer la FFT
    ts = res[0]
    # Python permet le paquetage/dépaquetage dans les définitions de variables
    # On peut par exemple définir les mêmes variables avec les mêmes valeurs
    # de plusieurs manières différentes:
    #
    # a = 1                             a, b = 1, 2
    # b = 2
    #
    # Dans la boucle for qui suit, on utilise les fonctions
    # zip_ et enumerate_. zip_ permet d'itérer sur les valeurs de plusieurs
    # listes simultanément, et enumerate_ permet d'itérer sur les valeurs
    # et l'index d'une liste. Dans la boucle, on a donc:
    #
    # i: int = <index des éléments>
    # pd: list[float] = <données de la broche/photodiode i>
    # fpd: list[float] = <transformée de pd>
    for i, (pd, fpd) in enumerate(zip(res.iloc[:, 1:], fft_pd)):
        # fig est la figure passée en argument
        # fig.axes est la liste des axes contenus dans la figure
        # fig.axes[0] est l'axe qu'on utilise pour les données brutes
        # fig.axes[1] est l'axe qu'on utilise pour la FFT
        # fig.axes[i].lines est la liste des courbes dessinées sur fig.axes[i]
        # fig.axes[i].lines[pd] est la courbe associée à la photodiode pd
        # fig.axes[i].lines[pd].set_ydata permet de modifier les valeurs en y
        #   d'une courbe existante
        # fig.axes[i].lines[pd].get_ydata permet d'obtenir les valeurs en y
        #   d'une courbe existante.

        # Afficher jusqu'aux 200 derniers points
        fig.axes[BRUT].lines[i].set_data(ts, pd)
        fig.axes[BRUT].set_xlim(left=0, right=max(ts))

        # Afficher la transformée de Fourier
        fig.axes[FFT].lines[i].set_data(fs, fpd)
        fig.axes[FFT].set_xlim(right=max(fs))
        fig.axes[FFT].set_ylim(top=max(fpd))

    # fig.axes[FFT].set_ylim(0, max(max(f) for f in fft_pd))
    plt.pause(1e-10)  # Petite pause pour permettre l'affichage correct


def tab(res: DataFrame, fig: Figure) -> DataFrame:
    raise NotImplementedError


__all__ = [
    'plot',
]
