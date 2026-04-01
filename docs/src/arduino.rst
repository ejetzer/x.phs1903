============================
 Module Arduino
============================

--------------
Installation
--------------

Pour installer ce module dans votre environnement de développement Arduino,
allez dans le menu :menuselection:`Croquis --> Importer une bibliothèque --> Ajouter la bibliothèque .ZIP...`.
Vous pourrez sélectionner le paquet :file:`xphs1903.zip` contenant le module, et il sera installé.
Retournez dans le menu :menuselection:`Croquis --> Importer une bibliothèque --> xphs1903` pour
l'inclure dans un carnet Arduino. 

--------------
Utilisation
--------------

Le module :file:`xphs1903` fournit la fonction :c:func:`set_PF` qui permet de régler la fréquence
d'acquisition du Arduino. Pour un exemple de son utilisation, allez voir :menuselection:`Fichier --> Exemples --> xphs1903 --> annonceur`. Ce programme fonctionne de paire avec :file:`demo.py` qui utilise le module Python.


----------------------------
Implémentation
----------------------------

.. cpp:autodoc:: src/arduino/xphs1903.h

----------------------------
Démonstrations
----------------------------

Annonceur
----------
.. cpp:autodoc:: tests/annonceur/annonceur.ino

Test de fréquences d'acquisition
---------------------------------

.. cpp:autodoc:: tests/freq_adc/freq_adc.ino
