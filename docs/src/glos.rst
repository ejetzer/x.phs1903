==========================
 Glossaire
==========================

.. glossary::

  IDE
  EDI
    Environnement de développement intégré.
    Spyder_ est un exemple d'un EDI. D'autres EDI populaires sont
    `VS Codium`_ ou `gram`_. Les EDI les plus simples n'incluent
    qu'un éditeur de texte, mais presque tous ont la coloration
    syntaxique et beaucoup ont d'autres capacités intéressantes.
    Spyder permet de facilement exécuter, inspecter et déboguer
    le code Python, par exemple.

  API
    Application Programming Interface. Une manière restreinte
    d'accéder aux informations et fonctions d'une application.
    Généralement, le terme est utilisé spécifiquement pour
    l'intégration d'une application avec d'autres. Dans le contexte
    du cours, vous utilisez l'API du module :mod:`xphs1903` dans
    l'application d'acquisition et de calcul que vous construisez
    pour votre projet.

  module
    Fichier contenant des définitions en C++ ou Python et pouvant être importé dans un projet.
    En C++, c'est l'instruction de pré-processeur ``#include <module>`` qui est utilisée,
    et en Python c'est l'instruction ``import module``. L'IDE Arduino inclue plusieurs
    module et permet d'en installer facilement, et l'installation Python standard
    en inclue une foule.

  éditeur
    Application permettant de modifier le code. Voir :term:IDE.

  environnement
  environnement virtuel
    Une description reproduisible des programmes, modules et fichiers accessibles par un projet.
    Généralement géré indirectement par un programme comme venv_ ou pipenv_.
    Les environnements virtuels permettent d'isoler un projet ou une application du
    système d'exploitation et des autres applications. Beaucoup d':term:IDE incluent
    la gestion des environnements virtuels pour faciliter le développement.

  ligne de commande
  cli
    La ligne de commande est une manière d'envoyer des instructions à un ordinateur
    avec le clavier, généralement dans un langage de programmation dédié comme ``bash``
    ou PowerShell. En opposition aux interfaces graphiques, ou :term:GUI. Les applications
    sont généralement plus simples à développer en ligne de commande à cause du flot
    d'exécution plus simple.

  terminal
    Interface en ligne de commande permettant de contrôler l'ordinateur. Windows offre
    ``cmd.exe`` et PowerShell, MacOS offre ``Terminal.app`` et Linux en offre une
    grande variété.

  Grand Modèle de Langage
  GML
  Large Language Model
  LLM
    Programme élaboré de prédiction de texte, généralement intégrés à des systèmes
    de conversation ou des logiciels d'édition ou conception, dans le but de
    faciliter la création rapide de contenus. De par leur principe de fonctionnement,
    ces programmes demandent une expertise par l'utilisateur du domaine précis de
    l'utilisation. Il est par exemple impossible pour un programmeur néophyte
    d'évaluer la qualité ou la pertinence du code généré par un assistant comme
    Claude ou CoPilot.

  fonction
    Une fonction est un sous-programme pouvant être appelé au moment opportun
    dans un programme plus grand. Généralement, les fonctions sont définies
    au début d'un programme ou dans un module externe, pour être utilisées par la suite.
    Une fonction en C++ ou en Python peut recevoir des arguments, souvent des paramètres
    pour contrôler son exécution ou le sujet sur lequel la fonction agit, et peuvent
    retourner une valeur au programme l'ayant invoquée. Dans l'exemple ci-dessous,
    on définie et appelle la fonction :func:`!f`:

    >>> def f(a, b):
    ...    return a + b
    ...
    >>> f(1, 5)
    6
    >>> f('allo ', 'le monde')
    'allo le monde'



  méthode
  fonction membre
    Une méthode ou fonction membre est une fonction définie pour une :term:classe.
    Généralement, elles ont un accès privilégié à l'objet à partir duquel elles sont appelées.

  classe
    Une classe est analogue à un type de variable (comme :py:class:`int` ou :py:class:`str`).
    Le sens précis peut varier un peu d'un langage de programmation à un autre, mais en C++
    et en Python, il est possible de définir des classes pour faciliter la programmation selon
    certains concepts. Par exemple, dans :mod:`xphs1903.outils.calcul`, on a la classe
    :class:`~xphs1903.outils.calcul.Calcul`, qui permet de décrire et manipuler des calculs
    qu'on veut appliquer à des ensembles de données.

  type
    En C++, un type décrit la manière dont le programme doit traiter une valeur. Au niveau
    machine, les données sont toutes représentées par des bits groupés par octets. Selon
    l'intention du programmeur, les mêmes bits pourraient devoir être additionner selon une
    méthode ou une autre, selon que le type indiqué est celui d'un nombre comme :py:class:`int`,
    d'un entier non-négatif :c:type:`uint8_t`. L'opération pourrait aussi être
    complètement différente, comme la concaténation plutôt que l'addition, pour une variable
    de type :py:class:`str` ou :cpp:class:`String`.

  objet
    ...

  instance
    ...

  compilateur
    ...

  interprèteur
    ...


.. _venv:

.. _pipenv:
