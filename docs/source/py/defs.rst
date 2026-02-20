======================================================
  Définitions de constantes et de valeurs par défaut 
======================================================

--------------------------
Les annotations de type
--------------------------

Python permet de préciser le type d'une variable dans le code,
selon la syntaxe ``<nom>: <type> = <valeur>``. Dans les définitions ci-dessous,
vous verrez des définitions de la forme:

.. literalinclude:: ../../../src/auditeur.py
	:language: python
	:lines: 37,45,59

pour définir respectivement des variables de :py:type:`texte <str>`, de :py:type:`nombre entier <int>`, et de
:py:type:`nombre à virgule flottante <float>`. Ces :py:mod:`annotations <annotationlib>` ne sont pas contraignantes.
Vous pouvez en apprendre plus dans la documentation officielle.
:external:py:mod:`typing`.

-------------------------
Constantes
-------------------------

.. autodata:: auditeur.PORT

.. autodata:: auditeur.DEBIT

.. autodata:: auditeur.DELAI

.. autodata:: auditeur.ESPACEMENT

.. autodata:: auditeur.BRUT
	:no-index:

.. autodata:: auditeur.FFT