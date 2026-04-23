#ifndef XPHS1903_SERIE
#define XPHS1903_SERIE 1

#include <Arduino.h>
#include <ArduinoSTL.h>
#include <queue>

// #define NBR_ANALOGIQUES 8
// #define NBR_DECLENCHABLES 20
// #define NBR_NUMERIQUES 12
// #define NBR_MODULABLES 5

namespace phs {

// const uint8_t ANALOGIQUES[NBR_ANALOGIQUES] = {A0, A1, A2, A3, A4, A5, A6, A7};
// const uint8_t DECLENCHABLES[NBR_DECLENCHABLES] = {A0, A1, A2, A3, A4, A5, A6, A7, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13};
// const uint8_t NUMERIQUES[NBR_NUMERIQUES] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13};
// const uint8_t MODULABLES[NBR_MODULABLES] = {3, 5, 6, 9, 10};

class LigneSerie
{
public:
  std::queue<uint8_t> _entree;
  std::queue<uint8_t> _sortie;
  uint32_t _baudrate = 9600;
  LigneSerie();
  LigneSerie(uint32_t baudrate);
  void setup();
  void loop();
  uint8_t read();
  void write(uint8_t octet);
  bool available();
  void print(char*);
  void println(char*);
};

class EchoSerie: public LigneSerie {
public:
  void loop();
};

}

#endif