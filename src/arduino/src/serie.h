#ifndef XPHS1903_SERIE
#define XPHS1903_SERIE 1

#ifndef HAWKMOTH
#include <Arduino.h>
#include <ArduinoSTL.h>
#include <queue>
#endif

namespace phs
{

class LigneSerie
{
public:
  std::queue<uint8_t> _entree;
  std::queue<uint8_t> _sortie;
  uint32_t _baudrate = 9600;
  LigneSerie ();
  LigneSerie (uint32_t baudrate);
  void setup ();
  void loop ();
  uint8_t read ();
  size_t write (uint8_t octet);
  size_t write (wchar_t cara);
  size_t write (char cara);
  uint8_t available ();
  size_t print (String);
  size_t println (String);
  size_t print (const char *);
  size_t println (const char *);
  size_t print (const Printable &);
  size_t println (const Printable &);
  size_t tab ();
  size_t ln ();
};

class EchoSerie : public LigneSerie
{
public:
  void loop ();
};

}

#endif
