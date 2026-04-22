#include "broche.h"

phs::Broche::Broche() : numero(A1) {}

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