Gestion du temps
----------------------------------------

Le module :file:`chrono.h` permet de facilement exécuter des tâches
à intervalle régulier sans bloquer l'exécution du programme.

.. sourcecode:: C++
  :name: lst:chrono-include
  :caption: Inclusion du module :file:`chrono.h`

  #include <chrono.h>

.. cpp:class:: phs::Chrono : public Printable

.. cpp:function:: void phs::Chrono::setup()

.. cpp:function:: bool phs::Chrono::loop()

.. cpp:function:: virtual size_t printTo(Print &p) const
