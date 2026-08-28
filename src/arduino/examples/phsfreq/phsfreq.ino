#include <broche.h>
#include <serie.h>
#include <chrono.h>

phs::BrocheAnalogique entree(A0);
phs::LigneSerie serie(115200);
phs::Chrono chrono(500);
phs::Chrono mesure(2);
phs::Broche del(13);

uint16_t somme = 0;
float N = 0.0;
uint16_t cycles = 0;
bool etat = false;

void setup() {
  entree.setup();
  serie.setup();
  chrono.setup();
  del.setup();
  mesure.setup();
}

void loop() {
  serie.loop();
  del.loop();

  if (mesure.loop()) {
    entree.loop();
    bool val = entree.potentiel() > 2500;
    del.regler(val);

    if (val && !etat) {
      cycles++;
      etat = true;
    } else if (etat && !val) {
      etat = false;
    }

    somme += entree.potentiel();
    N++;
  }

  if (chrono.loop()) {
    String t = String(millis());
    serie.print("t:");
    serie.print(t);
    serie.tab();
    serie.print(F("cycles:"));
    serie.print(String(cycles));
    serie.tab();
    serie.print("t:");
    serie.print(t);
    serie.tab();
    serie.print("freq:");
    serie.print(String(cycles * 2.0));
    serie.tab();
    serie.print("t:");
    serie.print(t);
    serie.tab();
    serie.print("moy:");
    serie.print(String(somme / N));
    serie.tab();
    serie.print("t:");
    serie.print(t);
    serie.tab();
    serie.print("som:");
    serie.print(String(somme));
    serie.tab();
    serie.print("t:");
    serie.print(t);
    serie.tab();
    serie.print("n:");
    serie.print(String(N));
    serie.ln();
    somme = 0;
    N = 0;
    cycles = 0;
  }
}
