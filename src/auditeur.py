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
import pandas as pd # <https://pandas.pydata.org/>
import logging # <https://docs.python.org/3/library/logging.html>
import time # <https://docs.python.org/3/library/time.html>

# Définitions
# Voir :doc:`defs`

DELIM_VAL = b'[]\r\n '
'''Caractères délimitant les listes de valeurs dans la communication avec le micro-contrôleur

Le programme d'annonceur sur le micro-contrôleur envoie les données avec la
même syntaxe qu'une liste Python. On peut donc retirer les caractères de
:py:var:`DELIM_VAL` des bouts de la chaîne avec :py:meth:`str.strip`.
'''

SEP_NOM = b'='
'''Séparateur du nom de variable ou colonne et de la liste de données

Le nom de la variable ou colonne lue sur la ligne série est séparé des données par un signe ``=``.
'''

SEP_VAL = b','
'''Séparateur de valeurs

Les valeurs dans la liste sont séparées par des virgules.
'''

SEP_LIGNE = b'\r\n'
'''Séparateur de ligne du micro-contrôleur

Arduino utilise la séquence ``\\r\\n`` pour finir les lignes, au lieu du plus
commun ``\\n``. Il faut donc régler nos séparateurs en conséquence.
'''

SEP_BLOC = SEP_LIGNE*2
'''Séparateur de blocs de données

Les blocs de données sont séparés par une ligne vide, soit deux saut de ligne/retours chariots.
'''

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
'''Délai de pause de l'afficahge :py:mod:`matplotlib`

:py:mod:`matplotlib` a besoin d'être interrompu à certains moments pour que le
programme d'acquisition continue de s'exécuter. La pause n'a pas besoin d'être longue.
'''

# Définition des indices pour les deux types de graphiques
BRUT: int = 0 #: Index des graphiques de données dans fig.axes
FFT: int = 1 #: Index des graphiques de transformée de Fourier dans fig.axes

N_max: int = 256
'''Nombre de mesures attendues

Le programme du micro-contrôleur envoie un nombre précis de mesures dans chaque 
bloc. De vérifier qu'on reçoit le bon nombre de mesures est un test facile pour
valider l'intégrité des données. Le nombre précis est déterminé par, entre
autres:

- La mémoire disponible sur l'Arduino
- Le type des variables stockant les mesures
- La précision du convertisseur analogique-numérique
- La fréquence d'échantillonage
- L'intervalle sur lequel les mesures sont prises.
'''

us = 1e-6 # Facteur de conversion de µs → s
MHz = 1e6 # Facteur de conversion de MHz → Hz

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
    mes: pd.DataFrame = pd.DataFrame(dtype=np.float64)
    '''Cadre de données, :py:class:`pandas.DataFrame` pour les nouvelles mesures'''
    
    bloc_cru: bytes = ser.read_until(SEP_BLOC)
    '''Bloc de données lues de la ligne série'''
    
    # Si on n'a reçu aucune données, on ne pourra pas en faire l'analyse
    # ou les afficher. Donc on quitte la fonction sans modifier :py:var:`res`.
    # Alternativement, vous pourriez soulever une erreur ou signaler le 
    # problème de différentes façons. J'ai mis quelques exemples en commentaire.
    if len(bloc_cru) == 0:
        #logging.warning('Aucune donnée reçue.')
        #raise RuntimeWarning('Aucune donnée n\'a été reçue.')
        return res
    
    bloc_ecourte = bloc_cru.strip() # Enlever les caractères invisibles
    lignes = bloc_ecourte.split(SEP_LIGNE) # Diviser par ligne
    for l in lignes:
        if SEP_NOM not in l: # Vérifier qu'on a bien une ligne de mesures
            #logging.warning('Pas de \'=\' présent dans %r', l)
            #raise RuntimeError('Pas de \'=\' présent')
            return res

        nom, valeurs = l.split(SEP_NOM, 1)
        
        # Retirer les caractères invisibles
        nom = nom.strip()\
                 .decode('utf-8') # Convertire de :py:type:`bytes` à :py:type:`str`
        
        # Retirer les caractères invisibles et :py:var:`DELIM_VAL`
        valeurs_isolees = valeurs.strip(DELIM_VAL)
        
        # Séparer les valeurs par :py:var:`SEP_VAL`
        valeurs_separees = valeurs_isolees.split(SEP_VAL)
        
        # Convertir de :py:type:`bytes` à :py:class:`numpy.float64`
        valeurs_converties = [np.float64(v) for v in valeurs_separees]
        
        # La tranformée de Fourier contient moitié moins de valeurs que
        # les données. Il faut donc les égaliser avant de les mettre
        # dans le même ``pandas.DataFrame``. Une alternative serait 
        # d'utiliser un ``pandas.DataFrame`` pour les données et un
        # pour la transformée de Fourier.
        diff = len(mes.index) - len(valeurs_converties) # Différence de longueur
        diff = diff if diff > 0 else 0 # Validation
        # Voir :py:func:`numpy.pad`.
        # Les positions ajoutées en début de liste auront la valeur
        # :py:`numpy.nan`, qui représente une valeur numérique non-définie.
        valeurs_compensees = np.pad(valeurs_converties,
                                    (diff, 0),
                                    constant_values=np.nan)
        
        # Voir :py:meth:`pandas.DataFrame.insert`
        # Ajouter la ligne lue comme une nouvelle colonne de 
        # :py:var:`mes`.
        mes.insert(0, nom, valeurs_compensees)
    
    # Voir :py:func:`pandas.concat`
    # Ajouter les données rangées dans :py:var:`mes` à 
    # :py:var:`res`.
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
    N
        Nombre maximal de données.
    '''
    
    # Si on n'a pas assez de données, on attend.
    # En pratique, ça veut dire que le tableau de données
    # est vide.
    if res.ts.size < N:
        return

    # Axe du temps, converti de us à s.
    ts = res.ts.to_numpy()[-N:] * us
    
    # Mesures à la broche A0 (ou autres broches programmées)
    A0 = res.A0.to_numpy()[-N:]
    
    # En cas de valeurs problématiques dans la plage à afficher,
    # on passe à la prochaine.
    if any([np.isnan(ts).sum(), np.isnan(A0).sum()]):
        return

    # On change les valeurs des courbes de mesures
    fig.axes[BRUT].lines[0].set_data(ts, A0)
    fig.axes[BRUT].set_xlim(ts[0], ts[-1])
    A0_max = 256 if A0.max() < 257 else 1024
    fig.axes[BRUT].set_ylim(0, A0_max)
    plt.pause(DELAI_PLT) # Petite pause pour permettre l'affichage correct
    
    # Axe des fréquences, converti de MHz à Hz
    fs = res.fs.to_numpy()[-N//2:] * MHz
    fig.axes[FFT].set_xlim(fs[0], fs[-1])
    if any(np.isnan(fs)):
        return
    
    # Spectre calculé sur le Arduino
    F = res.F.to_numpy()[-N//2:]
    F /= F.max()
    if not np.isnan(F).sum():
        fig.axes[FFT].lines[0].set_data(fs, F)
    else:
        logging.warning('Pas de FFT Arduino.')
    
    # Spectre calculé avec Python
    F2 = res.F2.to_numpy()[-N//2:]
    F2 /= F2.max()
    if not np.isnan(F2).sum():
        fig.axes[FFT].lines[1].set_data(fs, F2)
    else:
        logging.warning('Pas de FFT Python.')
    
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
    time.sleep(2) # On laisse le temps au Arduino de se réveiller
    
    # La première ligne envoyée par le programme Arduino affiche les paramètres
    # du micro-contrôleur.
    l = ser.read_until(SEP_BLOC).strip()
    print(l.decode('utf-8'))
    
    #: Paramètres des graphiques
    #: Affichage interactif, pour pouvoir suivre l'acquisition en direct
    plt.ion()
    
    #: Créer une nouvelle figure, qui contiendra nos systèmes d'axes
    #: fig.axes pour voir la liste des axes dans la console
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle('Démonstration de principe d\'un programme d\'analyse pour un oxymètre de pouls')
    
    ax.set_title('Mesures')
    ax.set_xlabel('Temps (s)')
    ax.set_ylabel('Unités CAN (5V / 1024 bits)')
    ax.plot([], color='black', label='A0', ls=':', marker='.')
    ax.legend()
    
    ax2.set_title('Transformées de Fourier des signaux')
    ax2.set_xlabel('Fréquence (Hz)')
    ax2.plot([], color='black', label='FFT (Arduino)', ls=':')
    ax2.plot([], color='red', label='FFT (Python)', ls=':')
    ax2.set_yticks([], [])
    ax2.legend()

    ax.set_ylim(0, N_max+5)
    ax2.set_ylim(0, 1)
    
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
    
    # Calculs et analyse
    # Dans cet exemple il n'y a que la transformée de Fourier,
    # mais vous allez devoir y ajouter d'autres fonctions.
    if res.ts.size >= N_max:
        res = fft(res)
    else:
        logging.warning('Pas de calcul de FFT.')
    #res = SpO_2(res)
    #res = un_train_arrive(res)
    
    # C'est ici que des fonctions pour réagir aux mesures devraient aller
    #signaler_absence_pouls(res)
    #bouger_barrière(res)
    
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
    
    # Si la communication série n'est pas fermée correctement, elle restera
    # ouverte et bloquera tout autre programme qui essaiera d'y accéder,
    # comme par exemple votre programme dans 5s, ou l'IDE Arduino.
    ser.close()
    plt.close(fig)

# ==================================
# = Fonctions d'analyse de données =
# ==================================

def estime_d(res: pd.DataFrame, N: int = N_max) -> float:
    '''Estimé de la période d'échantillonage
    
    Parameters
    ===============
    res
        Les mesures prises, incluant la liste des mesures de temps
    N
        Le nombre de mesures depuis la dernière à considérer
    
    Returns
    ========
    d
        L'espacement moyen entre chaque mesure
    '''
    tôt: np.ndarray[int] = res.ts.to_numpy()[-N:-1]
    tard: np.ndarray[int] = res.ts.to_numpy()[-N+1:]
    diff: np.ndarray[int] = tard - tôt
    d: float = diff.mean()
    
    return d

def fft(
    res: pd.DataFrame,
    N: int = N_max,
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
    d_t: float = estime_d(res, res.index.size)
    logging.info('d ≅ %sµs = %ss, d_t=%sµs', d, d*us, d_t)
    logging.info('f = %sMHz = %skHz = %sHz', 1/d, 1000/d, MHz/d)
    
    idx = res.index.size - N
    
    # Mesure de l'intervalle couvert par la série de mesure
    # Utile pour vérifier les calculs liés à n, f_{acq}, d, etc.
    intervalle: int = res.ts.to_numpy()[-1] - res.ts.to_numpy()[-N]
    logging.info('\\Delta t = %sµs', intervalle)
    
    cadre: np.ndarray[float] =  scipy.signal.get_window(cadre, N)
    res.loc[idx:,'cadre'] = cadre
    
    A0 = res.A0.to_numpy()[idx:]
    A0 = A0 - A0.mean()
    signal = A0 * cadre
    res.loc[idx:, 'signal'] = signal
    
    fft = np.abs(np.fft.rfft(signal))
    idx2 = res.index.size - fft.size
    res.loc[idx2:, 'F2'] = fft

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

