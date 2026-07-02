Premier pas avec l'Arduino Nano Every
---------------------------------------

#. Téléchargez l'archive ``zip`` du module Arduino :mod:`!xphs1903` sur la page
   des `sorties`_.
#. Ouvrez l'IDE Arduino
#. Dans la barre latérale, sélectionnez
   :guilabel:`Gestionnaire de bibliothèques`
#. Cherchez et installez le module :arduinolib:`ArduinoSTL <arduinostl>`.
#. Cherchez et installez le module :arduinolib:`ArduinoFFT <arduinofft>`.
#. Dans la barre de menu, sélectionnez
   :menuselection:`Croquis --> Importer une bibliothèque --> Ajouter la bibliothèque .ZIP...`
#. Sélectionnez l'archive :file:`xphs1903.zip`.

Une fois l'installation terminée,

#. Dans la barre de menu, sélectionnez
   :menuselection:`Fichier --> Exemples --> xphs1903 --> phsblink`
#. Appuyez sur le bouton :guilabel:`Vérifier`.

   Si le module :mod:`!xphs1903` est bien installé, aucun message d'erreur ne
   devrait apparaître.
#. Connectez un Arduino Nano Every à votre ordinateur avec un câble USB.
#. Sélectionnez votre carte Arduino nouvellement apparue dans le menu de
   sélection des cartes dans la barre d'outils de l'IDE Arduino.
#. :guilabel:`Téléchargez` le programme.

Vous devriez voir une diode clignoter sur la carte Arduino. Félicitations!

.. _sorties:

Les détails
.............

Si tout se passe bien, le code que vous voyiez dans l'éditeur après
avoir chargé l'exemple
:download:`phsblink <../../../../src/arduino/examples/phsblink/phsblink.ino>`
devrait être celui ci:

.. literalinclude:: ../../../../src/arduino/examples/phsblink/phsblink.ino
  :language: C++
  :linenos:

Les premières lignes indiquent au compilateur qu'il faut inclure les
définitions contenues dans les fichiers :file:`broche.h` et :file:`chrono.h`.
Ces fichiers font partie du module :mod:`!xphs1903`. et facilitent
respectivement la lecture et le contrôle des broches et la gestion du temps.

Viennent ensuite les définitions des objets :cpp:var:`!clignotant` et
:cpp:var:`!chrono`. Ils sont définis par le constructeur de leur types
respectifs, soit :cpp:class:`phs::Broche` et :cpp:class:`phs::Chrono`. Ces
constructeurs demandent et acceptent certains paramètres, dans ce cas-ci, le
numéro de la broche et le temps minimal entre chaque activation du
chronomètre.

Les deux définitions des fonctions :cpp:func:`!setup` et :cpp:func:`!loop` sont
requises par le compilateur Arduino. :cpp:func:`!setup` est exécutée au
démarrage de la carte, et ensuite :cpp:func:`!loop` est répétée sans arrêt. Pour
simplifier le code, tous les objets du module :mod:`!xphs1903` ont une méthode
:cpp:func:`!setup` à appeler dans la fonction globale :cpp:func:`!setup`, et
de même pour :cpp:func:`!loop`. C'est ce qui est défini dans les dernières
lignes du programme.

Pour résumer, nous demandons à l'Arduino d'inverser l'état de la broche 13 à
chaque 1000 ms.
