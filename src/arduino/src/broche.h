#ifndef XPHS1903_BROCHE
#define XPHS1903_BROCHE 1

/**
 * La bibliothèque Arduino et la
 * bibliothèque standard sont nécessaires
 * pour les définitions des classes de
 * manipulation des broches.
 */
#include <Arduino.h>
#include <ArduinoSTL.h>
#include <queue>

namespace phs
{

class Broche : public Printable
{
public:
  uint8_t numero;
  PinMode mode;
  uint16_t _valeur;
  Broche ();
  Broche (uint8_t numero);
  uint16_t valeur () const;
  uint16_t sonde ();
  void setup ();
  void loop ();
  void regler (uint8_t val);
  virtual size_t
  phs::Broche::printTo (Print &p) const
  {
    size_t n = p.print ("broche_");
    n += p.print (numero);
    n += p.print (':');
    n += p.print (valeur ());
    return n;
  }
};

class BrocheAnalogique : public Broche
{
private:
  using Broche::regler;

public:
  BrocheAnalogique ();
  BrocheAnalogique (uint8_t numero);
  void setup ();
  uint16_t sonde ();
  void loop ();
  uint16_t potentiel () const;
  virtual size_t
  phs::BrocheAnalogique::printTo (Print &p) const
  {
    size_t n = p.print ("V_");
    n += p.print (numero);
    n += p.print (':');
    uint16_t pot = potentiel ();
    n += p.print (pot);
    return n;
  }
};

class BrochePWM : public Broche
{
private:
  using Broche::sonde;
  using Broche::valeur;

public:
  void setup ();
  void loop ();
  void regler (uint8_t val);
};

}

#endif
