#ifndef XPHS1903_CHRONO
#define XPHS1903_CHRONO 1

#include <Arduino.h>

namespace phs
{

class Chrono : public Printable
{
public:
  uint32_t _delai;
  uint32_t _etampe;
  Chrono ();
  Chrono (uint32_t delai);
  void setup ();
  bool loop ();
  virtual size_t
  printTo (Print &p) const
  {
    size_t n = p.print ("t:");
    n += p.print (millis ());
    return n;
  }
};

}
#endif
