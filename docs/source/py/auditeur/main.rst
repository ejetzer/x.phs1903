=======================
 Programme principal 
=======================

Pour exécuter le programme de démonstration, vous pouvez entrer une commande
comme:

.. _runcmd:

.. code-block:: console

	$ python3.14 base.py

La partie sous le bloc conditionnel à ``__name__ == '__main__'`` 
ne s'exécute que si ce module est exécuté directement, par exemple avec :ref:`la 
commande précédente <runcmd>`.

Si vous voulez importer le programme, vous pouvez commencer avec un fichier
comme:

.. code-block:: python

	import base # Assumant que base.py est dans le même répertoire
	
	# Vos définitions
	
	if __name__ == '__main__':
		# Votre code

------------
Débogage
------------

Pour déboguer votre programme, je vous conseille d'utiliser le module
:external:py:mod:`pdb`, inclu dans la librairie standard de Python.

.. code-block:: console

	$ python3.14 -m pdb -c continue base.py

Le programme s'exécutera jusqu'à la première erreur, puis vous pourrez
examiner les valeurs des variables et le contexte du code.
