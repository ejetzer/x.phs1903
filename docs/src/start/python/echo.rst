Premier pas avec Spyder
-------------------------

#. Téléchargez le `modèle de projet`_ de la page des `sorties`_, ou:

   #. Créez un dossier de travail (si ce n'est pas déjà fait)
   #. Téléchargez y ce modèle de document de présentation:
      :download:`Lisez-moi.txt <../../../../template/Lisez-moi.txt>`.
   #. Dans le même répertoire, téléchargez ce document de description
      des dépendances:
      :download:`requirements.txt <../../../../template/requirements.txt>`
   #. Dans un sous-répertoire :file:`src/`, téléchargez ce modèle de code Python:
      :download:`main.py <../../../../template/src/main.py>`.

#. Ouvrez Spyder.
#. Sélectionnez :menuselection:`Projects --> New Project...` et créez un
   nouveau projet à partir de votre répertoire de travail.
#. Dans les réglages de Spyder, réglez l'interpréteur Python à
   l'interpréteur Python 3.14 que vous avez installé dans :doc:`../install`.
#. Dans la console IPython de Spyder, entrez les commandes:

   .. code:: python

      >>> import venv
      >>> venv.create('.venv', system_site_packages=True, with_pip=True)

#. Dans les préférences de Spyder, changez l'interpréteur Python pour
   ``.venv/bin/python``.
#. Rechargez la console IPython de Spyder
#. Dans la console IPython, entrez

   .. code:: bash

       $ pip install -r requirements.txt

#. Dans la console IPython, entrez

   .. code:: python

       >>> from xphs1903.demos.echo import echo
       >>> echo()

Vous devriez voir apparaître un invite de commande, qui vous renvoie exactement
le texte que vous tapez quand vous appuyez sur :kbd:`<Enter>`. Bravo!

.. _sorties:

.. _`modèle de projet`:

Les détails
..............

Ce que vous venez de faire dans Spyder est l'exécution de code dans un
environnement virtuel. Les environnements virtuels sont une manière d'isoler
votre code du reste de votre système d'exploitation, pour deux raisons
principales:

* Votre code aura des dépendances spécifiques, et vous voulez vous assurer
  qu'elles soient disponibles.
* La configuration et les bibliothèques installées sur votre ordinateur
  pourrait ne pas être compatibles avec les dépendances de votre code.

L'environnement virtuel est donc un ensemble de variables et de programmes
indiquant à votre code où trouver les bonnes ressources, plutôt que de se
fier aux versions de bibliothèques du système d'exploitation. Spécifiquement,
le module :mod:venv de Python crée un répertoire ``.venv`` contenant un
interpréteur Python et un répertoire de bibliothèques distinct.

.. code:: python

  import venv
  venv.create('.venv', system_site_packages=True, with_pip=True)

Pour utiliser cet environnement dans Spyder, nous devons lui indiquer où se
trouve l'interpréteur propre à l'environnement virtuel. C'est ce que nous
faisons en spécifiant ``.venv/bin/python`` comme chemin dans les réglages
de Spyder. Il faut ensuite installer les modules nécessaires à votre projet.
Il existe plusieurs façons de d'indiquer quels modules installer, mais la
plus accessible est celle du fichier ``requirements.txt``, qui contient une
simple liste des modules et parfois de leur version, lisible par l'outil ``pip``
avec la commande

.. code:: bash

  pip install -r requirements.txt

Au cours de votre projet, si vous avez besoin d'un module qui n'est pas déjà
installé, ajoutez le à ``requirements.txt`` et relancez ``pip``. Le fichier
fournis avec l'exemple contient le module dédié du cours et toutes ses
dépendances listées explicitement.

Une fois l'environnement virtuel activé, on peut y exécuter du code. Dans ce
cas-ci, on importe le module ``xphs1903.demos``, mais pas en entier:
seulement la fonction ``echo``. Ensuite, on l'exécute.

.. code:: python

  from xphs1903.demos.echo import echo
  echo()

Pour plus d'informations sur la syntaxe de base de Python, je vous invite à lire
`A Byte of Python <https://python.swaroopch.com/>`_ (aussi disponible
`en français <https://rgilliotte.gitbook.io/byte-of-python>`_).

