#include <serie.h>
#include <broche.h>
#include <chrono.h>

phs::LigneSerie serie (115200);
phs::ListeBroche<uint16_t> broche (A0, 200);
phs::ListeBroche<uint8_t> broche2 (A1, 200);
phs::Chrono mesure (10);

void setup() {
  // put your setup code here, to run once:
  serie.setup();
  mesure.setup();
  broche.setup();
  broche2.setup();
}

void loop() {
  // put your main code here, to run repeatedly:
  serie.loop();

  if (mesure.loop()) {
    broche.loop();
    broche2.loop();
  }

  if ( broche.is_full() ) {
    for (uint8_t i = broche.begin(); i < broche.end(); i++) {
      broche.pos(i);
      broche2.pos(i);
      serie.print(broche);
      serie.tab();
      serie.print(broche2);
      serie.ln();
    }
    broche.empty();
    broche2.empty();
  }
}
