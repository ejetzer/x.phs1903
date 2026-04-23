#include <broche.h>
#include <chrono.h>
#include <serie.h>

Chrono chrono(1000);
BrocheAnalogique broche(A0);
LigneSerie serie(9600);

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