===================================
 Installation
===================================

Outils officiels
--------------------

Dans le cadre du cours PHS1903, vous devez installer:

#. L'éditeur Spyder_
#. L'interpréteur `Python 3.14`_
#. L'`environnement de développement Arduino`_

.. _Spyder: https://www.spyder-ide.org/download

.. _`Python 3.14`: https://www.python.org/downloads/

.. _`environnement de développement Arduino`: https://www.arduino.cc/en/software/#ide

.. warning::

  Seuls les outils explicitement recommendés dans cette documentation et le
  matériel du cours sont assurés d'être supportés par les techniciens du cours.
  Si vous choisissez des outils différents, il est possible que les techniciens
  priorisent la résolution de problèmes de d'autres équipes utilisant les
  méthodes recommandées.

Ces outils sont ceux qui sont *officiellement supportés* par l'équipe
technique dans le cadre du cours. D'autres éditeurs que vous pourriez utiliser,
mais pour lesquels l'équipe du cours ne prendra pas la responsabilité du
débogage sont:

- `VS Code`_ ou la version libre `VS Codium`_
- `Zed`_ ou la version sans contribution de GML, `gram`_

.. _`VS Code`: https://code.visualstudio.com/

.. _`VS Codium`: https://vscodium.com/

.. _`Zed`: https://zed.dev/

.. _`gram`: https://gram-editor.com/

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

   Ce sera utile pour fixer l'interpréteur dans :ref:`Spyder <spyder-sec>` plus tard.

.. seealso::
   `Documentation officielle de Python sur Windows`_

.. _spyder-sec:

Spyder
--------

.. note::

  Cette procédure a été testée pour Spyder 6.1 sur MacOS et Windows
  en juin 2026.

#. Téléchargez l'installeur à partir de `la page de téléchargements de Spyder`_.
#. Lancez l'installeur
#. Acceptez la licence, à moins que vous n'y aillez une objection quelconque.
   Si c'est le cas, vous devrez trouver un autre éditeur.
#. Sélectionnez :guilabel:`Installer pour moi` si vous n'avez pas les droits
   d'administration de votre ordinateur.
#. Acceptez le répertoire d'installation par défaut.
#. Confirmez l'installation en appuyant sur :guilabel:`Installer`.

.. _`la page de téléchargements de Spyder`: https://www.spyder-ide.org/download


IDE Arduino
-------------

.. note::

  Cette procédure a été testée pour l'IDE Arduino 2.3 en juin 2026.

#. Téléchargez l'installeur à partir de `la page de téléchargements d'Arduino`_.
#. Lancez l'installeur
#. Acceptez la licence, à moins que vous n'y aillez une objection quelconque.
   Si c'est le cas, vous devrez trouver un autre éditeur et une chaîne de
   compilation.
#. Sélectionnez :guilabel:`Juste pour moi` si vous n'avez pas les droits
   d'adminstration de votre ordinateur.
#. Acceptez le répertoire d'installation par défaut.
#. Confirmez l'installation en appuyant sur :guilabel:`Installer`.

.. _`la page de téléchargements d'Arduino`: https://www.arduino.cc/en/software/#ide
