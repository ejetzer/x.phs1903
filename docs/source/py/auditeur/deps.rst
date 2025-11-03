.. _deps:

===============
 Dépendances 
===============

Plusieurs modules doivent être installés pour que le programme fonctionne
correctement. Ces modules peuvent être installés via `pip`_,
`pipenv`_, `conda`_ ou parfois directement dans votre IDE. Les différents
modules à installer sont listés dans un fichier
:download:`requirements.txt <../../../requirements.txt>` ou
:download:`Pipfile <../../../Pipfile>`, mais je
vous les indique ici avec des liens:

- :external:py:class:`serial <serial.Serial>` pour la communication série avec l'Arduino
- :external:py:mod:`numpy` pour l'analyse numérique
- :external:py:mod:`scipy` aussi pour l'analyse numérique
- :external:py:mod:`matplotlib` pour l'affichage des données et résultats d'analyse


.. _pip:
	https://pip.pypa.io/en/stable/


.. _pipenv:
	https://pipenv.pypa.io/en/latest/


.. _conda:
	https://docs.conda.io/projects/conda/en/stable/


.. _stdimports:

-------------------------------------------
 Dépendances de la bibliothèque standard 
-------------------------------------------

- :external:py:mod:`logging` facilite le traçage et la détection d'erreurs
- :external:py:mod:`time` permer de tenir compte du temps.
    En particulier, de mesurer le nombre de ns depuis le début
    de l'exécution du programme.
    
