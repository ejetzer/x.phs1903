Chaîne de compilation
=============================

La chaîne de compilation du module :mod:`xphs1903` est complexe parce qu'elle intègre trois fils distincts:

#. La compilation en distribution source et en paquet ``wheel`` du module Python
#. La compilation en module compatible avec l'IDE Arduino pour le module Arduino
#. La compilation de la documentation

Dans le casre du cours PHS1903, les trois fils sont tous aussi importants les uns que les autres. Pour les
maintenir à la même version, Émile Jetzer a développé un :file:`Makefile` et quelques scripts Python.

.. toctree::

   make/Makefile.rst
   make/utilities.rst
   make/pipenv.rst
   make/help.rst
   make/arduino.rst
   make/python.rst
   make/docs.rst
   make/tests.rst
   make/template.rst
   make/demos.rst
   make/release.rst
   make/faq.rst
