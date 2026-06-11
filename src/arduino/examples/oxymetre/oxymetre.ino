#include <broche.h>
#include <chrono.h>
#include <serie.h>

phs::Broche del_660nm (2);
phs::Broche del_900nm (3);
phs::Broche del_int (13);
phs::BrocheAnalogique pd_660nm (A2);
phs::BrocheAnalogique pd_900nm (A3);
phs::Chrono chrono (10);
phs::LigneSerie serie (115200);

void
setup ()
{
  del_660nm.setup ();
  del_900nm.setup ();
  del_int.setup ();
  pd_660nm.setup ();
  pd_900nm.setup ();
  chrono.setup ();
  serie.setup ();
}

void
loop ()
{
  del_660nm.loop ();
  del_900nm.loop ();
  del_int.loop ();
  pd_660nm.loop ();
  pd_900nm.loop ();
  serie.loop ();

  if (chrono.loop ())
    {
      serie.print (chrono);
      serie.tab ();
      serie.print (pd_660nm);
      serie.tab ();
      serie.print (pd_900nm);
      serie.ln ();

      // Mettre les DEL à jour
      del_int.regler (!del_int.valeur ());
      del_660nm.regler (del_int.valeur ());
      del_900nm.regler (!del_int.valeur ());
    }
}