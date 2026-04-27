#include <broche.h>
#include <chrono.h>
#include <serie.h>

phs::Chrono chrono(1000);
phs::BrocheAnalogique broche(A0);
phs::LigneSerie serie(9600);

void setup() {
  chrono.setup();
  broche.setup();
  serie.setup();
}

void loop() {
  broche.loop();
  serie.loop();
  if (chrono.loop()) {
    serie.write(broche.valeur());
  }
}