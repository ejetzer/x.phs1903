#include "broche.h"

phs::Broche::Broche() : numero(13) mode(OUTPUT) {}

phs::Broche::Broche(uint8_t numero) : numero(numero) mode(OUTPUT) {

}

uint16_t phs::Broche::valeur() {
  return _valeur;
}

uint16_t phs::Broche::sonde() {
  _valeur = digitalRead(numero);
  return valeur();
}

void phs::Broche::setup() {
  pinMode(numero, mode);
  regler(LOW);
}

void phs::Broche::regler(uint8_t val) {
  digitalWrite(numero, val);
}

void phs::Broche::loop() {
  sonde();
}

phs::BrocheAnalogique::BrocheAnalogique() : numero(A0) mode(INPUT_PULLUP) {}

phs::BrocheAnalogique::BrocheAnalogique(uint8_t numero) : numero(numero) mode(INPUT_PULLUP) {}

phs::BrocheAnalogique::BrocheAnalogique(uint8_t numero, uint8_t mode) : numero(numero) mode(mode) {}

phs::BrocheAnalogique::setup() {
  pinMode(numero, mode);
}

uint16_t phs::BrocheAnalogique::sonde() {
  _valeur = analogRead(numero);
  return valeur();
}

uint32_t phs::BrocheAnalogique::potentiel() {
  uint32_t res = (ufloat32_t)(5000 * valeur());
  res /= 1024;
  return res;
}