#include <chrono.h>
#include <broche.h>

phs::Broche clignotant(13);
phs::Chrono chrono(1000);

void setup() {
  clignotant.setup();
  chrono.setup();
}

void loop() {
  clignotant.loop();
  if (chrono.loop()) {
    clignotant.regler(!(clignotant.valeur()));
  }
}