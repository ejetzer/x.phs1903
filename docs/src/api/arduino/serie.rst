Communication série
------------------------------

Le module :file:`serie.h` permet de facilement utiliser la ligne de
communication série de l'Arduino. En pratique, c'est à dire de communiquer avec
l'ordinateur par la connexion USB.

.. sourcecode:: C++
  :name: lst:serie-include
  :caption: Inclusion du module :file:`serie.h`

  #include <serie.h>


.. cpp:class:: phs::LigneSerie

.. cpp:class:: phs::EchoSerie : public phs::LigneSerie

.. cpp:member:: std::queue<uint8_t> phs::LigneSerie::_entree

.. cpp:member:: std::queue<uint8_t> phs::LigneSerie::_sortie

.. cpp:class:: template<T> std::queue

.. cpp:type:: unsigned char uint8_t

.. cpp:member:: uint32_t phs::LigneSerie::_baudrate = 9600

.. cpp:type:: unsigned int uint32_t

.. cpp:function:: void phs::LigneSerie::setup()

.. cpp:function:: void phs::LigneSerie::loop()

.. cpp:function:: void phs::EchoSerie::loop()

.. cpp:function:: uint8_t read()

.. cpp:function:: size_t write(uint8_t octet)

.. cpp:type:: uint8_t size_t

.. cpp:function:: uint8_t phs::LigneSerie::available()

.. cpp:function:: size_t phs::LigneSerie::print (String)

.. cpp:function:: size_t phs::LigneSerie::print (const Printable &)

.. cpp:class:: String

.. cpp:class:: Printable

.. cpp:function:: size_t phs::LigneSerie::tab()

.. cpp:function:: size_t phs::LigneSerie::ln()
