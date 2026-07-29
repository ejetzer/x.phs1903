Premiers pas avec la communication série
---------------------------------------------

.. warning::

   Lisez :doc:`/start/arduino/blink` avant ceci.

#. Assurez vous d'avoir correctement installé le module :mod:`!xphs1903`,
   voir :doc:`/start/arduino/blink`.
#. Dans la barre de menu, sélectionnez
   :menuselection:`Fichier --> Exemples --> xphs1903 --> phsecho`.
#. Appuyez sur le bouton :guilabel:`Vérifier`.

   Si le module :mod:`!xphs1903` est bien installé, aucun message d'erreur
   ne devait apparaître.

#. Assurez vous que la carte Arduino est bien connectée à l'ordinateur.
#. Assurez vous que la carte Arduino est bien sélectionnée dans l'IDE
   Arduino.
#. Téléchargez le programme.
#. Ouvrez le terminal série de l'IDE Arduino.
#. Assurez vous que le débit attendu par le terminal série est le même
   qu'attendu par le programme Arduino.
#. Vérifiez que l'IDE Arduino envoie un caractère de fin de ligne avec
   chaque commande.
#. Entrez quelques lettres dans la ligne de commande et appuyez sur
   :kbd:`<Enter>`.

Les caractères que vous avez entrés devraient apparaître dans le terminal
après avoir été renvoyés par la carte Arduino. Félicitations!

Les détails
................

Si tout se passe bien, le code que vous voyiez dans l'éditeur après
avoir chargé l'exemple
:download:`phsecho <../../../../src/arduino/examples/phsecho/phsecho.ino>`
devrait être celui ci:

.. literalinclude:: ../../../../src/arduino/examples/phsecho/phsecho.ino
  :language: C++
  :linenos:

La première ligne indique au compilateur qu'il faut inclure le fichier
:file:`serie.h`, qui contient les définitions pertinentes à la communication
série.

Ensuite nous définissons un objet de type :cpp:class:`!phs::EchoSerie`. C'est
cet objet qui fera le gros du travail pour cet exemple. Comme pour la plupart
des objets du module :mod:`!xphs1903`, les objets de classe
:cpp:class:`!phs::EchoSerie` ont des méthodes :cpp:func:`!loop` et
:cpp:func:`!setup`. Regardons pour commencer :cpp:func:`!setup`.

.. code:: C++

   void
   phs::LigneSerie::setup ()
   {
     Serial.begin (_baudrate);
     while (!Serial)
       ;
   }

Premièrement, notez que la définition ci-dessus est en fait pour la fonction
:cpp:func:`phs::LigneSerie::setup`. :cpp:class:`phs::LigneSerie` est la
classe parente de :cpp:class:`phs::EchoSerie`. Si une fonction n'est pas
explicitement définie par :cpp:class:`phs::EchoSerie`, la définition de
:cpp:class:`phs::LigneSerie` sera utilisée. C'est ce qui se passe ici, comme
les deux classes ont la même méthode d'initialisation. Le corps de la fonction
:cpp:member:`phs::LigneSerie::setup` comporte deux instructions.

.. code:: C++

   Serial.begin (_baudrate);

qui définit le débit de communication (par défaut, 9600 bits/sec), et

.. code:: C++

   while (!Serial)
     ;

qui attend que la communication série soit ouverte et disponible avant de
continuer avec le reste du programme. C'est important pour éviter de tenter
d'envoyer ou de lire des données alors que la ligne série n'est pas
correctement configurée.

Regardons maintenant la définition de :cpp:func:`!loop`.

.. code:: C++

   void
   phs::EchoSerie::loop ()
   {
     this->LigneSerie::loop ();
     if (available ())
       {
         uint8_t res = read ();
         write (res);
       }
   }

Le corps de la fonction comporte deux sections: un appel à la fonction
:cpp:func:`!loop` de la classe parente :cpp:class:`phs::LigneSerie`, et un
bloc conditionnel. L'appel à :cpp:member:`phs::LigneSerie::loop` s'occupe
de la gestion de bas niveau de la ligne série. De l'avoir là vous permet de
n'avoir à penser qu'aux fonctions :cpp:func:`!read` et :cpp:func:`!write`, qui
respectivement retournent ou écrivent un octet à la ligne série.

Dans le bloc conditionnel, on lit un octet, pour immédiatement le réécrire sur
la ligne série: un écho bien typique.
