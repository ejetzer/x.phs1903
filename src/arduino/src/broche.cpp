#include "broche.h"

phs::Broche::Broche () : numero (13) {}

phs::Broche::Broche (uint8_t numero) : numero (numero) {}

uint16_t
phs::Broche::valeur () const
{
  return this->_valeur;
}

uint16_t
phs::Broche::sonde ()
{
  this->_valeur = digitalRead (this->numero);
  return this->valeur ();
}

void
phs::Broche::setup ()
{
  pinMode (this->numero, OUTPUT);
  this->regler (LOW);
}

void
phs::Broche::regler (uint8_t val)
{
  digitalWrite (this->numero, val);
}

void
phs::Broche::loop ()
{
  this->sonde ();
}

phs::BrocheAnalogique::BrocheAnalogique () { this->Broche::numero = A0; }

phs::BrocheAnalogique::BrocheAnalogique (uint8_t numero)
{
  this->Broche::numero = numero;
}

void
phs::BrocheAnalogique::setup ()
{
  pinMode (this->Broche::numero, INPUT_PULLUP);
}

uint16_t
phs::BrocheAnalogique::sonde ()
{
  this->Broche::_valeur = analogRead (this->Broche::numero);
  return this->Broche::valeur ();
}

uint16_t
phs::BrocheAnalogique::potentiel () const
{
  uint16_t res = this->Broche::valeur () * 5e3 / 1024;
  return res;
}

phs::ListeBroche::ListeBroche ()
{
  this->numero = 13;
  this->size = 100;
}

phs::ListeBroche::ListeBroche (uint8_t numero)
{
  this->numero = numero;
  this->size = 100;
}

phs::ListeBroche::ListeBroche (uint8_t numero, uint8_t size)
{
  this->numero = numero;
  this->size = size;
}

void
phs::ListeBroche::setup ()
{
  this->_valeurs.resize (this->size);
  this->_temps.resize (this->size);
  this->begin ();

  pinMode (this->numero, INPUT_PULLUP);
  this->regler (LOW);
}

void
phs::ListeBroche::loop ()
{
  this->sonde ();
  this->move ();
}

uint16_t
phs::ListeBroche::sonde ()
{
  uint8_t i = this->pos ();
  uint16_t v = analogRead (this->numero);
  uint16_t t = millis ();
  this->_temps[i] = t;
  this->_valeurs[i] = v;
  return this->valeur ();
}

uint8_t
phs::ListeBroche::pos () const
{
  return this->curri;
}

uint8_t
phs::ListeBroche::pos (uint8_t i)
{
  this->curri = i;
  this->curri %= this->size;
  return this->curri;
}

uint8_t
phs::ListeBroche::move ()
{
  this->pos (this->next ());
  return this->pos ();
}

uint8_t
phs::ListeBroche::move (uint8_t n)
{
  uint8_t i = this->pos ();
  this->pos (i + n);
  return this->pos ();
}

uint16_t
phs::ListeBroche::valeur () const
{
  uint8_t i = this->pos ();
  uint16_t v = this->_valeurs[i];
  return v;
}

uint16_t
phs::ListeBroche::valeur (uint8_t i) const
{
  uint16_t v = this->_valeurs[i];
  return v;
}

uint16_t
phs::ListeBroche::temps () const
{
  uint8_t i = this->pos ();
  uint16_t v = this->_temps[i];
  return v;
}

uint16_t
phs::ListeBroche::temps (uint8_t i) const
{
  uint16_t v = this->_temps[i];
  return v;
}

uint8_t
phs::ListeBroche::begin () const
{
  return 0;
}

uint8_t
phs::ListeBroche::end () const
{
  return this->size - 1;
}

uint8_t
phs::ListeBroche::next () const
{
  return this->pos () + 1;
}

bool
phs::ListeBroche::is_full () const
{
  if (this->next () == this->end ())
    {
      return true;
    }
  else
    {
      return false;
    }
}

void
phs::ListeBroche::empty ()
{
  this->pos (this->begin ());
}
