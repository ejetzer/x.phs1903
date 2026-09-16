Manipuler des fichiers avec :mod:`pandas`
--------------------------------------------

L'instruction :code:`tab.df.to_csv('données.csv)` exporte des données d'un objet :class:`~pandas.DataFrame` vers
un fichier. La méthode :func:`~pandas.DataFrame.to_csv` et d'autres méthodes semblables permettent cette exportation.
Les fonctions inverses comme :func:`~pandas.DataFrame.read_csv` permettent de charger un fichier dans un objet
:class:`~pandas.DataFrame`. Vous pouvez ensuite le manipuler dans une console ou un script exploratoire pour
éventuellement implémenter des calculs en direct. Pour des détails sur Pandas, voyez le `guide de l'utilisateur`_.

.. _`guide de l'utilisateur`: https://pandas.pydata.org/docs/user_guide/10min.html#min

Un :class:`~pandas.DataFrame` contient des colonnes et des rangées, accessibles via des *locateurs*, soit
:obj:`~pandas.DataFrame.loc` (par références nommées) et :obj:`~pandas.DataFrame.iloc` (par références numériques).
Voici un exemple de script effectuant quelques calculs sur un :class:`~pandas.DataFrame`. Les fonctions utilisées
proviennent de :mod:`pandas` et :mod:`numpy`.

.. code:: python

   import pandas as pd
   import numpy as np

   df = pd.read_csv('données.csv')

   ts = df.iloc[:, 0]  # Tous les items de la première colonne
   xs = df.iloc[:, 1]  # Tous les items de la seconde colonne
   arr = df.iloc[:, [0, 1]]  # Tous les items des deux premières colonnes

   gra = np.gradient(xs, ts)  # Calcul de la première dérivée

   dt = np.mean(ts[1:] - ts[:-1])  # Intervalle moyen entre chaque mesure
   fft = np.fft.rfft(xs)  # Calcul de la transformée de Fourier
   fs = np.fft.rfftfreq(xs.size, dt)  # Calcul des fréquences

   res = pd.DataFrame({'fs': fs, 'fft': fft})  # Conversion en DataFrame

   res.to_csv('calcul.csv')  # Export vers un fichier
