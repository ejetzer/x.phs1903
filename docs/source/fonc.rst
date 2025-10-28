============================
 Définitions de fonctions 
============================

Pour faciliter la lecture du code, les arguments sont toujours dans l'ordre

``res: list[list[int]]``
	Une liste de listes d'entiers destinée à 
	contenir les mesures renvoyées par la
	:arduino:`communication série <functions/communication/serial/>` de
	l'Arduino.

``ser: serial.Serial``
	Un objet de contrôle de la communication
	série entre Python et l'Arduino. Voir :external+serial:class:`serial.Serial`.

``fig: mpl.figure.Figure``
	Un objet de présentation graphique. Voir :external+matplotlib:class:`matplotlib.figure.Figure`.

...
	Les autres arguments n'ont pas d'ordre
	particulier.

.. autofunction:: base.prendre_mesure

.. autofunction:: base.plot

--------------------------------
Analyse de données
--------------------------------

.. autofunction:: base.fft

.. literalinclude:: ../../src/base.py
	:lines: 306-322
	:dedent:
	:lineno-match:

-------------------------------
Structure du programme
-------------------------------

1. setup, appelée au début du programme pour configurer les différents objets.
   Équivalent à setup dans un programme Arduino.
2. loop, appelée à répétition, contient l'essentiel du programme.
   Équivalent à loop dans un programme Arduino.
3. setdown, appelée à la fin pour correctement fermer les objets.
   setdown n'a pas d'équivalent Arduino.

.. autofunction:: base.setup

.. autofunction:: base.loop

.. autofunction:: base.setdown

Les trois fonctions sont appelées dans une structure de capture d'erreur

.. code-block:: python

    params = setup()
    try:
        while True:
            loop(*params)
    finally:
        setdown(*params)