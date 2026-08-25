Premiers pas avec la ligne série avec Python et Arduino
----------------------------------------------------------

.. warning::

   Ce tutoriel assume la complétion de :doc:`/start/arduino/echo` et de :doc:`/start/python/echo`.

Programme Arduino
...........................

#. Dans l'IDE Arduino, sélectionnez :menuselection:`Fichier --> Exemples --> xphs1903 --> phsecho`.
#. Téléversez le programme.
#. Vérifiez que le programme fonctionne bien avec le moniteur série.
#. Fermez le moniteur série pour que le programme Python puisse accéder à la carte Arduino.

Programme Python
...........................

#. Dans la console iPython, entrez

   >>> from xphs1903.outils.serial import ardecho
   >>> ardecho()

#. Vous devriez voir un invite de commande. Entrez du texte et appuyez sur :keyboard:`<enter>`.
   Le texte devrait vous être retourné par votre Arduino.

Les détails
...........................

La définition de la fonction :func:`ardecho` ressemble à ceci:

.. code:: python

   def ardecho():
      with ArduinoNanoEvery(baudrate=9600) as com:
          while True:
              try:
                  com.print(input(">>>"))
                  print(com.next(block=True))
              except KeyboardInterrupt:
                  break

