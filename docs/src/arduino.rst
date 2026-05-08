Module Arduino
============================

--------------
Utilisation
--------------

Le module :file:`xphs1903.h` fournit la fonction :c:func:`set_PF` qui permet de régler la fréquence
d'acquisition du Arduino. Pour un exemple de son utilisation, allez voir :menuselection:`Fichier --> Exemples --> xphs1903 --> phsblink`. Ce programme fonctionne de paire avec :file:`demo.py` qui utilise le module Python.


----------------------------
Implémentation
----------------------------

.. cpp:autodoc:: src/arduino/src/xphs1903.h

.. cpp:autodoc:: src/arduino/src/chrono.h

.. cpp:autodoc:: src/arduino/src/broche.h

.. cpp:autodoc:: src/arduino/src/serie.h

.. cpp:autodoc:: src/arduino/src/hautefrequence.h

