=======================
 Programme principal 
=======================

À cause de la condition ``__name__ == '__main__'``, cette partie du programme
ne s'exécute que si ce module est exécuté directement, par exemple avec la 
commande

.. code-block:: console

	$ python3.14 base.py

Si vous importez le module dans votre propre programme pour l'utiliser, vous
aurez à re-créer une structure similaire à celle ci-dessous, qui devrait vous
rappeler celle d'un programme Arduino.

------------
Code
------------

.. literalinclude:: ../../src/base.py
	:language: python
	:lines: 324-

------------
Débogage
------------

Pour déboguer votre programme, je vous conseille d'utiliser le module
:external+python:module:pdb, inclu dans la librairie standard de Python.

.. code-block:: console

	$ python3.14 -m pdb -c continue base.py

Le programme s'exécutera jusqu'à la première erreur, puis vous pourrez
examiner les valeurs des variables et le contexte du code.
