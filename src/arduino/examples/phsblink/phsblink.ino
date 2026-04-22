#include <chrono.h>
#include <broche.h>
#include <serie.h>

phs::Broche clignotant(13);
phs::Chrono chrono(1000);
phs::LigneSerie serie;

void setup() {
  serie.setup();
  clignotant.setup();
  chrono.setup();
}

void loop() {
  serie.loop();
  clignotant.loop();
  if (chrono.loop()) {
    clignotant.regler(!(clignotant.valeur()));
  }
}