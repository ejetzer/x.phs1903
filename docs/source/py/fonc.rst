.. _fonc:

============================
 Définitions de fonctions 
============================

Pour faciliter la lecture du code, les arguments sont toujours dans l'ordre

.. py:data:: res
	:type: list[list[int]]
	
	Une liste de listes d'entiers destinée à 
	contenir les mesures renvoyées par la
	:arduino:`communication série <functions/communication/serial/>` de
	l'Arduino.

.. py:data:: ser
	:type: serial.Serial
	
	Un objet de contrôle de la communication
	série entre Python et l'Arduino.

.. py:data:: fig
	:type: matplotlib.figure.Figure
	
	Un objet de présentation graphique.


Les autres arguments n'ont pas d'ordre particulier.

.. autofunction:: base.prendre_mesure

	:py:func:`prendre_mesure <base.prendre_mesure>` demande
	(avec :py:meth:`serial.Serial.write`) de nouvelles données au micro-contrôleur,
	puis lit les valeurs envoyées (avec :py:meth:`serial.Serial.readline`). C'est
	ce qu'on appelle une architecture :term:`serveur-client`, où le client, notre
	programme Python, communique avec le serveur, notre micro-contrôleur, qui
	exécute ses demandes. Ce n'est pas la seule architecture possible pour un
	programme de communication série. Notamment, le Arduino pourrait spontanément
	transmettre des données via la ligne série, et le programme Python ne ferait
	qu'attendre les blocs de données.
	
	Notez que l'architecture serveur-client offre un meilleur contrôle via le
	programme client, par exemple pour allumer ou éteindre des DÉLs sur demande.

.. autofunction:: base.plot

.. _analyse:

--------------------------------
Analyse de données
--------------------------------

.. autofunction:: base.fft

.. _structure:

-------------------------------
Structure du programme
-------------------------------

1. :py:func:`setup <base.setup>`, appelée au début du programme pour configurer les différents objets.
   Équivalent à setup dans un programme Arduino.
2. :py:func:`loop <base.loop>`, appelée à répétition, contient l'essentiel du programme.
   Équivalent à loop dans un programme Arduino.
3. :py:func:`setdown <base.setdown>`, appelée à la fin pour correctement fermer les objets.
   setdown n'a pas d'équivalent Arduino.

.. autofunction:: base.setup

.. autofunction:: base.loop

.. autofunction:: base.setdown

Les trois fonctions sont appelées dans une
:ref:`structure de capture d'erreur <try>`:

.. code-block:: python
	:emphasize-lines: 2,6

	*params, derniere_mesure = setup()
	try:
		while matplotlib.get_fignums() > 0:
			if time.process_time_ns() > (derniere_mesure + ESPACEMENT):
				*params, derniere_mesure = loop(*params)
	finally:
		setdown(*params)

Cette structure de programme est similaire à celle d'un
programme :arduino:`programme Arduino <#structure>`:

#. Une fonction :py:func:`setup <base.setup>`
   (:arduino:`setup <structure/sketch/setup/>`) invoquée au début du programme,
#. Une fonction :py:func:`loop <base.loop>`
   (:arduino:`loop <structure/sketch/loop/>`) exécutée à répétition.

Notre programme Python a aussi une fonction :py:func:`setdown <base.setdown>`
qui est exécutée à la fin du programme. Cette fonction n'a pas d'équivalent
dans un programme Arduino: un programme Python est généralement démarré,
utilisé puis quitté, alors qu'un micro-contrôleur est généralement initialisé
puis laissé en exécution indépendante.

La structure conditionnelle

.. code-block:: python

	if time.process_time_ns() > (derniere_mesure + ESPACEMENT):
		*params, derniere_mesure = loop(*params)

règle la demande de mesures provenant du micro-contrôleur, et limite
l'exécution de la boucle: elle ne s'exécute qu'au
:py:const:`ESPACEMENT <base.ESPACEMENT>` ns.
Sans une structure équivalente, on se retrouve à noyer la ligne de
communication série.
