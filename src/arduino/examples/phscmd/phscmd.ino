#include <broche.h>
#include <chrono.h>
#include <serie.h>

phs::Chrono chrono (1000);
phs::BrocheAnalogique broche (A0);
phs::LigneSerie serie (9600);

void
setup ()
{
  chrono.setup ();
  broche.setup ();
  serie.setup ();
}

void
loop ()
{
  broche.loop ();
  serie.loop ();
  if (chrono.loop () && serie.available())
    {
      String cmd = serie.cmd();
      if ((cmd == "A0") || (cmd == "14")) {
       serie.print("t:");
       serie.print(String(millis()));
       serie.tab();
       serie.println (broche);
      }
    }
}
