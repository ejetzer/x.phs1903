============================
 Démarrage rapide
============================

#. Assurez vous d'avoir installer les outils dans :doc:`install`.
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
#. Sélectionnez :menuselection:`Projects -> New Project...` et créez un nouveau projet
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
