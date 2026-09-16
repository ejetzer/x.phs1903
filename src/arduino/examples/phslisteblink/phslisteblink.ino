#include <serie.h>
#include <broche.h>
#include <chrono.h>

phs::LigneSerie com (115200);
phs::Broche clignotant (13);
phs::ListeBroche autre_broche (A1);
phs::Chrono chrono_clignotant (1);
phs::Chrono chrono_autre (5000);

void setup ()
{
  com.setup();
  clignotant.setup();
  autre_broche.setup();
  chrono_clignotant.setup();
  chrono_autre.setup();
}

void loop ()
{
  com.loop();
  clignotant.loop();


  if ( chrono_clignotant.loop() )
  {
    int valeur_a1 = autre_broche.valeur();
    clignotant.regler(valeur_a1);
    autre_broche.loop();
  }
  else if ( chrono_autre.loop() )
  {
    for (uint8_t i = autre_broche.begin(); i < autre_broche.end(); i++) {
      autre_broche.pos(i);
      com.println(autre_broche);
    }
  }
}
