#define DEL0 10
#define DEL1 11

#define TMES 8
// 4 ms * 2 * 625 = 5 s

#define NMES 625
// 2 o * 4 * 625 = 5 ko; limite 6 ko

uint16_t t_1[NMES];
uint16_t t_2[NMES];
uint16_t acq_1[NMES];
uint16_t acq_2[NMES];
uint16_t idx_1 = 0;
uint16_t idx_2 = 0;
uint16_t t_mes = 0;

bool groupe = false;
// Indicateur de quelle mesure on prend
// false -> acq_1, del_1; true -> acq_2, del_2

void
setup ()
{
  Serial.begin (115200);
  pinMode (A0, INPUT_PULLUP);
  pinMode (A1, INPUT_PULLUP);
  pinMode (DEL0, OUTPUT);
  pinMode (DEL1, OUTPUT);
}

void
loop ()
{
  if ((millis () - t_mes) >= TMES)
    {
      if (groupe)
        {
          acq_2[idx_2] = analogRead (A1);
          t_2[idx_2] = millis ();
          idx_2++;
          digitalWrite (DEL0, LOW);
          digitalWrite (DEL1, HIGH);
        }
      else
        {
          acq_1[idx_1] = analogRead (A0);
          t_1[idx_1] = millis ();
          idx_1++;
          digitalWrite (DEL1, LOW);
          digitalWrite (DEL0, HIGH);
        }
      t_mes = millis ();
      groupe = !groupe;
    }

  if (idx_1 >= NMES && idx_2 >= NMES)
    {
      for (uint16_t i = 0; i < NMES; i++)
        {
          Serial.print ("t0:" + String (t_1[i]) + "\tA0:" + String (acq_1[i]));
          Serial.println ("\tt1:" + String (t_2[i])
                          + "\tA1:" + String (acq_2[i]));
        }
      idx_1 = 0;
      idx_2 = 0;
    }
}
