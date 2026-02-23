============================
 Module Python
============================

--------------
Installation
--------------

Pour installer ce module, vous pouvez utiliser la commande

.. code-block:: shell

	python3.14 -m pip install xphs1903@1

Ou pour installer le module dans un nouvel environnement virtuel,

.. code-block:: shell

	python3.14 -m pipenv install xphs1903@1

--------------
Utilisation
--------------

Ce module assume que son compagnon Arduino a aussi été installé.
Une fois le programme Arduino inclut en exemple compilé et téléchargé,
vous pouvez lancer le programme ``demo.py`` ainsi:

.. code-block:: shell

	python3.14 -m xphs1903

Pour l'inclure à votre projet, utilisez l'énoncé ``import xphs1903`` normale
de Python.

----------------------------
Implémentation
----------------------------

.. automodule:: xphs1903
	:members:

Définitions uniformes
----------------------

.. automodule:: xphs1903.defs
	:members:

Communication avec le micro-contrôleur
---------------------------------------

.. automodule:: xphs1903.mesure
	:members:

Analyse des données
--------------------

.. automodule:: xphs1903.analyse
	:members:

Affichage des données
----------------------

.. automodule:: xphs1903.afficher
	:members:
