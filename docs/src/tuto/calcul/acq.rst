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
