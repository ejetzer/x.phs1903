#include <serie.h>
#include <broche.h>
#include <chrono.h>

phs::LigneSerie com (115200);
phs::ListeBroche<uint16_t> acq_1 (A0, 625); // 625 * 2 * 2 o = 2.5 ko
phs::ListeBroche<uint16_t> acq_2 (A1, 625); // 625 * 2 * 2 o = 2.5 ko
// 2.5 ko * 2 = 5 ko, limite 6 ko.
phs::Broche del_1 (10);
phs::Broche del_2 (11);
phs::Chrono mesure (4); // 4 ms * 2 * 625 = 5 s

bool groupe = false;
// Indicateur de quelle mesure on prend
// false -> acq_1, del_1; true -> acq_2, del_2

void setup ()
{
  com.setup();
  acq_1.setup();
  acq_2.setup();
  del_1.setup();
  del_2.setup();
  mesure.setup();
}

void loop ()
{
  com.loop ();
  del_1.loop ();
  del_2.loop ();

  if ( mesure.loop () )
  {
    if ( groupe )
    {
      acq_2.loop ();
      del_1.regler (LOW);
      del_2.regler (HIGH);
    }
    else
    {
      acq_1.loop ();
      del_1.regler (HIGH);
      del_2.regler (LOW);
    }
    groupe = !groupe;
  }

  if ( acq_1.is_full () && acq_2.is_full () )
  {
    for ( uint16_t i = acq_1.begin (); i < acq_1.end (); i++ )
    {
      acq_1.pos (i);
      acq_2.pos (i);
      com.print (acq_1);
      com.tab ();
      com.println (acq_2);
    }
    acq_1.empty();
    acq_2.empty();
  }
}
