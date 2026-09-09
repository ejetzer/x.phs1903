Trouver l'interpréteur Python sur Windows
--------------------------------------------

Sur Windows, l'installation de Python se fait généralement dans le répertoire :file:`AppData` de l'utilisateur
ou du système. Ce dossier est normalement caché. Il faut donc entrer le chemin manuellement dans la barre de
navigation du sélecteur de fichier de Spyder. Dans IDLE, tapez

>>> import sys
>>> print(sys.executable)

puis copiez le résultat pour l'insérer tel quel dans le champ d'entrée d'interpréteur Python.
