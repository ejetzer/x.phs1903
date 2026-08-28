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

void phs::BrocheAnalogique::loop ()
{
  this->BrocheAnalogique::sonde();
}

uint16_t
phs::BrocheAnalogique::valeur () const
{
  return this->Broche::_valeur;
}

uint16_t
phs::BrocheAnalogique::potentiel () const
{
  uint16_t res = this->valeur () * 4.883; // 5.0e3 / 1024
  return res;
}

template<typename T>
phs::ListeBroche<T>::ListeBroche ()
{
  this->numero = 13;
  this->size = 100;
  this->dt = 10;
  this->_valeurs.resize (this->size);
}

template<typename T>
phs::ListeBroche<T>::ListeBroche (uint8_t numero)
{
  this->numero = numero;
  this->size = 100;
  this->dt = 10;
  this->_valeurs.resize (this->size);
}

template<typename T>
phs::ListeBroche<T>::ListeBroche (uint8_t numero, uint16_t size)
{
  this->numero = numero;
  this->size = size;
  this->dt = 10;
  this->_valeurs.resize (this->size);
}

template<typename T>
phs::ListeBroche<T>::ListeBroche(uint8_t numero, uint16_t size, uint16_t dt)
{
  this->numero = numero;
  this->size = size;
  this->dt = dt;
  this->_valeurs.resize (this->size);
}

template<typename T>
void
phs::ListeBroche<T>::setup ()
{
  pinMode (this->numero, INPUT_PULLUP);
  this->regler (LOW);
}

template<typename T>
void
phs::ListeBroche<T>::loop ()
{
  this->sonde ();
  this->move ();
}

template<typename T>
T
phs::ListeBroche<T>::sonde ()
{
  uint16_t i = this->pos ();
  this->_valeurs[i] = analogRead (this->numero);
  return this->valeur ();
}

template<typename T>
uint16_t
phs::ListeBroche<T>::pos () const
{
  return this->curri;
}

template<typename T>
uint16_t
phs::ListeBroche<T>::pos (uint16_t i)
{
  this->curri = i;
  this->curri %= this->size;
  return this->curri;
}

template<typename T>
uint16_t
phs::ListeBroche<T>::move ()
{
  this->pos (this->next ());
  return this->pos ();
}

template<typename T>
uint16_t
phs::ListeBroche<T>::move (uint16_t n)
{
  uint16_t i = this->pos ();
  this->pos (i + n);
  return this->pos ();
}

template<typename T>
T
phs::ListeBroche<T>::valeur () const
{
  uint16_t i = this->pos ();
  T v = this->_valeurs[i];
  return v;
}

template<typename T>
T
phs::ListeBroche<T>::valeur (uint16_t i) const
{
  T v = this->_valeurs[i];
  return v;
}

template<typename T>
uint16_t
phs::ListeBroche<T>::potentiel () const
{
  T val = this->valeur ();
  float pre = 1.0;
  if (sizeof(T) == 1) {
    pre = 4.0;
  }
  uint16_t res = (float)(val) * pre * 4.883; // 5.0e3 / 1024
  return res;
}

template<typename T>
uint16_t
phs::ListeBroche<T>::potentiel (uint16_t n) const
{
  uint16_t res = (float)(this->valeur (n)) * 4.883; // 5.0e3 / 1024
  return res;
}

template<typename T>
uint16_t
phs::ListeBroche<T>::temps () const
{
  uint16_t i = this->pos ();
  uint16_t dt = this->dt;
  uint16_t t = i * dt;
  return t;
}

template<typename T>
uint16_t
phs::ListeBroche<T>::temps (uint16_t i) const
{
  uint16_t dt = this->dt;
  uint16_t t = i * dt;
  return t;
}

template<typename T>
uint16_t
phs::ListeBroche<T>::begin () const
{
  return 0;
}

template<typename T>
uint16_t
phs::ListeBroche<T>::end () const
{
  return this->size - 1;
}

template<typename T>
uint16_t
phs::ListeBroche<T>::next () const
{
  return this->pos () + 1;
}

template<typename T>
bool
phs::ListeBroche<T>::is_full () const
{
  if (this->pos () == this->end ())
    {
      return true;
    }
  else
    {
      return false;
    }
}

template<typename T>
void
phs::ListeBroche<T>::empty ()
{
  this->pos (this->begin ());
}

template class phs::ListeBroche<uint8_t>;
template class phs::ListeBroche<uint16_t>;

// https://docs.arduino.cc/learn/programming/memory-guide/
int freeRam() {
  extern int __heap_start,*__brkval;
  int v;
  return (int)&v - (__brkval == 0
    ? (int)&__heap_start : (int) __brkval);
}
