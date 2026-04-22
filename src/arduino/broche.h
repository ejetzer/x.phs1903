#ifndef XPHS1903_BROCHE
#define XPHS1903_BROCHE 1

#include <Arduino.h>
#include <ArduinoSTL.h>
#include <queue>

namespace phs {

  class Broche {
  public:
    uint8_t numero;
    uint16_t _valeur;
    Broche();
    Broche(uint8_t numero);
    uint16_t valeur();
    uint16_t sonde();
    void setup();
    void loop();
    void regler(uint8_t val);
  };

}

#endif
