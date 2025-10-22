#
#  oxy_base.py
#  Python
#
#  Created by Jacques Massicotte in 2025-W.
#  Updated by Émile Jetzer on 2025-10-20.
#  Copyright 2025 JM&ÉJ. All rights reserved.
#

# Communication série avec le Arduino.
# pyserial sur PyPI
# <https://pypi.org/project/pyserial/>
import serial

# Analyse numérique
import numpy as np # <https://numpy.org/>
import scipy as sp # <https://scipy.org/>
import scipy.signal.windows

# Affichage des résultats
# <https://matplotlib.org/>
import matplotlib as mpl
import matplotlib.pyplot as plt

# logging facilite le traçage et la détection d'erreurs
# <https://docs.python.org/3/library/logging.html#module-logging>
import logging

import time
import os
import sys
import json

logger = logging.getLogger(__name__)

# Port de communication série du Arduino
# Pour trouver quel port utiliser:
# <https://pythonhosted.org/pyserial/tools.html#module-serial.tools.list_ports>
PORT: str = '/dev/cu.usbmodemFA13201'

# Débit de communication
# Doit correspondre à la constante équivalente dans le programme
# oxy_base.ino sinon les programmes ne pourront pas communiquer.
DEBIT: int = 115200 # Le plus rapide possible pour notre micro-contrôleur
DELAI: int = 1 # Attente en lecture
BASELINE_FILE = "baseline.json"

# Définition des indices pour les deux types de mesures
IR: int = 0
VIS: int = 1

# Commandes que le micro-contrôleur s'attend à recevoir
# IR    VIS
# i     v
CMDS: bytes = b'iv'

# ============================
# = Définitions de fonctions =
# ============================

# Pour faciliter la lecture du code, les arguments sont toujours dans l'ordre
# 1. res|mes: list[list[int]]   Une liste de listes d'entiers destinée à 
#                               contenir les mesures renvoyées par l'Arduino.
# 2. ser: serial.Serial         Un objet de contrôle de la communication
#                               série entre Python et l'Arduino.
# 3. pd: int                    La ph<otodiode à mesurer.
#                               Elle devrait avoir les valeurs des constantes
#                               IR et VIS.
# 4. pds: list[int]             Une liste de photodiodes à mesurer.
# 5. cmds: bytes                Une chaîne d'octets contenant les commandes
#                               pour demander une mesure de chaque
#                               photodiode.
# ...                           Les autres arguments n'ont pas d'ordre
#                               particulier.

def get_1(res: list[list[int]],
          ser: serial.Serial,
          pd: int,
          cmds: bytes,
          logger: logging.Logger = logger) -> int|None:
    # Vider les tampons de lecture et d'écriture
    # Ça revient à ignorer toute requête trop longue
    # ou données manquées.
    ser.reset_output_buffer()
    ser.reset_input_buffer()
    
    ser.write(cmds[pd:pd+1]) # Envoyer la commande
    ser.flush() # Vider le tampon d'écriture (envoyer toutes les instructions)
    octet = ser.read() # Lecture d'un octet
    
    if len(octet) == 1:
        val = int.from_bytes(octet)
        res[pd].append(val)
        return val
    else:
        # Conserver les valeurs d'erreurs permet
        # de facilement garder deux listes de même longueur.
        # On pourra ignorer les valeurs nulles plus tard.
        if 0 not in [len(x) for x in res]:
            logger.warning('%s: (%s, %s)', len(res[0]), res[0][-1], res[1][-1])
        else:
            logger.warning('Valeur ignorée.')
        res[pd].append(None)
        return None

def get_all(res: list[list[int]],
            ser: serial.Serial,
            pds: tuple[int] = (IR, VIS),
            cmds: bytes = CMDS,
            logger: logging.Logger = logger) -> tuple[int|None]:
    return tuple(get_1(res, ser, pd, cmds, logger=logger) for pd in pds)

def display(res: list[list[int]],
            pds: tuple[int],
            logger: logging.Logger = logger):
        import pandas
        cadre = pandas.DataFrame({'IR': res[IR], 'VIS': res[VIS]})
        print(cadre.tail())

def plot(res: list[list[int]],
         pds: tuple[int],
         fig: mpl.figure.Figure,
         logger: logging.Logger = logger):
    
    logging.debug('pds = %s', pds)
    logging.debug('fig = %s', fig)
    logging.debug('fig.axes = %s', fig.axes)
    logging.debug('fig.axes[0].lines = %s', fig.axes[0].lines)
    logging.debug('fig.axes[1].lines = %s', fig.axes[1].lines)
    
    for pd in pds:
        # fig est la figure passée en argument
        # fig.axes est la liste des axes contenus dans la figure
        # fig.axes[0] est l'axe qu'on utilise pour les données brutes
        # fig.axes[1] est l'axe qu'on utilise pour la FFT
        # fig.axes[i].lines est la liste des courbes dessinées sur fig.axes[i]
        # fig.axes[i].lines[pd] est la courbe associée à la photodiode pd, soit
        #   IR ou VIS
        # fig.axes[i].lines[pd].set_ydata permet de modifier les valeurs en y
        #   d'une courbe existante
        # fig.axes[i].lines[pd].get_ydata permet d'obtenir les valeurs en y
        #   d'une courbe existante.
        fig.axes[0].lines[pd].set_data(np.arange(len(res[pd])), res[pd])
        fig.axes[1].lines[pd].set_data(*fft(res[pd], logger=logger))
        fig.axes[0].set_xlim(0, len(res[pd]))
        plt.pause(0.01)

def setup(pds: tuple[int] = (IR, VIS),
          cmds: bytes = CMDS,
          port: str = PORT,
          debit: int = DEBIT,
          delai: int = DELAI,
         logger: logging.Logger = logger):
    # Initialisation des paramètres importants
    
    # On utilise la fonction list plutôt que la valeur litérale [] pour ne pas
    # créer un unique object commun répété plusieurs fois dans la liste.
    # Voir https://stackoverflow.com/q/366422 pour ce genre de problèmes.
    mes: list[list[int]] = [list() for pd in pds]
    logger.debug('%s', mes)
    
    ser = serial.Serial(port, baudrate=debit, timeout=delai)
    logger.debug('%s', ser)
    
    # Paramètres des graphiques
    # Affichage interactif, pour pouvoir suivre l'acquisition en direct
    logging.info('Paramétrage du graphique...')
    plt.ion()
    logging.info('Mode interactif activé.')
    #plt.xkcd()
    # Créer une nouvelle figure, qui contiendra nos systèmes d'axes
    # fig.axes pour voir la liste des axes dans la console
    fig = plt.figure()
    logging.debug('%r', fig)
    # Créer un premier système d'axes dans fig
    ax = fig.gca()
    logging.info('Système d\'axes créé.')
    ax.plot([])
    ax.plot([])
    logging.info('Graphiques vides initialisés.')
    # Créer un système d'axe avec les mêmes absisses mais une échelle verticale
    # différente (pour représenter la transformée de Fourier sur le même
    # graphique)
    ax2 = ax.twinx()
    ax2.plot([])
    ax2.plot([])
    fig.tight_layout()
    logging.info('Axes pour la transformée de Fourier créés.')
    ax.set_ylim(0, 255)
    ax2.set_ylim(0, 1.25)
    plt.pause(0.01)
    plt.show()

    return mes, ser, pds, cmds, fig, logger

def loop(res: list[list[int]],
         ser: serial.Serial,
         pds: tuple[int],
         cmds: bytes,
         fig: mpl.figure.Figure,
         logger: logging.Logger = logger):
    
    if 35 < len(res[0]) < 45:
        breakpoint()
        
    # Lecture des valeurs de chaque photodiode
    val_ir, val_vis = get_all(res, ser, pds, cmds, logger=logger)
    logger.info('%s: (%s, %s)', len(res[0]), res[0][-1], res[1][-1]) # Affichage sur la console.
    
    # Mise à jour du graphique
    plot(res, pds, fig, logger=logger)
    
    # Affichage des données
    #display(res, pds, logger=logger)

def setdown(res: list[list[int]],
            ser: serial.Serial,
            pds: tuple[int],
            cmds: bytes,
            fig: mpl.figure.Figure,
            logger: logging.Logger = logger):
    
    ser.close()

    plt.close(fig)
    logger.info('Fini')

# ==================================
# = Fonctions d'analyse de données =
# ==================================

def fft(res: list[int], logger: logging.Logger = logger) -> np.array:
    N: int = len(res)
    
    if N > 100:
        cadre = scipy.signal.windows.hann(N)
        signal = np.array(res) * cadre
        ys = np.abs(np.fft.rfft(signal))
    else:
        ys = np.ones(N)
    
    logger.debug('N = %s, N_{fft} = %s', N, ys)
    return np.arange(len(ys)), ys

def spo2(res: list[list[int]],
         n_f: int,
         logger: logging.Logger = logger) -> np.array:
    # Estimation du taux d'oxygénation
    # Voir <https://en.wikipedia.org/wiki/Pulse_oximetry>
    ir_fft = fft(res[IR])
    vis_fft = fft(res[VIS])
    
    ir_fn = ir_fft[n_f]
    vis_fn = vis_fft[n_f]
    ir_f0 = ir_fft[0]
    vis_f0 = vis_fft[0]
    R = (vis_fn / vis_f0) / (ir_fn / ir_f0)
    res = 110 - 25 * R
    return res


# =======================
# = Programme principal =
# =======================

# À cause de la condition __name__ == '__main__', cette partie du programme
# ne s'exécute que si ce module est exécuté directement, par exemple avec la 
# commande
#
# $ python3.14 oxy_base.py
#
# Si vous importez le module dans votre propre programme pour l'utiliser, vous
# aurez à re-créer une structure similaire à celle ci-dessous, qui devrait vous
# rappeler celle d'un programme Arduino.

# Débogage
# ------------
 
# Pour déboguer votre programme, je vous conseille d'utiliser le module pdb,
# inclu dans la librairie standard de Python.
#
# $ python3.14 -m pdb -c continue oxy_base.py
#
# Le programme s'exécutera jusqu'à la première erreur, puis vous pourrez
# examiner les valeurs des variables et le contexte du code.

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
     format='%(levelname)s:%(filename)s:%(lineno)s:%(funcName)s\t%(message)s')
    
    params = setup(logger=logger) # Initialiser le programme avec les valeurs par défaut
    logger.debug('''Paramètres:

- res = %r
- ser = %r
- pds = %r
- cmds = %r
- fig = %r
- logger = %r''', *params)
    
    try:
        while True: # Boucle infinie (ne s'arrêtera pas d'elle même)
            loop(*params) # Exécuter la fonction à répéter
    except KeyboardInterrupt:
        # Détection de la combinaison ^C pour arrêter le programme
        logger.critical('Sortie forcée par l\'utilisateur.')
    except Exception:
        logger.exception('Erreur inattendue dans l\'exécution du programme.')
    finally:
        # Procédures de fin
        # Ce bloc est toujours exécuté, peu importe la raison de l'arrêt
        # du programme.
        # eg: libérer le port série pour qu'il puisse être utilisé par d'autres
        # programmes.
        setdown(*params)

