Calculs sur des données en C++
.....................................

.. admonition:: Sujets couverts

   Effectuer des calcul soit

   * à l'acquisition même
   * soit juste avant l'envoi série

   Et ensuite

   * Utiliser le résultat des calculs pour contrôler d'autres broches

#. Créez un nouveau croquis Arduino, titré :file:`calcul.ino`.
#. Importez les modules de contrôle des broches, de chronomètre et de communication série:

   .. code:: C++

      #include <broche.h>
      #include <serie.h>
      #include <chrono.h>

#. Définissez vos objets de base:

   .. code:: C++

      phs::BrocheAnalogique entree(A0); // Broche A0
      phs::LigneSerie serie(9600); // Communication série à 9600baud
      phs::Chrono chrono(100); // Intervalle de 100ms

#. Placez les appels adéquats dans :func:`setup` et :func:`loop`:

   .. code:: C++

      void setup() {
        entree.setup();
        serie.setup();
        chrono.setup();
      }

      void loop() {
        entree.loop();
        serie.loop();

        if (chrono.loop()) {
          // Code à venir ici.
        }
      }

#. Empruntez un générateur de fonction et un oscilloscope dans le local C-537.
#. Ajustez la sortie du générateur de fonction à un signal arbitraire allant de 0 à 5 V.
#. Vérifiez le signal avec l'oscilloscope.
#. Dans votre code Arduino, ajoutez des instructions permettant de vérifier si la valeur du signal
   envoyé à la broche A0 est supérieure à 2.5V:

   .. code:: C++

      if (entree.potentiel() > 2500) {
        // Faire quelque chose.
      }

#. Modifiez votre code pour que la DÉL en broche 13 s'allume quand le signal en A0 est supérieur à 2.5V:

   .. code:: C++

      phs::Broche del(13);
      // ...
      if (entree.potentiel() > 2500) {
        del.regler(1);
      } else {
        del.regler(0);
      }
      // ...

#. Avec l'oscilloscope, mesurez simultanément les broches A0 et 13. Que constatez-vous?

Nous allons maintenant modifier le code pour calculer la fréquence d'un signal sur la broche A0, et
envoyer la mesure de fréquence sur la ligne série.

#. Définissez un nouveau :class:`phs::Chrono` pour pouvoir prendre 500 échantillons par seconde.

   .. code:: C++

      phs::Chrono mesure(2);

#. Créez une nouvelle variable :var:`cycles` et une variable :var:`etat`:

   .. code:: C++

      uint32_t cycles = 0;
      bool etat = false;

#. Modifiez :func:`setup`et :func:`loop` pour qu'à chaque 2ms, une mesure soit prise:

   .. code:: C++

      if (mesure.loop()) {
        entree.loop();
      }

#. Modifiez le bloc conditionnel à :code:`chrono.loop)_` dans :func:`loop` pour calculer le nombre de cycles mesurés
   dans les deux dernières secondes:

   .. code:: C++

      cycles = 0;
      for (uint8_t i = entree.begin(); i < entree.end(); i++) {
        val = entree.valeur();
        if (etat == false && val > 2500) {
          cycles++;
          etat = true;
        } else if (etat == true && val <= 2500) {
          etat = false;
        }
      }

      float freq = (float)cycles / 2.0; // Hz

      serie.print("t:");
      serie.print(millis());
      serie.tab();
      serie.print("f:");
      serie.print(freq);
      serie.ln();

#. Modifiez le programme pour que la diode en broche 13 s'allume pour les fréquences en haut de 100Hz.

   .. code:: C++

      del.regler(freq > 100);

#. Testez le programme avec le générateur de fonction et l'oscilloscope. Pour quelles fréquences est-ce que
   les mesures sont exactes? Pourquoi?

.. admonition:: Question

   Pour quelles fréquences est-ce que les mesures sont exactes? Pourquoi?

.. hint::
   :collapsible: closed

   Pour bien mesurer la fréquence d'un signal, il faut une fréquence d'échantillonage d'au moins le double de celle
   du signal, et plusieurs cycles.

.. seealso::

   `Théorème d'échantillonage <https://fr.wikipedia.org/wiki/Th%C3%A9or%C3%A8me_d%27%C3%A9chantillonnage>`_

.. admonition:: Réponse
   :collapsible: closed

   Vous devriez obtenir des mesures exactes entre 2Hz et 500Hz, avec une perte de précision graduelle près des limites.

