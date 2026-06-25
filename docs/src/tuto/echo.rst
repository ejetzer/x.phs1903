Écho
------

Un programme simple pour tester les fonctionalités d'une ligne de
communication est l'écho, ou ``loopback``. Il s'agit d'un programme qui
ne fait que répéter ce qu'il reçoit. Plusieurs versions sont expliquées ici.

Écho sur Arduino avec la librairie ``x.phs1903``
...................................................

.. literalinclude:: ../../../src/arduino/examples/phsecho/phsecho.ino
  :language: cpp

Pour exécuter cet exemple, compilez le dans l'environnement Arduino et
téléchargez le sur un Arduino Nano Every. Ouvrez le terminal série, et
admirez comment chaque caractère envoyé via la ligne série vous est retourné
tel quel.

Écho en ligne de commande avec la bibliothèque standard de Python
........................................................................


Écho en ligne de commande entre Arduino et Python
......................................................


