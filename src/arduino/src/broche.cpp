#include "broche.h"

phs::Broche::Broche() : numero(13) {}

phs::Broche::Broche(uint8_t numero) : numero(numero) {}

uint16_t phs::Broche::valeur() const {
  return _valeur;
}

uint16_t phs::Broche::sonde() {
  _valeur = digitalRead(numero);
  return valeur();
}

void phs::Broche::setup() {
  pinMode(numero, OUTPUT);
  regler(LOW);
}

void phs::Broche::regler(uint8_t val) {
  digitalWrite(numero, val);
}

void phs::Broche::loop() {
  sonde();
}

phs::BrocheAnalogique::BrocheAnalogique() {
  this->Broche::numero = A0;
}

phs::BrocheAnalogique::BrocheAnalogique(uint8_t numero) {
  this->Broche::numero = numero;
}

void phs::BrocheAnalogique::setup() {
  pinMode(this->Broche::numero, INPUT_PULLUP);
}

uint16_t phs::BrocheAnalogique::sonde() {
  this->Broche::_valeur = analogRead(this->Broche::numero);
  return valeur();
}

uint16_t phs::BrocheAnalogique::potentiel() const {
  uint16_t res = valeur() * 5e6 / 1024;
  return res;
}
