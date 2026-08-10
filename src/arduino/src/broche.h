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
#include <vector>

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
public:
  BrocheAnalogique ();
  BrocheAnalogique (uint8_t numero);
  using Broche::_valeur;
  using Broche::loop;
  using Broche::mode;
  using Broche::numero;
  using Broche::regler;
  using Broche::valeur;
  void setup ();
  uint16_t sonde ();
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
public:
  using Broche::_valeur;
  using Broche::loop;
  using Broche::mode;
  using Broche::numero;
  using Broche::setup;
  using Broche::sonde;
  using Broche::valeur;
  void regler (uint8_t val);
};

class ListeBroche : public Broche
{
public:
  ListeBroche ();
  ListeBroche (uint8_t numero);
  ListeBroche (uint8_t numero, uint8_t size);
  using Broche::numero;
  uint8_t size;
  uint8_t curri = 0;
  std::vector<uint16_t> _temps;
  std::vector<uint16_t> _valeurs;
  void setup ();
  void loop ();
  using Broche::regler;
  uint16_t sonde ();
  uint8_t pos (uint8_t);
  uint8_t pos () const;
  uint8_t move ();
  uint8_t move (uint8_t);
  uint16_t valeur (uint8_t) const;
  uint16_t valeur () const;
  uint16_t temps (uint8_t) const;
  uint16_t temps () const;
  uint8_t begin () const;
  uint8_t end () const;
  uint8_t next () const;
  bool is_full () const;
  void empty ();
  virtual size_t
  phs::ListeBroche::printTo (Print &p) const
  {
    size_t n = p.print ("t_");
    n += p.print (this->numero);
    n += p.print (':');
    uint16_t t = this->temps ();
    n += p.print (t);
    n += p.print ('\t');
    n += p.print ("broche_");
    n += p.print (this->numero);
    n += p.print (':');
    uint16_t v = this->valeur ();
    n += p.print (v);
    return n;
  }
};

}

#endif
