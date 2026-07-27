Plusieurs clignotements
.....................................

.. admonition:: Sujets couverts

   Comment utiliser différentes conditions pour allumer ou éteindre
   des broches analogiques.

   * Différents chronomètres
   * Des chronomètres déphasés
   * L'activation de différentes broches

   Ce tutoriel est basé sur :doc:`/start/arduino/blink`.

La bibliothèque :mod:`!xphs1903` pour Arduino Nano Every fournit le module
:file:`broche.h` pour gérer les broches du Arduino, et le module
:file:`chrono.h` pour gérer le temps sans bloquer la boucle d'exécution
du Arduino. Pour les utiliser, il faut inclure les déclarations

.. sourcecode:: C++
  :name: lst:decl-include
  :caption: Inclusion des modules ``broche.h`` et ``chrono.h``

   #include <broche.h>
   #include <chrono.h>

en tête de votre document ``.ino``. Elles indiquent au compilateur utilisé
par Arduino qu'il faut inclure les déclarations et définitions des fichiers
:file:`broche.h` et :file:`chrono.h` lors de la compilation du code. Ces
définitions incluent deux classes (types d'objets), :cpp:class:`Broche` et
:cpp:class:`Chrono`.

Pour gérer une broche,il faut déclarer une instance de la classe
:cpp:class:`Broche`, entre les déclarations ``#include`` et ``void setup() {``.
Par exemple, le bloc de code qui suit déclare deux objets pour contrôler les
broches ``13`` et ``A1``.

.. sourcecode:: C++
  :name: lst:decl-broches
  :caption: Déclaration des broches à contrôler

  phs::Broche clignotant (13);
  phs::BrocheAnalogique autre_broche (A1);

Les numéros de broches et leurs alias sont disponibles dans la documentation
officielle du :arduinocard:`Arduino Nano Every <nano-every>`, et reproduites
dans le tableau :ref:`tab:broches`.

.. list-table:: Broches du Arduino Nano Every
  :header-rows: 1
  :name: tab:broches

  * - Broche
    - Alias
    - Description
  * - ``2``
    -
    - Broche numérique 2
  * - ``3``
    -
    - Broche numérique 3, capable de PWM
  * - ``4``
    -
    - Broche numérique 4
  * - ``5``
    -
    - Broche numérique 5
  * - ``6``
    -
    - Broche numérique 6, capable de PWM
  * - ``7``
    -
    - Broche numérique 7
  * - ``8``
    -
    - Broche numérique 8
  * - ``9``
    -
    - Broche numérique 9, capable de PWM
  * - ``10``
    -
    - Broche numérique 10, capable de PWM
  * - ``11``
    -
    - Broche numérique 11
  * - ``12``
    -
    - Broche numérique 12
  * - ``13``
    - ``LED_BUILTIN``
    - Broche numérique 13, associée à une DEL intégrée
  * - ``14``
    - ``A0``
    - Broche de lecture analogique 0
  * - ``15``
    - ``A1``
    - Broche de lecture analogique 1
  * - ``16``
    - ``A2``
    - Broche de lecture analogique 2
  * - ``17``
    - ``A3``
    - Broche de lecture analogique 3
  * - ``18``
    - ``A4``
    - Broche de lecture analogique 4
  * - ``19``
    - ``A5``
    - Broche de lecture analogique 5
  * - ``20``
    - ``A6``
    - Broche de lecture analogique 6
  * - ``21``
    - ``A7``
    - Broche de lecture analogique 7

Pour utiliser les objets :cpp:class:`phs::Broche`, il faut ajouter deux instructions
par broche: une dans :c:func:`setup` et une :c:func:`loop`.

.. sourcecode:: C++
  :name: lst:setup-broches
  :caption: Pré-réglage des broches dans ``setup``
  :emphasize-lines: 2,3

  void setup() {
    clignotant.setup ();
    autre_broche.setup ();
  }

.. sourcecode:: C++
  :name: lst:loop-broches
  :caption: Exécution des routines de contrôle et mesure dans ``loop``
  :emphasize-lines: 2,3

  void loop() {
    clignotant.loop();
    autre_broche.loop();
  }

Ces étapes complétées, nous pouvons définir nos chronomètres, soit deux
instances de la classe :cpp:class:`phs::Chrono`, déclarées ainsi:

.. sourcecode:: C++
  :name: lst:decl-chrono
  :caption: Déclaration des chronomètres
  :emphasize-lines: 3,4

  phs::Broche clignotant (13);
  phs::BrocheAnalogique autre_broche (A1);
  phs::Chrono chrono_clignotant (1);
  phs::Chrono chrono_autre (5000);

et nous complétons les fonctions :c:func:`setup` et :c:func:`loop`:

.. sourcecode:: C++
  :name: lst:setup-chrono
  :caption: Pré-réglage des chronomètres dans ``setup``
  :emphasize-lines: 4,5

  void setup() {
    clignotant.setup();
    autre_broche.setup();
    chrono_clignotant.setup();
    chrono_autre.setup();
  }

.. sourcecode:: C++
  :name: lst:loop-chrono
  :caption: Exécution des routines des chronomètres dans ``loop``
  :emphasize-lines: 5-9

  void loop() {
    clignotant.loop();
    autre_broche.loop();

    if ( chrono_clignotant.loop() ) {
      // Code ici...
    } else if ( chrono_autre.loop() ) {
      // Code ici...
    }
  }

Vous remarquerez que le code pour les chronomètres est légèrement plus
complexe que pour les broches. La manière dont les chronomètres (et les
structures équivalentes) fonctionnent sur Arduino est la suivante:

#. Au démarrage, déclarer une variable pour se rappeler du moment de la dernière
   exécution.
#. Déclarer aussi une constante contenant le délai à respecter entre deux
   exécutions.
#. À chaque exécution de la boucle (la fonction :c:func:`loop`),

   #. Vérifier si le délai est atteint ou dépassé. C'est l'instruction
      :code:`if (chrono.loop())`.
   #. Si oui, exécuter le code (bloc conditionnel), sinon passer à l'instruction
      suivante.
   #. Et ainsi de suite pour chaque chronomètre et chaque boucle.

Pour ce tutoriel, nous allons asservir la DEL :c:macro:`LED_BUILTIN` à la valeur mesurée par la broche :c:macro:`A1`. Dans le bloc conditionnel de
:c:var:`chrono_clignotant`, nous allons inclure des instructions pour
obtenir la valeur de :c:var:`autre_broche` et régler la valeur de
:c:var:`chrono_clignotant`.

.. sourcecode:: C++
  :name: lst:read-set-broches
  :caption: Lecture et contrôle des broches dans ``loop``
  :emphasize-lines: 6-7

  void loop() {
    clignotant.loop();
    autre_broche.loop();

    if ( chrono_clignotant.loop() ) {
      int valeur_a1 = autre_broche.valeur();
      clignotant.regler(valeur_a1);
    } else if ( chrono_autre.loop() ) {
      // Code ici...
    }
  }

Le programme entier devrait maintenant de un être compilable, et de deux
s'exécuter correctement. Téléchargez le sur votre carte Arduino. Vous ne
devriez rien voir dans le terminal série, et rien sur la carte. Pour utiliser
le programme:

#. Connectez la sortie d'un générateur de fonction à la broche
   :c:macro:`A1`
#. Connectez le canal 1 d'un oscilloscope à la sortie du générateur de fonction
#. Connectez le canal 2 de l'oscilloscope à la broche :c:macro:`LED_BUILTIN`
#. Sans activer la sortie du générateur, configurez une onde carrée allant de
   0 à 5V, à une fréquence de 100Hz
#. Sur l'oscilloscope, réglez l'étendue des deux canaux pour afficher 2V par
   grande division, et l'axe du temps pour afficher 2.5ms par grande division.
#. Vérifiez vos connexions et réglages avec un technicien.
#. Activez la sortie du générateur de fonction. Plusieurs choses devraient se
   produire:

   #. La diode :c:macro:`LED_BUILTIN` devrait clignoter rapidement
   #. Les deux canaux de l'oscilloscope devraient afficher une forme d'onde
      carrée avec une fréquence de 100Hz.

Pour pouvoir valider l'état des broches, ou vous en servir pour collecter des
données, vous pouvez utiliser le module :file:`serie.h`, qui offre la
classe :cpp:class:`phs::LigneSerie`.

.. sourcecode:: C++
  :name: lst:ajout-serie
  :caption: Ajout de la communication série
  :emphasize-lines: 1,5,12,20,28-32

  #include <serie.h>
  #include <broche.h>
  #include <chrono.h>

  phs::LigneSerie com (115200);
  phs::Broche clignotant (13);
  phs::BrocheAnalogique autre_broche (A1);
  phs::Chrono chrono_clignotant (1);
  phs::Chrono chrono_autre (1);

  void setup() {
    com.setup();
    clignotant.setup();
    autre_broche.setup();
    chrono_clignotant.setup();
    chrono_autre.setup();
  }

  void loop() {
    com.loop();
    clignotant.loop();
    autre_broche.loop();

    if ( chrono_clignotant.loop() ) {
      int valeur_a1 = autre_broche.valeur();
      clignotant.regler(valeur_a1);
    } else if ( chrono_autre.loop() ) {
      com.print( chrono_autre );
      com.tab();
      com.print( clignotant );
      com.tab();
      com.println( autre_broche );
    }
  }

Utilisez le moniteur et le traceur série pour observer différemment les signaux
captés et émis par l'oscilloscope. Variez la fréquence du signal du générateur
de fonction, et les temps de déclenchement des chronomètres, pour voir l'effet
sur :c:macro:`LED_BUILTIN` et la sortie série.

.. admonition:: Utilisation des appareils de mesure

   Dans ce tutoriel nous avons utilisé le générateur de fonction et
   l'oscilloscope pour créer et observer les signaux d'entrée de notre
   Arduino. C'est une bonne pratique pendant votre projet de continuer
   à vous en servir de la sorte.

Pour aller plus loin
,,,,,,,,,,,,,,,,,,,,,,

#. Connectez une DEL à une broche inutilisée, et modifiez le programme pour
   préserver la fonctionnalité existante, mais aussi faire clignoter cette
   nouvelle DEL à une fréquence d'un cinquième du signal reçu en :c:macro:`A1`.
#. Utilisez une autre broche pour mesurer le temps d'exécution de votre
   :c:func:`loop` à l'oscilloscope. Où devriez vous l'activer et la désactiver?
   Quel code devez-vous ajouter?
#. L'Arduino comprend une instruction :c:func:`delay` qui permet d'arrêter
   l'exécution un certain temps. Dans des cas simples, ça peut fonctionner
   à la place des chronomètres. Pourquoi est-ce que ce n'est pas approprié ici?
#. Qu'est-ce qui arrive si la broche :c:macro:`A1` est déclarée avec la classe
   :cpp:class:`phs::Broche` au lieu de :cpp:class:`phs::BrocheAnalogique`?
