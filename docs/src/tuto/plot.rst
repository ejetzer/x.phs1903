Affichage graphique de données en direct
--------------------------------------------

.. warning::

   En date du 28 août cette section n'est pas complète.

.. admonition:: Pré-requis

   Ce tutoriel assume que vous avez complété :doc:`acq` et :doc:`calcul`

Dans ce tutoriel, vous verrez:

#. Comment construire un graphique avec :external+matplotlib:mod:`matplotlib`.
#. Comment afficher le graphique à l'écran;
#. Comment exporter le graphique en image vectorielle ou bitmap.

:mod:`xphs1903.outils.plot` contient différentes classes pour la création de graphiques. Elles ont toutes quelques points en commun, comme la manière de les configurer et de démarrer l'affichage. Nous avons:

* :class:`PyPlotGraphe` pour de simples graphiques interactifs;
* :class:`FichierGraphe` pour garder un fichier à jour;
* :class:`TkGraphe` pour afficher le graphique dans une interface simple.

Méthodes communes
...........................

.. function:: get_formats(key: int | str | None) -> BaseFormat

   Obtiens les objets de configuration de format apliqués aux différents éléments graphiques.

.. function:: add_subplot(which: tuple[int | str], where: tuple[int] = (1, 1, 1)) -> matplotlib.axes.Axes

   Ajoute un graphique à la figure.

Exemples
...........................

PyPlot
,,,,,,,,,,,,,,,,,,,,,,,,,,,

.. code:: python

   with ArduinoNanoEvery() as com:
       tab = PyPlotGraphe(com)
       tab.register(fft)
       tab.add_subplot("fft", (1, 2, 2))
       tab.add_subplot(0, (1, 2, 1))

       with tab:
           tab.show()

Fichier
,,,,,,,,,,,,,,,,,,,,,,,,,,,

.. code:: python

   from xphs1903.outils.serial import ArduinoNanoEvery
   from xphs1903.outils.plot import TkGraphe

   with ArduinoNanoEvery() as com:
       tab = FichierGraphe(com)
       tab.register(fft)
       tab.add_subplot(0, (1, 2, 1))
       tab.add_subplot("fft", (1, 2, 2))

       with tab:
           tab.wait()

TkGraphe
,,,,,,,,,,,,,,,,,,,,,,,,,,,

.. code:: python

   import tkinter as tk
   from xphs1903.outils.serial import ArduinoNanoEvery
   from xphs1903.outils.plot import TkGraphe

   root = tk.Tk()
   with ArduinoNanoEvery() as com:
       tab = TkGraphe(com, root=root)
       tab.register(fft)
       tab.add_subplot(0, (1, 2, 1))
       tab.add_subplot("fft", (1, 2, 2))
       tab.show()
       tab.toolbar.grid(column=0, row=1, sticky=tk.W + tk.E)

       with tab:
           root.mainloop()
