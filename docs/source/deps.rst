.. _deps:

===============
 Dépendances 
===============

Plusieurs modules doivent être installés pour que le programme fonctionne
correctement. Ces modules peuvent être installés via :python:pip,
:pipenv:, :external+conda: ou parfois directement dans votre IDE. Les différents modules à installer sont
listés dans un fichier requirements.txt, mais je vous les indique ici avec
des liens:

- :serial: pour la communication série avec l'Arduino
- :numpy: pour l'analyse numérique
- :scipy: aussi pour l'analyse numérique
- :matplotlib: pour l'affichage des données et résultats d'analyse

.. _stdimports:

-------------------------------------------
 Dépendances de la bibliothèque standard 
-------------------------------------------

- :external+python:module:logging facilite le traçage et la détection d'erreurs
- :external+python:module:time permer de tenir compte du temps.
    En particulier, de mesurer le nombre de ns depuis le début
    de l'exécution du programme.
    
