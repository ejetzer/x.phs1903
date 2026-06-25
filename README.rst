========================================================
 Outils pour le cours PHS1903 de Polytechnique Montréal
========================================================

Ce projet fournit un module Arduino, un module Python et quelques programmes
d'exemples d'utilisation de ces fichiers.

-------------
Utilisation
-------------

Outils
--------

Dans le cadre du cours PHS1903, vous devez installer:

#. L'éditeur Spyder_
#. L'interpréteur `Python 3.14`_
#. L'`environnement de développement Arduino`_

.. _Spyder: https://www.spyder-ide.org/download

.. _`Python 3.14`: https://www.python.org/downloads/

.. _`environnement de développement Arduino`: https://www.arduino.cc/en/software/#ide

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

Pour les étudiants ayant plus d'expérience avec la programmation et la ligne
de commande, ces outils sont aussi *officiellement supportés* mais vous ne
serez pas encouragés à les utiliser:

#. La ligne de commande ``bash`` ou ``zsh``

    #. Via Cygwin_ sur Windows
    #. Ou via votre terminal préféré sur Linux et MacOS

#. Le système de gestion des versions `git`_
#. L'interpréteur `Python 3.14`_
#. L'`environnement de développement Arduino`_ (nous n'encourageons pas
   l'utilisation des outils `arduino-cli` dans le cadre du cours)
#. N'importe quel éditeur de texte avec coloration syntaxique, comme
   `Notepad++`_, `TextMate`_, `vim`_ ou votre préféré.

.. _`Cygwin`: https://cygwin.com/

.. _`git`: https://git-scm.com/

.. _`Notepad++`: https://notepad-plus-plus.org/

.. _`TextMate`: https://macromates.com/

.. _`vim`: https://www.vim.page/

Premiers pas
---------------

#. Assurez vous d'avoir installer les outils décrits plus haut.
#. Téléchargez l'archive zip du module Arduino xphs1903 sur la page
   des `sorties`_.
#. Installez le module Arduino xphs1903.
#. Téléchargez le `modèle de projet`_ de la page des `sorties`_.
#. Extrayez le dossier ``template`` et renommez le en quelque chose
   de plus descriptif.
#. Renommez les différents fichiers nommés ``projets`` avec un nom
   descriptif de votre projet, mais concis, avec seulement des caractères
   alphanumériques.
#. Ouvrez le fichier ``.ino`` dans l'IDE Arduino.
#. Ouvrez Spyder
#. Sélectionnez :menu:`Projects -> New Project...` et créez un nouveau projet
   à partir de votre répertoire anciennement nommé ``template``.
#. Dans les réglages de Spyder, réglez l'interpréteur Python à
   l'interpréteur Python 3.14 que vous avez installé précédemment.
#. Dans la console IPython de Spyder, entrez les commandes:

  .. code:: python

      import venv
      venv.create('venv', system_site_packages=True, with_pip=True)

#. Dans les préférences de Spyder, changez l'interpréteur Python pour
   ``venv/bin/python``.
#. Rechargez la console IPython de Spyder
#. Dans la console IPython, entrez

  .. code:: bash

      pip install -r requirements.txt

#. Complétez les différents `tutoriels`_.

.. _`modèle de projet`: https://github.com/ejetzer/x.phs1903/releases/download/v2/template.zip

.. _`sorties`: https://github.com/ejetzer/x.phs1903/releases

.. _`tutoriels`: https://xphs1903.readthedocs.io/fr/dev/

--------
Support
--------

Contactez un des techniciens du cours:

* Émile Jetzer <emile.jetzer@polymtl.ca>
* Jacques Massicotte <jacques-2.massicotte@polymtl.ca>

Seules les requêtes provenant d'étudiants de la session en cours de PHS1903 ont
l'assurance d'être lues, entendues et prises en compte dans le développement du
module ou la correction de bogues. Ces requêtes doivent être faites par
courriel ou via le groupe MS Teams approprié.

--------------
Documentation
--------------

La documentation complète est hébergée sur `Read The Docs`_.

.. _`Read The Docs`: https://xphs1903.readthedocs.io/fr/dev/

--------
Auteurs
--------

Les techniciens du cours de PHS1903 sont les principaux auteurs de ce module.
Le gros du code est écrit par Émile Jetzer, suivant les conseils de Jacques
Massicotte, la coordination de Camila Rizzi et sous la responsabilité de
Caroline Boudoux et Jérémie Villeneuve.

---------
Licence
---------

Ce projet est sous la licence GNU publique (GPLv3+). Voir `LICENSE.rst`_.

.. _`LICENSE.rst`: LICENSE.rst

----------
Citations
----------

Si vous utilisez ce projet dans un contexte académique, référez vous à `CITATION.cff`_ pour le format à utiliser. Vous pouvez l'importer directement dans Zotero_.

.. _`CITATION.cff`: CITATION.cff

.. _Zotero: https://zotero.org

------------
Références
------------

Accessibles à tous
---------------------------

Une fois que vous êtes à l'aise avec les exemples de code, et que vous
avez lu les différents tutoriels de ce module, je vous invite à consulter
les documentations suivantes pour aller plus loin.

#. SciPy_, pour le calcul scientifique, en particulier les transformées
   de Fourier.
#. NumPy_, pour les calculs plus simples, mais sur de grands ensembles de
   données, comme toute une série de mesures.
#. Matplotlib_, pour l'affichage de vos données.
#. Arduino_, pour de la documentation générale sur l'Arduino.
#. Python_, pour de la documentation générale sur Python.

Lecture avancée
------------------

Ces références sont plus détaillées, plus précises, mais aussi plus arides
et difficiles à comprendre si vous n'êtes pas déjà à l'aise avec le C++ et
la programmation pour micro-contrôleurs. Je vous conseille de venir discuter
avec moi (Émile) avant de vous lancer dans ces lectures, du moins dans le cadre
du cours PHS1903.

#. cppreference_, une référence complète sur le C++
#. ATMEL_, une référence pour les micro-contrôleurs des Arduino Nano Every.

.. _SciPy: https://docs.scipy.org/doc/scipy/

.. _NumPy: https://numpy.org/doc/stable/

.. _Matplotlib: https://matplotlib.org/stable/users/index

.. _Arduino: https://docs.arduino.cc/

.. _Python: https://docs.python.org/3/

.. _cppreference: https://cppreference.com/

.. _ATMEL: https://www.microchip.com/en-us/product/ATMEGA4809

