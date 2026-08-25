Recevoir un tableau
.....................................

.. admonition:: Sujets couverts

   Comment lire les valeurs envoyées par le Arduino.

   * Comment remplir un :external+pandas:class:`~pandas.DataFrame`
   * Comment exporter les données en différents formats
   * Comment charger les données au besoin

   Ce tutoriel est basé sur :doc:`/start/python/echo`.

#. Assurez vous d'avoir téléversé le programme de remplissage et d'envoi de tableau sur votre Arduino.
#. Créez un nouveau fichier Python dans votre dossier de projet, nommé :file:`tabsend.py`.
#. Importez la classe de communication série :class:`ArduinoNanoEvery` du sous-module :mod:`xphs1903.outils.serial`:

   .. code:: python

      from xphs1903.outils.serial import ArduinoNanoEvery

#. Importez la classe de tableau d'acquisition :class:`Tableau` du sous-module :mod:`xphs1903.outils.acq`:

   .. code:: python

      from xphs1903.outils.acq import Tableau

#. Utilisez un bloc :py:`with` pour définir vos objets:

   .. code:: python

      with ArduinoNanoEvery as com, Tableau(com) as tab:
          while True:
              print(tab.df)

#. Exécutez le code. Il devrait s'exécuter sans erreurs, mais si vite que vous ne pouvez pas lire l'affichage.
#. Ajoutez une instruction de délai dans votre boucle:

   .. code:: python

      import time

      from xphs1903.outils.serial import ArduinoNanoEvery
      from xphs1903.outils.acq import Tableau

      with ArduinoNanoEvery as com, Tableau(com) as tab:
          while True:
              print(tab.df)
              time.sleep(5)

#. Exécutez le code. Vous devriez maintenant avoir 5 secondes pour lire chaque mise à jour.
#. Pour pouvoir arrêter l'exécution du programme, ajoutez ce code de gestion d'erreurs:

   .. code:: python

      import time

      from xphs1903.outils.serial import ArduinoNanoEvery
      from xphs1903.outils.acq import Tableau

      with ArduinoNanoEvery as com, Tableau(com) as tab:
          while True:
              try:
                  print(tab.df)
                  time.sleep(5)
              except KeyboardInterrupt:
                  break

#. Exécutez le programme. Pendant l'exécution, appuyez sur :kbd:`<control>-C`. Le programme devrait s'arrêter.
#. Pour sauvegarder vos données, ajoutez le code suivant après la boucle :py:`while` mais toujours dans le
   bloc :py:`with`:

   .. code:: python

      tab.df.to_csv('données.csv')

#. Vérifiez que le fichier :file:`données.csv` apparaît bien dans votre répertoire de projet quand vous arrêtez
   l'exécution du programme.
#. Ouvrez le fichier :file:`données.csv` et observez les colonnes. À quoi correspondent-elles?
