Transmettre des données structurées
.....................................

.. admonition:: Sujets couverts

   #. Transmettre un tableau rangée par rangée
   #. Lire un tableau dans un :class:`~pandas.DataFrame`.
   #. Exécuter des calculs sur les données reçues.

#. Dans un projet vierge, créez les fichiers :file:`tuto_serialdata.py` et :file:`tuto_seriadata/tuto_serialdata.ino`.
#. En vous basant sur :doc:`/tuto/acq/tabfill`, créez un programme dans :file:`tuto_serialdata.ino` pour envoyer
   les mesures des broches ``A0`` et ``A1`` à la ligne série. Référez vous à :doc:`/tuto/calcul/acq` pour appliquer
   ces contraintes:

   #. La fréquence d'échantillonage devrait être de 500Hz.
   #. Les mesures devraient être prises sur 2s.

#. Dans :file:`tuto_serialdata.py`, importez :class:`ArduinoNanoEvery` du sous-module :mod:`xphs1903.outils.serial` et
   initialisez le. Assurez vouss que le débit de communication entre le programme Arduino et le programme Python
   correspondent.

   .. code:: python

      from xphs1903.outils.serial import ArduinoNanoEvery

      with ArduinoNanoEvery(baudrate=115200) as ard:
          pass

#. Importez :class:`TableauCalcul` du sous-module :mod:`xphs1903.outils.calcul` et
   et initialisez le:

   .. code:: python

      from xphs1903.outils.serial import ArduiNanoEvery
      from xphs1903.outils.calcul import TableauCalcul

      with ArduinoNanoEvery(baudrate=115200) as ard:
          tab = TableauCalcul(ard)

#. Définissez une fonction pour calculer la moyenne des 2 dernières secondes de données reçues. La fonction doit avoir
   la signature

   .. py:function:: f(df: pandas.DataFrame, executor=None, logger=None) -> pandas.DataFrame

   Notez que le :class:`pandas.DataFrame` devrait avoir les colonnes ``t_0``, ``A0``, ``t_1``, ``A1``.

   .. list-table:: df
      :header-rows: 1

      * - ``t_0``
        - ``A0``
        - ``t_1``
        - ``A1``
      * - ...
        - ...
        - ...
        - ...

   .. hint::

      Vous pouvez sélectionner les colonnes avec l'indexeur :obj:`pandas.DataFrame.iloc`, comme ceci:

      .. code:: python

         df.iloc[:, 0]  # Tous les éléments de la première colonne.
         df.iloc[-100:,0]  # Les 100 derniers éléments de la première colonne.

   .. hint::

      Vous pouvez calculer la moyenne d'une colonne avec la méthode :obj:`pandas.DataFrame.mean`.

   .. admonition:: Réponse
      :collapsible: closed

      .. code:: python

         def f(df, executor=None, logger=None):
             return df.iloc[-2000:,:].mean()

#. Enregistrez la fonction dans :data:`tab`:

   .. code:: python

      tab.register(f)

#. Ajoutez une boucle avec une condition pour afficher les résultats du calcul à chaque fois que vous appuyez sur
   :kdb:`<enter>`:

   .. code:: python

      with tab:
          while True:
              input('<enter>')
              print(tab['f'])

#. Exécutez le programme. Utilisez le générateur de fonction pour envoyer différents signaux aux broches
   du Arduino. Que constatez-vous?
#. Importez la fonction :func:`fft` du module :mod:`xphs1903.outils.calcul` et utilisez la à la place de votre
   fonction :func:`f`.

