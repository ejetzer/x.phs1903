Remplir un tableau
.....................................

.. admonition:: Sujets couverts

   Comment remplir un tableau de données avec des mesures.

   * Comment remplir un tableau de longueur fixe
   * Comment estimer la fréquence d'échantillonage
   * Comment estimer la mémoire disponible et la précision
   * Comment envoyer le contenu du tableau via la ligne série

   Ce tutoriel est basé sur :doc:`/start/arduino/echo`.

Une opération couteuse en temps de processeur sur le Arduino et dans
beaucoup de processeurs est la communication, surtout en série. Si on
transmet l'information à un débit de 1kb/s, on prend 1ms pour envoyer
un caractère. Selon le signal qu'on caractérise, ça peut être dérangeant. Une
méthode pour mitiger l'effet de la communication série sur l'exécution du code
est de n'envoyer des données que périodiquement, par paquet. Par exemple, si on
a besoin d'un échantillon de 100 points sur un intervale de 1s, on peut
utiliser un chronomètre de période 10ms pour l'acquisition dans un tableau
de 100 éléments, et envoyer toutes les valeurs d'un coup avec un
chronomètre de 1s. 100 éléments prenant autour de 10 bits à envoyer, à une
fréquence de communication à 1kb/s, on prend autour de 1s à tout envoyer. On
alterne donc entre 1s d'acquisition et 1s de communication.

Avec le module :mod:`!xphs1903`, la classe C++ correspondante se trouve dans
le fichier :file:`broche.h`, sous le nom :cpp:class:`phs::ListeBroche`.
