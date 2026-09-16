
Foire aux questions
#############################


Question #9: C'est quoi un «interpréteur»?
===========================================


.. index::
   single: python
   single: lexique


La documentation sur Read The Docs parle d'un «interpréteur» Python.
Qu'est-ce que c'est?



Réponse #17
------------

Un interpréteur est un programme qui lit un fichier de code source et
exécute immédiatement le code, sans le compiler au préalable.






Question #8: Que veut dire le `>>>` ou `$` en début de ligne de commande?
==========================================================================


.. index::
   single: python
   single: shell
   single: cli


Dans les exemples les commandes sont souvent précédées d'un ``>>>`` ou
d'un ``$``. Qu'est-ce que ça veut dire? Est-ce qu'il faut les inclure
dans les commandes?



Réponse #16
------------

Il s’agit d’invites de commande standards. Les invites de commande sont
le préfixe de ligne indiquant à un utilisateur qu’il peut entrer une
commande, ou en général qu’une entrée est attendue de sa part. Dans une
console Python, il est courant d’utiliser ``>>>``. En ``bash`` ou
PowerShell, il est courant d’utiliser plutôt ``$`` ou ``#``. Il n’y a
pas de raison autre que la tradition et la cohérence pour l’utilisation
d’invites particuliers. Dans la plupart des cas, ils peuvent aussi être
modifiés par l’utilisateur du terminal.






Question #7: Utiliser l'interpréteur Python 3.14 externe avec Spyder
=====================================================================


.. index::
   single: spyder
   single: python


J'ai réglé l'interpréteur Python de Spyder à Python 3.14, mais
maintenant la console IPython affiche une erreur de type ``ImportError``
à propos d'un module ``spyder-kernels``. Qu'est-ce qui se passe?



Réponse #15
------------

Dans un terminal (donc ``cmd.exe`` sur Windows ou ``Terminal.app`` sur
MacOS), entrez

.. code:: shell

   python3.14 -m pip install spyder-kernels

pour installer le module :mod:``spyder-kernels`` avec votre interpréteur
Python 3.14. Spyder pourra ensuite l’utiliser comme interpréteur.






Question #5: __init__.py bloque l'importation des sous-modules de xphs1903.outils
==================================================================================


.. index::
   single: ipython
   single: venv
   single: spyder


En tentant d'importer ``xphs1903.outils.plot`` ou
``xphs1903.outils.gui`` pour exécuter la fonction ``main()`` dans la
ligne de commande Python. Le problème est arrivé avec l'installation via
``pip`` dans un environnement virtuel, dans la console IPython de Spyder
6.



Réponse #14
------------

Le problème est réglé, la source est inconnue.






Question #6: Où est l'exécutable Python 3.14 sur Windows?
==========================================================


.. index::
   single: spyder
   single: python


Je veux changer l'interpréteur Python dans Spyder, mais je ne trouve pas
où se trouve l'interpréteur Python 3.14 que j'ai installé. Où est-ce que
l'installeur officiel place les exécutables?



Réponse #13
------------

Pour trouver l’exécutable Python 3.14 du système sur Windows, le plus
simple est d’ouvrir l’application IDLE via le menu
:menuselection:``Démarrer``, et entrer

         import sys sys.executable

pour obtenir le chemin vers l’exécutable. C’est utile pour pouvoir
changer l’interpréteur dans Spyder.






Question #10: C'est quoi un «exécutable»?
==========================================


.. index::
   single: lexique


La documentation parle d'«exécutables». Qu'est-ce que c'est?



Réponse #12
------------

Un *exécutable* est un fichier que l'ordinateur saura comment
*exécuter*, càd une série d'instructions pour le processeur, directement
ou indirectement. Les différents types de fichiers suivants sont
généralement considérés comme des exécutables:

#. Le résultat d'une compilation, eg: le programme compilé et transféré
   à la carte Arduino
#. Un script d'un langage reconnu par l'ordinateur et qu'il sait comment
   interprété, eg: un programme Python

--------------

- Pour plus d'explications sur la compilation, je recommande le `livre
  wiki sur le
  C++ <https://fr.wikibooks.org/wiki/Programmation_C%2B%2B/Compilation>`__
- Pour plus d'explications sur l'interprétation, je recommande le `livre
  wiki sur
  Python <https://fr.wikibooks.org/wiki/Programmation_Python/Avant-propos#Langage_machine,_langage_de_programmation>`__






Question #11: Spyder et tkinter figent?
========================================


.. index::
   single: gui
   single: tkinter
   single: spyder


En essayant d'exécuter la fonction ``main`` de ``xphs1903.outils.plot``
et ``xphs1903.outils.gui``, Spyder semblait particulièrement lent.
Est-ce qu'il y a un problème avec les différentes boucles d'exécution?






Question #1: Erreur dans le téléchargement d'un programme Arduino
==================================================================


.. index::
   single: arduino-ide
   single: avrdude
   single: arduino


Au téléchargement d'un programme sur la carte Arduino Nano Every, il y a
ce message d'erreur que je ne comprends pas:

.. code:: text

   avrdude: jtagmkII_initialize(): Cannot locate "flash" and "boot" memories in description
   avrdude: jtagmkII_reset(): timeout/error communicating with programmer (status -1)
   avrdude: initialization failed, rc=-1
            Double check connections and try again, or use -F to override
            this check.
    
   avrdude: jtagmkII_close(): timeout/error communicating with programmer (status -1)
   avrdude: jtagmkII_close(): timeout/error communicating with programmer (status -1)
   Failed uploading: uploading error: exit status 1







