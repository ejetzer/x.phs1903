#include "chrono.h"

phs::Chrono::Chrono () : _delai (1000), _etampe (0) {}

phs::Chrono::Chrono (uint32_t delai) : _delai (delai), _etampe (0) {}

bool
phs::Chrono::loop ()
{
  if ((millis () - _etampe) > _delai)
    {
      _etampe = millis ();
      return true;
    }
  return false;
}

void
phs::Chrono::setup ()
{
}
