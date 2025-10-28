# -*- coding: utf-8 -*-

'''Programme de base pour le contrôle, l'acquisition et l'analyse avec Arduino

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
'''

# Voir :doc:`deps` pour les détails
import serial # <https://www.pyserial.com/docs>
import numpy as np # <https://numpy.org/>
import scipy as sp # <https://scipy.org/>
import scipy.signal.windows
import matplotlib as mpl # <https://matplotlib.org/>
import matplotlib.pyplot as plt
import logging
import time

# Définitions
# Voir :doc:`defs`

PORT: str = '/dev/cu.usbmodemFA13201'
'''Port série à utiliser pour le programme

Sous Windows, ressemblera à 'COM2'. Sous les autres plate-formes,
ressemblera à '/dev/cu.usbmodemFA13201'. Le module ``serial`` a un outil
dédié à la découverte des ports série disponibles:
<https://pythonhosted.org/pyserial/tools.html#module-serial.tools.list_ports>
'''

DEBIT: int = 115200
'''Débit de communication

Doit correspondre à la constante équivalente dans le programme
oxy_base.ino sinon les programmes ne pourront pas communiquer.

115200 est le débit le plus rapide pratique pour les Arduino nano et micro.
Un débit plus rapide cause des problèmes au niveau de l'acquisition et de
la fiabilité. Voir la `documentation officielle`_ pour plus de détails.

.. _documentation officielle:
    https://pythonhosted.org/pyserial/pyserial_api.html
'''

DELAI: float = 1 # Attente en lecture
'''Délai maximal en secondes avant d'abandonner une tentative de lecture

Certaines valeurs spéciales sont décrites dans la `documentation officielle`_.

.. _documentation officielle:
    https://pythonhosted.org/pyserial/pyserial_api.html
'''

ESPACEMENT: int = int(1e7) # [ns] Temps d'attente entre les mesures, en ns
'''Temps entre les mesures en ns

Ce paramètre est utilisé pour la prise de mesures et l'analyse par
transformée de Fourier.
'''

# Facteurs de conversion
ns2s: float = 1e-9 #: Conversion de ns à secondes pour les axes des graphiques
GHz2Hz: float = 1e9 #: Conversion de GHz à Hz pour les graphiques

# Définition des indices pour les deux types de graphiques
BRUT: int = 0 #: Index des graphiques de données dans fig.axes
FFT: int = 1 #: Index des graphiques de transformée de Fourier dans fig.axes

def prendre_mesure[R: list[list[int]]](res: R, ser: serial.Serial) -> R:
    '''Prise d'une mesure
    
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
'''
    # Mesure du temps auquel la mesure est prise
    temps: int = time.process_time_ns()
    
    mes: list[float] = [temps]
    for i in bytes(range(1, len(res))):
        # Pour demander la photodiode A0, envoyer l'octet \x00, ou
        # de façon équivalente bytes([0]).
        # En général, si on veut de A0 à A1, et qu'on itère de 1 à 2, on a
        #
        # A0    \x00    bytes([0])  bytes([1-1])
        # A1    \x01    bytes([1])  bytes([2-1])
        ser.write(i)
        ser.flush() # S'assurer que la commande est envoyée immédiatement.
        mes.append(ser.readline())

    mes[1:] = map(int, mes[1:])
    for r, m in zip(res, mes):
        r.append(m)

    return res

def plot(res: list[list[int]], fig: mpl.figure.Figure):
    '''Mise à jour du graphique avec de nouvelles données
    
    Met les graphiques contenus dans fig à jour avec les données de res.
    
    Parameters
    ----------
    res
        Liste des mesures prises. Structurée en ``[t, pd1, pd2, ...]``
    fig
        Figure contenant les différents graphiques
    '''
    fs, *fft_pd = fft(res) # Calculer la FFT
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
    for i, (pd, fpd) in enumerate(zip(res[1:], fft_pd)):
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
        fig.axes[BRUT].lines[i].set_data(np.array(ts)*ns2s, pd)
        fig.axes[BRUT].set_xlim(max(ts)*ns2s-2, max(ts)*ns2s)

        # Afficher la transformée de Fourier
        fig.axes[FFT].lines[i].set_data(fs*GHz2Hz, fpd)
    
    fig.axes[FFT].set_ylim(0, max(max(f) for f in fft_pd))
    plt.pause(1e-10) # Petite pause pour permettre l'affichage correct

# ===========================
# = Fonctions structurelles =
# ===========================

def setup(pds: int = 2, port: str = PORT, debit: int = DEBIT, delai: int = DELAI) -> tuple[list[list[int]], serial.Serial, mpl.figure.Figure, int]:
    '''Initialisation du programme
    
    Initialise le programme avec les paramètres transmis, et retourne les
    objets configurés.
    
    Parameters
    -----------
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
    '''
    # Initialisation des paramètres importants
    
    #: On utilise une expression de liste plutôt que la multiplication pour
    #: ne pas créer un unique object commun répété plusieurs fois dans la liste.
    #: Voir https://stackoverflow.com/q/366422 pour ce genre de problèmes.
    res: list[list[int]] = [[] for pd in range(pds+1)]
    ser = serial.Serial(port, baudrate=debit, timeout=delai)
    
    #: Paramètres des graphiques
    #: Affichage interactif, pour pouvoir suivre l'acquisition en direct
    plt.ion()
    
    #: Créer une nouvelle figure, qui contiendra nos systèmes d'axes
    #: fig.axes pour voir la liste des axes dans la console
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle('Démonstration de principe d\'un programme d\'analyse pour un oxymètre de pouls')
    
    ax.set_title('Mesures des photodiodes')
    ax.set_xlabel('Temps (s)')
    ax.set_ylabel('Unités CAN (5V / 1024 bits)')
    ax.plot([], color='black', label='IR')
    ax.plot([], color='red', label='VIS')
    ax.legend()
    
    ax2.set_title('Transformées de Fourier des signaux')
    ax2.set_xlabel('Fréquence (Hz)')
    ax2.plot([], color='black', label='IR')
    ax2.plot([], color='red', label='VIS')
    ax2.set_yticks([], [])
    ax2.legend()

    ax.set_ylim(0, 1030)
    ax.set_xlim(left=-200, right=0)
    ax2.set_ylim(bottom=0)
    ax2.set_ylim(auto=True)
    ax2.set_xlim(left=0, right=50)
    
    fig.tight_layout()
    plt.pause(0.01)
    plt.show()

    return res, ser, fig, 0

def loop(res: list[list[int]], ser: serial.Serial, fig: mpl.figure.Figure):
    '''Prend de nouvelles mesures et les affiche
    
    Parameters
    -----------
    res
        Liste des mesures prises. Structurée en ``[t, pd1, pd2, ...]``
    ser
        Objet de communication série avec lequel communiquer pour obtenir
        les données.
    fig
        Figure contenant les différents graphiques
    '''
    # Lecture des valeurs de chaque photodiode
    res = prendre_mesure(res, ser)
    
    # Mise à jour du graphique
    plot(res, fig)
    
    return res, ser, fig, res[0][-1]

def setdown(res: list[list[int]], ser: serial.Serial, fig: mpl.figure.Figure):
    '''Ferme tous les objets en ayant besoin
    
    Parameters
    ------------
    res
        Liste des mesures prises, à effacer
    ser
        Objet de communication série, à fermer
    fig
        Figure, à fermer via pyplot
    '''
    del res[:]
    ser.close()
    plt.close(fig)

# ==================================
# = Fonctions d'analyse de données =
# ==================================

def fft(res: list[list[int]], N_max: int = 500) -> tuple[np.array, ...]:
    '''Retourne la transformée de Fourier des données contenues dans res
    
    Parameters
    ------------
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
    '''
    N: int = min(len(res[0]), N_max) # Nombre de valeurs à considérer
    
    # Estimation de l'espacement, basé sur les mesures
    ts: list[float] = res[0]
    d: float = np.mean(np.array(ts[1:]) - np.array(ts[:-1]))

    ys = []
    for sig in res[1:]:
        cadre = scipy.signal.windows.hann(N)
        signal = np.array(sig[-N:]) * cadre
        ys.append(np.abs(np.fft.rfft(signal)))
    
    fs = np.fft.rfftfreq(signal.size, d=d)

    # Équivalent à
    # return fs, ys[0], ys[1], ...
    return fs, *ys

if __name__ == '__main__':
    *params, derniere_mesure = setup()
    
    try:
        # Cette boucle est infinie à toutes fins pratiques, càd équivalente à
        # while True:
        #   ...
        # Techniquement, elle s'arrête quand la fenêtre du graphique est fermée,
        # ou que l'utilisateur entre ^C sur la ligne de commande.
        while plt.get_fignums() > 0:
            if time.process_time_ns() > (derniere_mesure + ESPACEMENT):
                *params, derniere_mesure = loop(*params)
    except KeyboardInterrupt:
        # Détection de la combinaison ^C pour arrêter le programme
        logging.critical('Sortie forcée par l\'utilisateur.')
    except Exception:
        logging.exception('Erreur inattendue dans l\'exécution du programme.')
    finally:
        # Procédures de fin
        # Ce bloc est toujours exécuté, peu importe la raison de l'arrêt
        # du programme.
        # eg: libérer le port série pour qu'il puisse être utilisé par d'autres
        # programmes.
        setdown(*params)

