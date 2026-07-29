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
le fichier :file:`broche.h`, sous le nom :cpp:class:`phs::ListeBroche`. Cette
classe permet de stocker en mémoire un nombre pré-déterminé de valeurs avec
le moment de la mesure, pour pouvoir les envoyer d'un coup quand le tableau
est plein.

Pour l'utiliser, commencez par importer le module :file:`broche.h`.

.. sourcecode:: C++
  :name: lst:incl-broche

  #include <broche.h>

Ensuite, déclarez un objet de type :cpp:class:`phs::ListeBroche`. Le
constructeur prend en arguments la broche à mesurer et le nombre
d'échantillons à garder en mémoire.

.. sourcecode:: C++
  :name: lst:decl-listebroche

  phs::ListeBroche broche (A0, 100);

Comme pour les autres objets du module :mod:`!xphs1903`, il faut invoquer les
fonctions :c:func:`setup` et :c:func:`loop` aux bons endroits.

.. sourcecode:: C++
  :name: lst:setup-loop-listebroche
  :emphasize-lines: 2,6

  void setup() {
    broche.setup();
  }

  void loop() {
    broche.loop();
  }

Programmée de cette façon, la valeur de la broche est stockée à chaque itération
de :c:func:`loop`. Je vous recommande de plutôt temporiser vos mesures pour
avoir une fréquence d'échantillonage prévisible et ajustable. Pour ça il
faut utiliser le module :file:`chrono.h`.

.. sourcecode:: C++
  :name: lst:chrono-listebroche
  :emphasize-lines: 2,5,9,13-15

  #include <broche.h>
  #include <chrono.h>

  phs::ListeBroche broche (A0, 100);
  phs::Chrono chrono (5);

  void setup() {
    broche.setup();
    chrono.setup();
  }

  void loop() {
    if (chrono.loop()) {
      broche.loop();
    }
  }

La classe :cpp:class:`phs::ListeBroche` fournit aussi une fonction
:c:func:`is_full` qui permet de tester si la liste est tout juste pleine.
Elle s'insère comme suit dans le programme:

.. sourcecode: C++
  :name: lst:is-full
  :emphasize-lines: 5-7

  void loop() {
    if (chrono.loop()) {
      broche.loop();
    }
    if (broche.is_full()) {
      // Faire quelque chose...
    }
  }

On peut faire des calculs avec les valeurs en mémoire, ou les envoyer sur la
ligne série. Dans tous les cas, il faudra itérer sur la liste en entier. C'est
malheureusement plus compliqué que pour une seule valeur, mais ça peut valoir
la peine. Pour itérer donc, on va utiliser une boucle ``for``. L'exemple
:ref:`lst:listebroche-for` assume que vous avez importé :file:`serie.h` et
déclaré un objet :code:`phs::LigneSerie com`.

.. sourcecode:: C++
  :name: lst:listebroche-for
  :caption: Itération sur les valeurs de ``broche``

  if (broche.is_full()) {
    for (uint8_t i = broche.begin(); i < broche.end(); i++) {
      broche.pos(i);
      com.print(broche);
      com.ln();
    }
  }

L'échantillonage
,,,,,,,,,,,,,,,,,,,,,,,,,

Il y a quelques faits importants à garder en tête quand on conçoit un
programme d'acquisition de données. Chaque opération sur le micro-contrôleur
prend un certain temps de processeur, et ça va limiter la fréquence
d'échantillonage.

Sur le Arduino Nano Every, avec le processeur ATMega4809, on a une fréquence
de processeur de 20MHz, ce qui veut dire que l'exécution d'une instruction
de processeur prend environ 50ns. Chaque itération de :c:func:`loop` demandera
certainement plus qu'une instruction, donc on pourrait s'attendre d'un
programme bien optimisé qu'il prenne moins de 1us pour s'exécuter. On peut
vérifier le temps d'exécution avec des variantes de l'exemple :file:`phsblink`
et un oscilloscope.

.. sourcecode:: C++
  :name: lst:blink-timer
  :caption: Programme avec signal de test de temps d'exécution

  #include <broche.h>

  phs::Broche broche (13);

  void setup() {
    broche.setup();
  }

  void loop() {
    broche.loop();
    broche.regler(!broche.valeur());

    // Ce que vous voulez ici.
  }

En branchant un oscilloscope à la broche 13 du Arduino, vous devriez voir une
onde carrée, qui change d'état (haut ou bas) à chaque exécution de la boucle.
Ce changement d'état vous permet d'estimer le temps d'exécution de votre
programme.

Vous ne pourrez pas échantilloner plus vite que votre programme ne
s'exécute. Ajustez donc vos attentes selon ce que vous observez à
l'oscilloscope.

Vous êtes aussi limités par le temps de conversion du signal analogique
en signal numérique. Cette conversion prend normalement autour de 650ns.

L'échantillonage à haute fréquence
''''''''''''''''''''''''''''''''''''''''''

Il est possible d'échantilloner à des fréquences plus élevées avec certaines
contraintes. Si vous pensez en avoir besoin pour votre projet, consultez
Émile Jetzer. Si c'est absolument nécessaire, vous aurez besoin de
structurer votre code différement et pourriez devoir utiliser des fonctions
de plus bas niveau pour optimiser votre programme.
