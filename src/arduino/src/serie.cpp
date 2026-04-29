#include "serie.h"

phs::LigneSerie::LigneSerie () : _baudrate (9600) {}

phs::LigneSerie::LigneSerie (uint32_t baudrate) : _baudrate (baudrate) {}

void
phs::LigneSerie::setup ()
{
  Serial.begin (_baudrate);
  while (!Serial)
    ;
}

uint8_t
phs::LigneSerie::read ()
{
  uint8_t res = _entree.front ();
  _entree.pop ();
  return res;
}

size_t
phs::LigneSerie::write (uint8_t octet)
{
  _sortie.push (octet);
  return sizeof (uint8_t);
}

void
phs::LigneSerie::loop ()
{
  if (Serial.available () > 0)
    {
      uint8_t res = Serial.read ();
      _entree.push (res);
    }

  if (_sortie.size () > 0)
    {
      uint8_t res = _sortie.front ();
      _sortie.pop ();
      Serial.write (res);
    }
}

uint8_t
phs::LigneSerie::available ()
{
  return _entree.size ();
}

size_t
phs::LigneSerie::print (const char *msg)
{
  return Serial.print (msg);
}

size_t
phs::LigneSerie::print (String msg)
{
  return Serial.print (msg);
}

size_t
phs::LigneSerie::print (const Printable &msg)
{
  return Serial.print (msg);
}

size_t
phs::LigneSerie::println (const Printable &msg)
{
  size_t n = print (msg);
  n += Serial.println ();
  return n;
}

size_t
phs::LigneSerie::println (const char *msg)
{
  size_t n = print (msg);
  n += Serial.println ();
  return n;
}

size_t
phs::LigneSerie::println (String msg)
{
  size_t n = print (msg);
  n += Serial.println ();
  return n;
}

size_t
phs::LigneSerie::tab ()
{
  return print ("\t");
}

size_t
phs::LigneSerie::ln ()
{
  return Serial.println ();
}

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
