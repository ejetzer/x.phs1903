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
  printTo (Print &p) const
  {
    size_t n = p.print (F("broche_"));
    n += p.print (this->numero);
    n += p.print (F(":"));
    n += p.print (this->valeur ());
    return n;
  }
};

class BrocheAnalogique : public Broche
{
public:
  BrocheAnalogique ();
  BrocheAnalogique (uint8_t numero);
  using Broche::_valeur;
  void loop ();
  using Broche::mode;
  using Broche::numero;
  using Broche::regler;
  uint16_t valeur () const;
  void setup ();
  uint16_t sonde ();
  uint16_t potentiel () const;
  virtual size_t
  printTo (Print &p) const
  {
    size_t n = p.print (F("V_"));
    n += p.print (this->numero);
    n += p.print (F(":"));
    uint16_t pot = this->potentiel ();
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

template <typename T = uint16_t>
class ListeBroche : public Broche
{
public:
  ListeBroche ();
  ListeBroche (uint8_t numero);
  ListeBroche (uint8_t numero, uint16_t size);
  ListeBroche (uint8_t numero, uint16_t size, uint16_t dt);
  using Broche::numero;
  uint16_t size;
  uint16_t curri = 0;
  uint16_t dt = 10;
  std::vector<T> _valeurs;
  void setup ();
  void loop ();
  using Broche::regler;
  T sonde ();
  uint16_t pos (uint16_t);
  uint16_t pos () const;
  uint16_t move ();
  uint16_t move (uint16_t);
  T valeur (uint16_t) const;
  T valeur () const;
  uint16_t potentiel(uint16_t) const;
  uint16_t potentiel () const;
  uint16_t temps (uint16_t) const;
  uint16_t temps () const;
  uint16_t begin () const;
  uint16_t end () const;
  uint16_t next () const;
  bool is_full () const;
  void empty ();
  virtual size_t
  printTo (Print &p) const
  {
    size_t n = p.print ("t_");
    n += p.print (this->numero);
    n += p.print (F(":"));
    uint16_t t = this->temps ();
    n += p.print (t);
    n += p.print (F("\t"));
    n += p.print (F("broche_"));
    n += p.print (this->numero);
    n += p.print (F(":"));
    uint16_t v = this->valeur ();
    n += p.print (v);
    return n;
  }
};

int freeRam();

}

#endif
