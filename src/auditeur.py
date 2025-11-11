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

PORT: str = '/dev/cu.usbmodemFA13201'
'''Port série à utiliser pour le programme

Sous Windows, ressemblera à 'COM2'. Sous les autres plate-formes,
ressemblera à '/dev/cu.usbmodemFA13201'. Le module :external:py:class:`serial <serial.Serial>`
a un outil dédié à la découverte des ports série disponibles, :py:mod:`serial.tools.list_ports`, ou :py:func:`serial.tools.list_ports.comports`.
'''

DEBIT: int = 115200
'''Débit de communication

Doit correspondre à la constante équivalente dans le programme
oxy_base.ino sinon les programmes ne pourront pas communiquer.

115200 est le débit le plus rapide pratique pour les Arduino nano et micro.
Un débit plus rapide cause des problèmes au niveau de l'acquisition et de
la fiabilité. Voir la documentation de :py:class:`serial <serial.Serial>` ou de :arduino:`Serial.begin <functions/communication/serial/begin/>`  pour plus de détails.

.. _documentation officielle:
    https://pythonhosted.org/pyserial/pyserial_api.html
'''

DELAI: float = 0.005 # Attente en lecture
'''Délai maximal en secondes avant d'abandonner une tentative de lecture

Certaines valeurs spéciales sont décrites dans la documentation officielle de :py:class:`serial <serial.Serial>`. Comme la fréquence de transfert d'un bit
est d'environ 100kHz (voir :py:const:`DEBIT`), le délai ne devrait pas être
plus petit que la période associée (0.01ms) multipliée par le nombre de bits
envoyés. Pour des chiffres, on peut assumer du ASCII 8b, avec un message long
(eg: ``1021 1012``) faisant donc un peut moins de 80b, on doit avoir au minimum
un délai de 0.8ms. Avec une petite marge, on arrive à 0.005s.
'''

# Définition des indices pour les deux types de graphiques
BRUT: int = 0 #: Index des graphiques de données dans fig.axes
FFT: int = 1 #: Index des graphiques de transformée de Fourier dans fig.axes

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
    for l in ser.readlines():
        if not l.strip():
            break

        try:
            nom, vs = l.split(b'=', 1)
            vs = [np.float64(v) for v in vs.strip(b'[] \r\n').split(b', ')]
            mes.insert(0, nom.strip().decode('utf-8'), vs)
            logging.info('l = %r', l)
            logging.info('mes =\\\n%r', mes.tail())
        except ValueError:
            logging.debug('l = %s', l)
            logging.exception('La dernière ligne lue n\'était pas conforme.')
            continue
    
    res = pd.concat([res, mes])

    return res

def plot(res: pd.DataFrame, fig: mpl.figure.Figure):
    '''Mise à jour du graphique avec de nouvelles données
    
    Met les graphiques contenus dans fig à jour avec les données de res.
    
    Parameters
    ----------
    res
        Liste des mesures prises. Structurée en ``[t, pd1, pd2, ...]``
    fig
        Figure contenant les différents graphiques
    '''
    logging.debug('res.size = %s', res.size)
    logging.debug('res.ts.size = %s', res.ts.size)
    logging.debug('res.tail() =\\\n%r', res.tail())
    if res.ts.size >= 256:
        fig.axes[BRUT].lines[0].set_data(res.ts, res.A0)
        fig.axes[BRUT].set_xlim(res.ts[res.ts.size-256], res.ts[res.ts.size-1]) 
        
        if not res.ts.size % 256:
            res = fft(res) # Calculer la FFT
        
            fig.axes[FFT].lines[0].set_data(res.fs, res.F)
            fig.axes[FFT].lines[1].set_data(res.fs, res.F2) 
            fig.axes[FFT].set_ylim(0, max(res.F.max(), res.F2.max()))

    plt.pause(0.01) # Petite pause pour permettre l'affichage correct

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
    ser = serial.Serial(port, baudrate=debit, timeout=delai)
    time.sleep(0.01)
    while ser.in_waiting:
        l = ser.readline().strip()
        if len(l) > 0:
            print(l)
        else:
            break
        time.sleep(0.01)
    
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
    ax2.set_ylim(auto=True)
    ax2.set_xlim(left=0, right=50)
    
    fig.tight_layout()
    plt.pause(0.01)
    plt.show()

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
    d: float = (res.ts[-N+1:] - res.ts[-N:-1]).mean()
    
    idx = res.index.size - N
    
    res.loc[idx:,'cadre'] = scipy.signal.get_window(cadre, N)
    res.loc[idx:, 'signal'] = res.A0[idx:] * res.cadre[idx:]
    
    logging.debug('res = \\\n%r', res.tail())
    logging.debug('res.signal = \\\n%r', res.signal[idx:])
    logging.debug('res.signal.to_numpy() = \\\n%r', res.signal[idx:].to_numpy())
    
    arr = res.signal[idx:].to_numpy()
    logging.debug('arr = %r', arr)
    tran = np.abs(np.fft.rfft(arr))
    logging.debug('tran = %r', tran)
    logging.debug('tran.size = %r', tran.size)
    
    idx2 = res.index.size - tran.size
    logging.debug('res.loc[idx2:, \'F2\'].size = %s', res.loc[idx2:, 'F2'].size)
    res.loc[idx2:, 'F2'] = tran
    res.loc[idx2:, 'fs'] = np.fft.rfftfreq(tran.size, d)
    
    return res

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
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

