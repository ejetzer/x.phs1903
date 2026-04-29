uint32_t etampe;
uint32_t delai;

void
setup ()
{
  delai = 1000;
  pinMode (13, OUTPUT);
}

void
loop ()
{
  if ((millis () - etampe) > delai)
    {
      digitalWrite (13, !digitalRead (13));
      etampe = millis ();
    }
}