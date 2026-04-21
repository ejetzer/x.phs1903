#include "Cereal.h"

LigneSerie::LigneSerie() {
  
}

void LigneSerie::setup() {
  Serial.begin(_baudrate);
}

void LigneSerie::setup(uint16_t baudrate) {
  _baudrate = baudrate;
  Serial.begin(_baudrate);
}

uint8_t LigneSerie::read() {
  uint8_t res = _entree.front();
  _entree.pop();
  return res;
}

void LigneSerie::write(uint8_t octet) {
  _sortie.push(octet);
}

void LigneSerie::basic_loop() {
  if (Serial.available() > 0) {
    _entree.push(Serial.read());
  } else if (_sortie.size() > 0) {
    Serial.write(_sortie.front());
    _sortie.pop();
  }
}

void LigneSerie::loop() {
  basic_loop();
}

void EchoSerie::loop() {
    this->basic_loop();
    this->write(this->read());
}
