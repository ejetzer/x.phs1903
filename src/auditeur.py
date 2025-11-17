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
import pandas as pd
import logging
import time

# Définitions
# Voir :doc:`defs`

DELIM_VAL = b'[]\r\n '
SEP_NOM = b'='
SEP_VAL = b','
SEP_LIGNE = b'\r\n'
SEP_BLOC = SEP_LIGNE*2

PORT: str = '/dev/cu.usbmodemFA13201'
'''Port série à utiliser pour le programme

Sous Windows, ressemblera à 'COM2'. Sous les autres plate-formes,
ressemblera à '/dev/cu.usbmodemFA13201'. Le module :external:py:class:`serial <serial.Serial>`
a un outil dédié à la découverte des ports série disponibles, :py:mod:`serial.tools.list_ports`, ou :py:func:`serial.tools.list_ports.comports`.
'''

DEBIT: int = 1000000
'''Débit de communication

Doit correspondre à la constante équivalente dans le programme
oxy_base.ino sinon les programmes ne pourront pas communiquer.

115200 est le débit le plus rapide pratique pour les Arduino nano et micro.
Un débit plus rapide cause des problèmes au niveau de l'acquisition et de
la fiabilité. Voir la documentation de :py:class:`serial <serial.Serial>` ou de :arduino:`Serial.begin <functions/communication/serial/begin/>`  pour plus de détails.

.. _documentation officielle:
    https://pythonhosted.org/pyserial/pyserial_api.html
'''

DELAI: float = 2 # Attente en lecture
'''Délai maximal en secondes avant d'abandonner une tentative de lecture

Certaines valeurs spéciales sont décrites dans la documentation officielle de :py:class:`serial <serial.Serial>`. Comme la fréquence de transfert d'un bit
est d'environ 100kHz (voir :py:const:`DEBIT`), le délai ne devrait pas être
plus petit que la période associée (0.01ms) multipliée par le nombre de bits
envoyés. Pour des chiffres, on peut assumer du ASCII 8b, avec un message long
(eg: ``1021 1012``) faisant donc un peut moins de 80b, on doit avoir au minimum
un délai de 0.8ms. Avec une petite marge, on arrive à 0.005s.
'''

DELAI_PLT: float = 0.01

# Définition des indices pour les deux types de graphiques
BRUT: int = 0 #: Index des graphiques de données dans fig.axes
FFT: int = 1 #: Index des graphiques de transformée de Fourier dans fig.axes

N_max: int = 256

us = 1e-6
MHz = 1e6

def prendre_mesure[R: pd.DataFrame](res: R, ser: serial.Serial) -> R:
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
    mes = pd.DataFrame(dtype=np.float64)
    
    bloc_cru = ser.read_until(SEP_BLOC)
    
    if len(bloc_cru) == 0:
        return res
    
    bloc_ecourte = bloc_cru.strip()
    lignes = bloc_ecourte.split(SEP_LIGNE)
    for l in lignes:
        if b'=' not in l:
            return res

        nom, valeurs = l.split(SEP_NOM, 1)
        
        nom = nom.strip()\
                 .decode('utf-8')
        
        valeurs_isolees = valeurs.strip(DELIM_VAL)
        valeurs_separees = valeurs_isolees.split(SEP_VAL)
        valeurs_converties = [np.float64(v) for v in valeurs_separees]

        diff = len(mes.index) - len(valeurs_converties)
        diff = diff if diff > 0 else 0
        valeurs_compensees = np.pad(valeurs_converties,
                                    (diff, 0),
                                    constant_values=np.nan)
        
        mes.insert(0, nom, valeurs_compensees)
    
    res = pd.concat([res, mes], ignore_index=True)

    return res

def plot(res: pd.DataFrame, fig: mpl.figure.Figure, N: int = N_max):
    '''Mise à jour du graphique avec de nouvelles données
    
    Met les graphiques contenus dans fig à jour avec les données de res.
    
    Parameters
    ----------
    res
        Liste des mesures prises. Structurée en ``[t, pd1, pd2, ...]``
    fig
        Figure contenant les différents graphiques
    '''
    if res.ts.size < N:
        return

    ts = res.ts.to_numpy()[-N:] * us
    A0 = res.A0.to_numpy()[-N:]
    if any([np.isnan(ts).sum(), np.isnan(A0).sum()]):
        return

    fig.axes[BRUT].lines[0].set_data(ts, A0)
    fig.axes[BRUT].set_xlim(ts[0], ts[-1])
    plt.pause(DELAI_PLT)
    
    res = fft(res) # Calculer la FFT
    
    fs = res.fs.to_numpy()[-N//2:] * MHz
    F = res.F.to_numpy()[-N//2:]
    F2 = res.F2.to_numpy()[-N//2:]
    if any([np.isnan(fs).sum(), np.isnan(F).sum(), np.isnan(F2).sum()]):
        return
    
    fig.axes[FFT].lines[0].set_data(fs, F)
    fig.axes[FFT].lines[1].set_data(fs, F2)
    fig.axes[FFT].set_xlim(fs[0], fs[-1])
    fig.axes[FFT].set_ylim(0, max(F.max(), F2.max()))
    plt.pause(DELAI_PLT) # Petite pause pour permettre l'affichage correct

# ===========================
# = Fonctions structurelles =
# ===========================

def setup(port: str = PORT, debit: int = DEBIT, delai: int = DELAI) -> tuple[pd.DataFrame, serial.Serial, mpl.figure.Figure, int]:
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
    res: pd.DataFrame = pd.DataFrame(columns=['ts', 'A0', 'cadre', 'signal', 'F', 'fs', 'F2'], dtype=np.float64)
    ser = serial.Serial(port, baudrate=debit, timeout=DELAI)
    time.sleep(2)
    l = ser.read_until(SEP_BLOC).strip()
    print(l.decode('utf-8'))
    
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
    ax.plot([], color='black', label='A0')
    ax.legend()
    
    ax2.set_title('Transformées de Fourier des signaux')
    ax2.set_xlabel('Fréquence (Hz)')
    ax2.plot([], color='black', label='FFT (Arduino)')
    ax2.plot([], color='red', label='FFT (Python)')
    ax2.set_yticks([], [])
    ax2.legend()

    ax.set_ylim(0, 1030)
    ax.set_xlim(left=-200, right=0)
    ax2.set_ylim(bottom=0)
    ax2.set_ylim(bottom=0, auto=True)
    ax2.set_xlim(left=0, auto=True)
    
    fig.tight_layout()
    plt.pause(0.01)
    plt.show()
    plt.pause(0.01)

    return res, ser, fig

def loop(res: pd.DataFrame, ser: serial.Serial, fig: mpl.figure.Figure):
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
    
    Returns
    ---------------
    res: list[list[int]]
    ser: serial.Serial
    fig: matplotlib.figure.Figure
    derniere_mesure: int
    '''
    # Lecture des valeurs de chaque photodiode
    res = prendre_mesure(res, ser)
    
    # Mise à jour du graphique
    plot(res, fig)
    
    return res, ser, fig

def setdown(res: pd.DataFrame, ser: serial.Serial, fig: mpl.figure.Figure):
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
    ser.close()
    plt.close(fig)

# ==================================
# = Fonctions d'analyse de données =
# ==================================

def estime_d(res, N):
    tôt, tard = res.ts[-N:-1].to_numpy(), res.ts[-N+1:].to_numpy()
    diff = tard - tôt
    d: float = diff.mean()
    return d

def fft(
    res: pd.DataFrame,
    N: int = 256,
    cadre: str = 'hann'
) -> pd.DataFrame:
    '''Retourne la transformée de Fourier des données contenues dans :py:data:`res`. C'est une bonne idée de personnaliser cette fonction selon
    vos besoins. Pour bien comprendre ce que fait la fonction, vous devriez
    consulter :py:func:`scipy.signal.get_window`, :py:func:`numpy.fft.rfft` et
    :py:func:`numpy.fft.rfftfreq`. Pour les mathématiques derrière, consultez
    dans un premier lieu votre chargé de groupe.
    
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
    # Estimation de l'espacement, basé sur les mesures
    d: float = estime_d(res, N)
    logging.info('d ≅ %sµs', d)
    logging.info('f = %sMHz', 1/d)
    
    idx = res.index.size - N
    intervalle = res.ts.to_numpy()[-1] - res.ts.to_numpy()[-N]
    logging.info('\\Delta t = %sµs', intervalle)
    
    res.loc[idx:,'cadre'] = scipy.signal.get_window(cadre, N)
    res.loc[idx:, 'signal'] = res.A0[idx:] * res.cadre[idx:]
    
    arr = res.signal[idx:].to_numpy()
    tran = np.abs(np.fft.rfft(arr))
    
    idx2 = res.index.size - tran.size
    
    res.loc[idx2:, 'F2'] = tran

    fs = np.fft.rfftfreq(N, d)

    res.loc[idx2:, 'fs'] = fs

    return res

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    params = setup()
    
    try:
        # Cette boucle est infinie à toutes fins pratiques, càd équivalente à
        # while True:
        #   ...
        # Techniquement, elle s'arrête quand la fenêtre du graphique est fermée,
        # ou que l'utilisateur entre ^C sur la ligne de commande.
        while len(plt.get_fignums()) > 0:
            params = loop(*params)
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

