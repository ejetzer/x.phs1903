PORT: str = '/dev/cu.usbmodemFD1301'
"""Port série à utiliser pour le programme

Sous Windows, ressemblera à 'COM2'. Sous les autres plate-formes,
ressemblera à '/dev/cu.usbmodemFA13201'. Le module :external:py:class:`serial <serial.Serial>`
a un outil dédié à la découverte des ports série disponibles, :py:mod:`serial.tools.list_ports`, ou :py:func:`serial.tools.list_ports.comports`.
"""

DEBIT: int = 1000000
"""Débit de communication

Doit correspondre à la constante équivalente dans le programme
oxy_base.ino sinon les programmes ne pourront pas communiquer.

115200 est le débit le plus rapide pratique pour les Arduino nano et micro.
Un débit plus rapide cause des problèmes au niveau de l'acquisition et de
la fiabilité. Voir la documentation de :py:class:`serial <serial.Serial>` ou de :arduino:`Serial.begin <functions/communication/serial/begin/>`  pour plus de détails.

.. _documentation officielle:
    https://pythonhosted.org/pyserial/pyserial_api.html
"""

DELAI: float = 0.005  # Attente en lecture
"""Délai maximal en secondes avant d'abandonner une tentative de lecture

Certaines valeurs spéciales sont décrites dans la documentation officielle de :py:class:`serial <serial.Serial>`. Comme la fréquence de transfert d'un bit
est d'environ 100kHz (voir :py:const:`DEBIT`), le délai ne devrait pas être
plus petit que la période associée (0.01ms) multipliée par le nombre de bits
envoyés. Pour des chiffres, on peut assumer du ASCII 8b, avec un message long
(eg: ``1021 1012``) faisant donc un peut moins de 80b, on doit avoir au minimum
un délai de 0.8ms. Avec une petite marge, on arrive à 0.005s.
"""

# Définition des indices pour les deux types de graphiques
BRUT: int = 0  #: Index des graphiques de données dans fig.axes
FFT: int = 1  #: Index des graphiques de transformée de Fourier dans fig.axes

__all__ = [
    'BRUT',
    'DEBIT',
    'DELAI',
    'FFT',
    'PORT',
]
