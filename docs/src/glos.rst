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

    .. seealso::
      `IDLE`_, l'IDE incluse avec l'installation Python standard

      `Spyder`_, l'IDE recommandée pour le cours

      `VS Codium`_

  API
    Application Programming Interface. Une manière restreinte
    d'accéder aux informations et fonctions d'une application.
    Généralement, le terme est utilisé spécifiquement pour
    l'intégration d'une application avec d'autres. Dans le contexte
    du cours, vous utilisez l'API du module :mod:`xphs1903` dans
    l'application d'acquisition et de calcul que vous construisez
    pour votre projet.

    .. seealso::
       :doc:`api`

  module
    Fichier contenant des définitions en C++ ou Python et pouvant être importé dans un projet.
    En C++, c'est l'instruction de pré-processeur ``#include <module>`` qui est utilisée,
    et en Python c'est l'instruction ``import module``. L'IDE Arduino inclue plusieurs
    module et permet d'en installer facilement, et l'installation Python standard
    en inclue une foule.

    .. seealso::
       `Les modules`_ dans `A Byte of Python`_

  éditeur
    Application permettant de modifier le code.

    .. seealso::
       :term:`IDE`

  environnement
  environnement virtuel
    Une description reproduisible des programmes, modules et fichiers accessibles par un projet.
    Généralement géré indirectement par un programme comme venv_ ou pipenv_.
    Les environnements virtuels permettent d'isoler un projet ou une application du
    système d'exploitation et des autres applications. Beaucoup d':term:`IDE` incluent
    la gestion des environnements virtuels pour faciliter le développement.

  ligne de commande
  cli
    La ligne de commande est une manière d'envoyer des instructions à un ordinateur
    avec le clavier, généralement dans un langage de programmation dédié comme ``bash``
    ou PowerShell. En opposition aux interfaces graphiques, ou :term:`GUI`. Les applications
    sont généralement plus simples à développer en ligne de commande à cause du flot
    d'exécution plus simple.

    .. seealso::
      Le manuel de `Bash`_

      Le manuel de `PowerShell`_

  invite de commande
  prompt
    Un invite de commande est un symbole utilisé en début de ligne pour indiquer qu'une
    entrée utilisateur est attendue. Dans l'interpréteur interactif Python_, l'invite
    standard est ``>>>``. En Bash_ ou PowerShell_ et pour d'autres lignes de commandes
    populaires, on retrouve généralement ``$``, ``#`` ou ``>`` comme invite, mais
    il n'y a pas de raison technique pour ce choix.

    .. seealso::
       :term:`Ligne de commande`

  terminal
    Interface en ligne de commande permettant de contrôler l'ordinateur. Windows offre
    ``cmd.exe`` et PowerShell, MacOS offre ``Terminal.app`` et Linux en offre une
    grande variété.

    .. seealso::
       :term:`Ligne de commande`

    .. seealso::
       `iTerm2`_

       `GhosTTY`_

       `Terminator`_

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

    .. seealso::
      `Large Language Models Explained Briefly`_ par 3Blue1Brown

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

    .. seealso::
       `Les fonctions`_ dans `A Byte of Python`_


  méthode
  fonction membre
    Une méthode ou fonction membre est une fonction définie pour une :term:classe.
    Généralement, elles ont un accès privilégié à l'objet à partir duquel elles sont appelées.

    .. seealso::
       :term:`Classe <classe>`

       :term:`Fonction <fonction>`

  classe
    Une classe est analogue à un type de variable (comme :py:class:`int` ou :py:class:`str`).
    Le sens précis peut varier un peu d'un langage de programmation à un autre, mais en C++
    et en Python, il est possible de définir des classes pour faciliter la programmation selon
    certains concepts. Par exemple, dans :mod:`xphs1903.outils.calcul`, on a la classe
    :class:`~xphs1903.outils.calcul.Calcul`, qui permet de décrire et manipuler des calculs
    qu'on veut appliquer à des ensembles de données.

    .. seealso::
       `Programmation orientée objet`_ dans `A Byte of Python`_

       `Classes`_
         Classes en C++.

       `Les classes`_ dans `Programmation C++`_ sur Wikilivres

  type
    En C++, un type décrit la manière dont le programme doit traiter une valeur. Au niveau
    machine, les données sont toutes représentées par des bits groupés par octets. Selon
    l'intention du programmeur, les mêmes bits pourraient devoir être additionner selon une
    méthode ou une autre, selon que le type indiqué est celui d'un nombre comme :py:class:`int`,
    d'un entier non-négatif :c:type:`uint8_t`. L'opération pourrait aussi être
    complètement différente, comme la concaténation plutôt que l'addition, pour une variable
    de type :py:class:`str` ou :cpp:class:`String`.

    .. seealso::
      `Les types`_ en C++

      `Les bases`_ dans `A Byte of Python`_

  objet
    En Python, tout est un objet. C'est à dire que chaque variable ou valeur possède des
    attributs et des méthodes qui sont propres à sa classe ou type.

    En C++, les objets sont des valeurs spéciales crées selon les instructions d'une
    :term:`classe`. Les objets possèdent des :term:`fonctions membres <fonction membre>` et des
    attributs, contrairement aux valeurs et variables de types standards.

    .. seealso::
       :term:`Classe <classe>`

  instance
    En C++, on décrit parfois un :term:`objet` comme étant une instance d'une :term:`classe`.
    Créer un nouvel objet implique l'instanciation de la classe, la création d'une nouvelle
    instance.

    .. seealso::
       :term:`Classe <classe>`

  compilateur
    Un compilateur est un programme pouvant produire un fichier exécutable à partir de
    code source. Par exemple, l'IDE Arduino a un compilateur intégré, qui exécute les
    différentes étapes de compilation pour ensuite téléverser le fichier exécutable
    sur la carte Arduino. Ces étapes sont typiquement:

    #. La pré-compilation, où des instructions à propos de comment compiler le code
       sont interprétées. C'est à cette étape que les instructions :code:`#include`
       sont évaluées.
    #. La compilation en fichier objet, où le code est traduit en langage machine, c'est
       à dire des instructions reconnues directement par le processeur.
    #. L'édition de lien, où les fichiers objets produits par différents fichiers source
       sont assemblés pour produire un fichier exécutable statique.

    .. seealso::
       `Programmation C++`_ sur Wikilivres

  interpréteur
    Un interpréteur est un programme qui lit du code source pour exécuter des commandes
    appropriées, sans auparavant le compiler en code machine comme un :term:`compilateur`
    le ferait. Python et la plupart des lignes de commandes sont interpretés.

    .. seealso::
       `Programmation Python`_ sur Wikilivres

       `Les premiers pas`_ de `A Byte of Python`_

       :term:`Compilateur <compilateur>`

  GUI
  Interface graphique
    Une interface graphique, en opposition avec une :term:`ligne de commande`, permet
    d'afficher graphiquement des informations et contrôles. C'est le type d'interface
    le plus répandu aujourd'hui, et celle à laquelle vous être probablement le plus
    habitué. Du point de vue de la programmation, une interface graphique utilise
    généralement une boucle événementielle, qui vérifie l'état des composants de
    l'interface à chaque itération et appelle les fonctions pertinentes. Dans l'exemple
    ci-dessous, on définit une fonction de rappel qui est appelée par la boucle
    événementielle quand un bouton passe de l'état ``inactif`` à l'état ``appuyé``.

    >>> from tkinter import *
    >>> fenetre = Tk()
    >>> def f():
    ...     print('allo')
    ...
    >>> bouton = Button(fenetre, 'Écrire allo dans la console', command=f)
    >>> bouton.pack()  # Dire au gestionnaire de composants d'afficher le bouton
    >>> fenetre.mainloop()  # Lancer la boucle événementielle

    .. seealso::
       :doc:`tuto/gui`

       :doc:`tuto/plot`

       :term:`Ligne de commande <cli>`

       `Tutoriel Tkinter`_


.. _`Spyder`: https://www.spyder-ide.org/

.. _`VS Codium`: https://vscodium.com/

.. _`gram`: https://gram-editor.com/

.. _venv: https://docs.python.org/3/library/venv.html#module-venv

.. _pipenv: https://pipenv.pypa.io/en/latest/

.. _`Programmation C++`: https://fr.wikibooks.org/wiki/Programmation_C%2B%2B/Compilation

.. _`Classes`: https://cppreference.com/cpp/language/classes

.. _`Programmation Python`: https://fr.wikibooks.org/wiki/Programmation_Python/Avant-propos#Langage_machine,_langage_de_programmation

.. _`Les premiers pas`: https://rgilliotte.gitbook.io/byte-of-python/a-byte-of-python/first_steps

.. _`A Byte of Python`: https://rgilliotte.gitbook.io/byte-of-python/a-byte-of-python/

.. _`Les classes`: https://fr.wikibooks.org/wiki/Programmation_C%2B%2B/Les_classes

.. _`Programmation orientée objet`: https://rgilliotte.gitbook.io/byte-of-python/a-byte-of-python/oop

.. _`Les fonctions`: https://rgilliotte.gitbook.io/byte-of-python/a-byte-of-python/functions

.. _`Les modules`: https://rgilliotte.gitbook.io/byte-of-python/a-byte-of-python/modules

.. _`Large Language Models Explained Briefly`: https://www.3blue1brown.com/lessons/mini-llm/

.. _`Bash`: https://www.gnu.org/software/bash/manual/html_node/index.html

.. _`PowerShell`: https://learn.microsoft.com/en-us/powershell/

.. _`Les types`: https://cppreference.com/c/language/type

.. _`Les bases`: https://rgilliotte.gitbook.io/byte-of-python/a-byte-of-python/basics

.. _`iTerm2`: https://iterm2.com/

.. _`GhosTTY`: https://ghostty.org/

.. _`Terminator`: https://gnome-terminator.org/

.. _`Tutoriel Tkinter`: https://www.pythonguis.com/tkinter-tutorial/

.. _`IDLE`: https://docs.python.org/3/library/idle.html#idle

.. _`Python`: https://www.python.org/
