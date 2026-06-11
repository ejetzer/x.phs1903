============================
 Démarrage rapide
============================

#. Ouvrir votre projet VS Code
#. Activer son environnement virtuel
#. Y installer le module ``x.phs1903`` avec ``pip``:

  .. code:: shell

    pip install x.phs1903@2

#. Ouvrir l'IDE Arduino
#. Télécharger le module Arduino compressé
#. Cliquer sur :menuselection:`Croquis --> Importer une bibliothèque --> Ajouter la bibliothèque .ZIP...`
#. Sélectionner l'archive du module Arduino
#. Ouvrir l'exemple `phsblink`
#. Le télécharger sur l'Arduino et vérifier qu'il fonctionne
#. Ouvrir l'exemple `phsecho`
#. Le télécharger sur l'Arduino et vérifier qu'il fonctionne en utilisant la ligne série
#. Exécuter ``python -m xphs1903.demos.echo`` dans VS Code
#. Valider le fonctionnement.

Félicitations!

.. --------------
.. Utilisation
.. --------------
..
.. Ce module assume que son compagnon Arduino a aussi été installé.
.. Une fois le programme Arduino inclut en exemple compilé et téléchargé,
.. vous pouvez lancer le programme ``demo.py`` ainsi:
..
.. .. code-block:: shell
..
.. 	python3.14 -m xphs1903
..
.. Pour l'inclure à votre projet, utilisez l'énoncé ``import xphs1903`` normal
.. de Python.
