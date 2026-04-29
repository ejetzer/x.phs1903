#include "journal.h"

using namespace phs;

void
Journal::entrer (char *msg, Niveau_t niveau)
{
  Serial.print (niveau);
  Serial.print ("::");
  Serial.print (millis ());
  Serial.print ("::");
  Serial.println (msg);
}

void
Journal::debug (char *msg)
{
  entrer (msg, DEBUG);
}

void
Journal::info (char *msg)
{
  entrer (msg, INFO);
}

void
Journal::warn (char *msg)
{
  entrer (msg, WARNING);
}

void
Journal::error (char *msg)
{
  entrer (msg, ERROR);
}

void
Journal::crit (char *msg)
{
  entrer (msg, CRITICAL);
}
