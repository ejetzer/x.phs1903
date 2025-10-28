======================================================
  Définitions de constantes et de valeurs par défaut 
======================================================

--------------------------
Les annotations de type
--------------------------

Python permet de préciser le type d'une variable dans le code,
selon la syntaxe ``<nom>: <type> = <valeur>``. Dans les définitions ci-dessous,
vous verrez des définitions de la forme:

.. code-block:: python

    PORT: str = '...'
    DEBIT: int = 0405
    ns2s: float = 0.4235

pour définir respectivement des variables de texte, de nombre entier, et de
nombre à virgule flottante. Ces annotations ne sont pas contraignantes.
Vous pouvez en apprendre plus dans la documentation officielle.
:python:typing.

-------------------------
Constantes
-------------------------

.. autodata:: base.PORT

.. autodata:: base.DEBIT

.. autodata:: base.DELAI

.. autodata:: base.ESPACEMENT

.. autodata:: base.BRUT
	:no-index:

.. autodata:: base.FFT

Facteurs de conversion
---------------------------

.. autodata:: base.ns2s

.. autodata:: base.GHz2Hz
