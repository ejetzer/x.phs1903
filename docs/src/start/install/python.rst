Python
--------

.. Pour installer Python, rendez-vous sur la `page officielle des téléchargements`_
   de Python, et sélectionnez la version appropriée pour votre système
   d'exploitation. Des informations détaillées sur l'installation sont
   disponibles dans la `documentation officielle de Python sur Windows`_.

.. _`page officielle des téléchargements`: https://www.python.org/downloads/latest/python3.14/

.. _`documentation officielle de Python sur Windows`: https://docs.python.org/fr/3.14/using/windows.html

.. note::

   Cette procédure a été testée pour Python 3.14 sur MacOS et Windows en août 2026.

#. Téléchargez l'installeur approprié selon votre système d'exploitation à partir de la
   `page officielle des téléchargements`_ de Python.
#. Lancez l'installeur.
#. Acceptez la licence, à moins que vous n'ayez une objection quelconque.
   Si c'est le cas, vous devrez vous débrouiller avec le langage de programmation
   de votre choix.
#. Sélectionnez :guilabel:`Installer pour moi` si vous n'avez pas les droits
   d'administration de votre ordinateur.
#. Acceptez l'installation par défaut.
#. Confirmez l'installation en appuyant sur :guilabel:`Installer`.
#. Vérifiez l'installation en lançant l'application IDLE.
   Sur Windows, elle se trouve via le menu :guilabel:`Windows`.
   Sur MacOS elle se trouve dans le dossier :file:`/Applications/Python 3.14` ou
   dans le lanceur d'applications («Launchpad»).
#. Dans la console interactive d'IDLE, vous pouvez trouver où se trouve votre
   installation Python en entrant ces commandes:

   >>> import sys
   >>> sys.executable

   Ce sera utile pour fixer l'interpréteur dans :doc:`spyder` plus tard.

.. seealso::
   `Documentation officielle de Python sur Windows`_
