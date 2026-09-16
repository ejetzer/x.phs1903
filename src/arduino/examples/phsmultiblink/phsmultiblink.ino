#include <serie.h>
#include <broche.h>
#include <chrono.h>

phs::LigneSerie com (115200);
phs::Broche clignotant (13);
phs::BrocheAnalogique autre_broche (A1);
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
  autre_broche.loop();

  if ( chrono_clignotant.loop() )
  {
    int valeur_a1 = autre_broche.valeur();
    clignotant.regler(valeur_a1);
  }
  else if ( chrono_autre.loop() )
  {
    com.print( chrono_autre );
    com.tab();
    com.print( clignotant );
    com.tab();
    com.println( autre_broche );
  }
}
