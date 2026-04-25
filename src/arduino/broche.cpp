#include "broche.h"

phs::Broche::Broche() : numero(13) {}

phs::Broche::Broche(uint8_t numero) : numero(numero) {

}

uint16_t phs::Broche::valeur() {
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

phs::BrocheAnalogique::BrocheAnalogique() : numero(A0) {}

phs::BrocheAnalogique::setup() {
  pinMode(numero, INPUT_PULLUP);
  regler(0);
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