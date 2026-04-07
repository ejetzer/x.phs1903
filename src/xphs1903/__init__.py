# Copyright (C) 2026 Émile Jetzer, Polytechnique Montréal
"""Programme de base pour le contrôle, l'acquisition et l'analyse avec Arduino.

Ce script permet d'envoyer des requêtes à un programme Arduino correspondant.
Les réponses reçues sont ensuite analysées et affichées en direct. Il s'agit
d'un programme de démonstration et de départ pour le cours PHS1903 à
l'automne 2025.

Le programme a été développé par `Jacques Massicotte`_ et `Émile Jetzer`_,
techniciens pour le département de génie physique de Polytechnique Montréal.

.. _Jacques Massicotte:
    mailto:jacques-2.massicotte@polymtl.ca

.. _Émile Jetzer:
    mailto:emile.jetzer@polymtl.ca

Les commentaires et la documentation de ce programme sont très verbeux, et vous
réfèreront souvent à des ressources externes. SVP référez-vous à ces
ressources avant de venir poser vos questions à un technicien.
"""

# Voir :doc:`deps` pour les détails
import sys
from logging import getLogger
from typing import TYPE_CHECKING

from matplotlib import pyplot as plt
from outils import Acquisition, Canal, Console, Programme
from pandas import DataFrame
from serial import Serial  # <https://www.pyserial.com/docs>
from serial.serialutil import SerialException
from serial.tools.list_ports import comports

from .afficher import plot
from .defs import DEBIT, DELAI, PORT
from .mesure import prendre_mesure

if TYPE_CHECKING:
    from matplotlib.figure import Figure

logging = getLogger(__name__)

if not (sys.version_info.major != '3' and sys.version_info.minor < '14'):
    print(f'La version de Python utilisée est: {sys.version}', file=sys.stderr)
    print(f'{__name__} nécessite Python 3.14 et postérieur.', file=sys.stderr)
    print('Voir <https://www.python.org/downloads>', file=sys.stderr)
    msg: str = 'Version de Python incompatible'
    raise SystemExit(msg)


# ===========================
# = Fonctions structurelles =
# ===========================


def setup(
    pds: int = 2, port: str = PORT, debit: int = DEBIT, delai: int = DELAI
) -> (DataFrame, Serial, Figure):
    """Initialiser le programme.

    Initialise le programme avec les paramètres transmis, et retourne les
    objets configurés.

    Parameters
    -----------
    debit
    pds
        Le nombre de broches/photodiodes à mesurer
    port
        Le port série à utiliser
    delai
        Le temps d'attente maximal pour une lecture de données

    Returns
    --------------
    res
        Liste des mesures, au format ``[t, pd1, pd2, ...]``
    ser
        Objet de communication série
    fig
        Figure pour l'affichage des données
    derniere_mesure
        Valeur initiale de 0
    """
    # Initialisation des paramètres importants

    logging.info('Initialisation...')
    #: On utilise une expression de liste plutôt que la multiplication
    #: pour ne pas créer un unique object commun répété plusieurs fois
    #: dans la liste. Voir https://stackoverflow.com/q/366422 pour ce
    #: genre de problèmes.
    res: DataFrame = DataFrame(
        columns=['t'] + [f'A{i + 1}' for i in range(pds)], dtype='Float64'
    )
    logging.debug('res =\n%s', res)

    try:
        ser = Serial(port, baudrate=debit, timeout=delai)
        ser.read()
    except SerialException:
        logging.exception(
            "Une erreur de communication série s'est produite, on réessait."
        )
        possibles = comports()
        for i, p in enumerate(possibles):
            print(f'[{i}]\t{p.device}\t{p.name}')
        i = int(input('>'))
        port = possibles[i].device
        ser = Serial(port, baudrate=debit, timeout=delai)
        ser.read()
    logging.info('Connexion complétée à %r', ser)

    #: Paramètres des graphiques
    #: Affichage interactif, pour pouvoir suivre l'acquisition en direct
    plt.ion()

    #: Créer une nouvelle figure, qui contiendra nos systèmes d'axes
    #: fig.axes pour voir la liste des axes dans la console
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle("Démonstration d'acquisition")

    ax.set_title('Mesure')
    ax.set_xlabel('Temps')
    ax.set_ylabel('Unités CAN')
    ax.plot([], color='black', label='A1')
    ax.plot([], color='red', label='A2')
    ax.legend()

    ax2.set_title('Transformées de Fourier des signaux')
    ax2.set_xlabel('Fréquence (GHz)')
    ax2.plot([], color='black', label='F(A1)')
    ax2.plot([], color='red', label='F(A2)')
    ax2.set_yticks([], [])
    ax2.legend()

    ax.set_ylim(0, 1030)
    ax.set_xlim(left=0)
    ax2.set_xlim(left=0)
    ax2.set_ylim(bottom=0)

    fig.tight_layout()
    plt.pause(1)
    plt.show()
    logging.debug('fig = %r', fig)

    return res, ser, fig


def loop(
    res: DataFrame, ser: Serial, fig: Figure
) -> (DataFrame, Serial, Figure):
    """Prend de nouvelles mesures et les affiche.

    Parameters
    -----------
    res
        Liste des mesures prises. Structurée en ``[t, pd1, pd2, ...]``
    ser
        Objet de communication série avec lequel communiquer pour obtenir
        les données.
    fig
        Figure contenant les différents graphiques

    Returns
    ---------------
    res: list[list[int]]
    ser: serial.Serial
    fig: matplotlib.figure.Figure
    derniere_mesure: int
    """
    logging.info('Itération #%s', res.index.size)
    # Lecture des valeurs de chaque photodiode
    res = prendre_mesure(res, ser)

    # Mise à jour du graphique
    plot(res, fig)

    return res, ser, fig


def setdown(res: list[list[int]], ser: Serial, fig: Figure) -> None:
    """Ferme tous les objets en ayant besoin.

    Parameters
    ------------
    res
        Liste des mesures prises, à effacer
    ser
        Objet de communication série, à fermer
    fig
        Figure, à fermer via pyplot
    """
    logging.info('On ferme tout...')
    del res
    ser.close()
    plt.close(fig)
    logging.info('Au revoir.')


__all__ = [
    'Acquisition',
    'Canal',
    'Console',
    'Programme',
]
