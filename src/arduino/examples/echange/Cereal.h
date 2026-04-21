#ifndef XPHS1903
#define XPHS1903 1

#include <Arduino.h>
#include <ArduinoSTL.h>
#include <queue>

// #define NBR_ANALOGIQUES 8
// #define NBR_DECLENCHABLES 20
// #define NBR_NUMERIQUES 12
// #define NBR_MODULABLES 5

// const uint8_t ANALOGIQUES[NBR_ANALOGIQUES] = {A0, A1, A2, A3, A4, A5, A6, A7};
// const uint8_t DECLENCHABLES[NBR_DECLENCHABLES] = {A0, A1, A2, A3, A4, A5, A6, A7, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13};
// const uint8_t NUMERIQUES[NBR_NUMERIQUES] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13};
// const uint8_t MODULABLES[NBR_MODULABLES] = {3, 5, 6, 9, 10};

class LigneSerie
{
public:
  std::queue<uint8_t> _entree;
  std::queue<uint8_t> _sortie;
  uint16_t _baudrate = 9600;
  LigneSerie();
  void setup();
  void setup(uint16_t baudrate);
  void basic_loop();
  void loop();
  uint8_t read();
  void write(uint8_t octet);
};

class EchoSerie: public LigneSerie {
public:
  void loop();
};

#endif