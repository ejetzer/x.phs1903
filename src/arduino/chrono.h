#ifndef XPHS1903_CHRONO
#define XPHS1903_CHRONO 1

#include <Arduino.h>

namespace phs {

  class Chrono {
  public:
    uint32_t _etampe;
    uint32_t _delai;
    Chrono();
    Chrono(uint32_t delai);
    void setup();
    bool loop();
  };

}
#endif