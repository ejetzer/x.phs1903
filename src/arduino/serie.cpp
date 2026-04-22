#include "serie.h"

phs::LigneSerie::LigneSerie() : _baudrate(9600) {
  
}

phs::LigneSerie::LigneSerie(uint32_t baudrate) : _baudrate(baudrate) {
  
}

void phs::LigneSerie::setup() {
  Serial.begin(_baudrate);
}

uint8_t phs::LigneSerie::read() {
  uint8_t res = _entree.front();
  _entree.pop();
  return res;
}

void phs::LigneSerie::write(uint8_t octet) {
  _sortie.push(octet);
}

void phs::LigneSerie::loop() {
  if (Serial.available() > 0) {
    uint8_t res = Serial.read();
    _entree.push(res);
  }
  
  if (_sortie.size() > 0) {
    uint8_t res = _sortie.front();
    _sortie.pop();
    Serial.write(res);
  }
}

bool phs::LigneSerie::available() {
  return ( _entree.size() > 0 );
}

void phs::EchoSerie::loop() {
  this->LigneSerie::loop();
  if (available()) {
    uint8_t res = read();
    write(res);
  }
}
