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

# Module de la bibliothèque standard
# Permet de tenir compte du temps
# En particulier, de mesurer le nombre de ns depuis le début
# de l'exécution du programme.
import time

# Port de communication série du Arduino
# Pour trouver quel port utiliser:
# <https://pythonhosted.org/pyserial/tools.html#module-serial.tools.list_ports>
PORT: str = '/dev/cu.usbmodemFA13201'

# Débit de communication
# Doit correspondre à la constante équivalente dans le programme
# oxy_base.ino sinon les programmes ne pourront pas communiquer.
DEBIT: int = 115200 # Le plus rapide possible pour notre micro-contrôleur
DELAI: int = 1 # Attente en lecture
ESPACEMENT: int = 1e6 # [ns] Temps d'attente entre les mesures, en ns

# Facteurs de conversion
ns2s: float = 1e-9 # Pour l'axe du temps
GHz2Hz: float = 1e9 # Pour l'axe des fréquences

# Définition des indices pour les deux types de mesures
IR: int = 0
VIS: int = 1

# Définition des indices pour les deux types de graphiques
BRUT: int = 0
FFT: int = 1

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

def prendre_mesure(res: list[list[int]],
               ser: serial.Serial) -> tuple[int|None]:
    temps = time.process_time_ns()
    res[0].append(temps)
    
    for i in range(1, len(res)):
        ser.write(bytes([i-1]))
        ser.flush()
        ligne = ser.readline().decode('utf-8').strip()
        
        if ligne.isdigit():
            res[i].append(int(ligne))
        else:
            res[i].append(None)

    return [x[-1] for x in res]

def plot(res: list[list[int]],
         fig: mpl.figure.Figure):
    
    fs, *fft_pd = fft(res) # Calculer la FFT
    ts = res[0]
    for i, (pd, fpd) in enumerate(zip(res[1:], fft_pd)):
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
        
        # Afficher jusqu'aux 200 derniers points
        N: int = min(len(ts), 10000)
        fig.axes[BRUT].lines[i].set_data(np.array(ts[-N:])*ns2s, pd[-N:])
        xs = ts[-N]*ns2s, ts[-1]*ns2s
        dx = xs[1] - xs[0]
        fig.axes[BRUT].set_xlim(*xs)
        fig.axes[BRUT].set_xticks(xs, [f'-{dx}', '0'])

        # Afficher la transformée de Fourier
        fig.axes[FFT].lines[i].set_data(fs*GHz2Hz, fpd)
    
    fig.axes[FFT].set_ylim(0, max(max(f) for f in fft_pd))

    plt.pause(0.01) # Petite pause pour permettre l'affichage correct

def setup(pds: tuple[int] = (IR, VIS),
          port: str = PORT,
          debit: int = DEBIT,
          delai: int = DELAI):
    # Initialisation des paramètres importants
    
    # On utilise la fonction list plutôt que la valeur litérale [] pour ne pas
    # créer un unique object commun répété plusieurs fois dans la liste.
    # Voir https://stackoverflow.com/q/366422 pour ce genre de problèmes.
    mes: list[list[int]] = [list() for pd in range(len(pds)+1)]
    ser = serial.Serial(port, baudrate=debit, timeout=delai)
    
    # Paramètres des graphiques
    # Affichage interactif, pour pouvoir suivre l'acquisition en direct
    plt.ion()
    
    # Créer une nouvelle figure, qui contiendra nos systèmes d'axes
    # fig.axes pour voir la liste des axes dans la console
    #fig = plt.figure()
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
    ax2.plot([], color='black', linestyle='--', label='IR')
    ax2.plot([], color='red', linestyle='--', label='VIS')
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

    return mes, ser, fig

def loop(res: list[list[int]],
         ser: serial.Serial,
         fig: mpl.figure.Figure):
        
    # Lecture des valeurs de chaque photodiode
    temps, val_ir, val_vis = prendre_mesure(res, ser)
    
    # Mise à jour du graphique
    plot(res, fig)

def setdown(res: list[list[int]],
            ser: serial.Serial,
            fig: mpl.figure.Figure):
    
    ser.close()
    plt.close(fig)

# ==================================
# = Fonctions d'analyse de données =
# ==================================

def fft(res: list[list[int]]) -> tuple[np.array]:
    N: int = min(len(res[0]), 10000)

    ys = []
    for sig in res[1:]:
        cadre = scipy.signal.windows.hann(N)
        signal = np.array(sig[-N:]) * cadre
        ys.append(np.abs(np.fft.rfft(signal)))
    
    fs = np.fft.rfftfreq(signal.size, d=ESPACEMENT)

    return fs, *ys


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
    
    params = setup() # Initialiser le programme avec les valeurs par défaut
    
    try:
        derniere_mesure = time.process_time_ns()
        
        # Cette boucle est infinie à toutes fins pratiques, càd équivalente à
        # while True:
        #   ...
        # Techniquement, elle s'arrête quand la fenêtre du graphique est fermée,
        # ou que l'utilisateur entre ^C sur la ligne de commande.
        while plt.get_fignums():
            if time.process_time_ns() > (derniere_mesure + ESPACEMENT):
                loop(*params) # Exécuter la fonction à répéter
                
                # S'il y a un problème de communication, reprendre la valeur
                # sans attendre.
                if None in [d[-1] for d in params[0]]:
                    for i in len(params[0]):
                        params[0][i].pop(-1) # Retirer la mauvaise valeur
                else:
                    derniere_mesure = params[0][0][-1]
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

