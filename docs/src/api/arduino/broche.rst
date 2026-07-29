Utilisation des broches du Arduino
----------------------------------------

Le module :file:`broche.h` permet de contrôler et mesurer les broches du
Arduino.

.. sourcecode:: C++
  :name: lst:broche-include
  :caption: Inclusion du module :file:`broche.h`

  #include <broche.h>

.. cpp:class:: phs::Broche : public Printable

.. cpp:class:: phs::BrocheAnalogique : public Broche

.. cpp:class:: phs::ListeBroche : public Broche

.. cpp:member:: uint8_t numero

.. cpp:member:: PinMode mode

.. cpp:function:: phs::Broche::setup()

.. cpp:function:: phs::Broche::loop()

.. cpp:function:: phs::BrocheAnalogique::setup()

.. cpp:function:: phs::BrocheAnalogique::loop()

.. cpp:function:: phs::ListeBroche::setup()

.. cpp:function:: phs::ListeBroche::loop()

.. cpp:function:: virtual size_t phs::Broche::printTo(Print &p) const

.. cpp:function:: virtual size_t phs::BrocheAnalogique::printTo(Print &p) const

.. cpp:function:: virtual size_t phs::ListeBroche::printTo(Print &p) const

.. cpp:class:: Print

.. cpp:function:: uint16_t valeur() const

.. cpp:function:: void regler(uint8_t val)
