#define DEBIT 1000000
#define DELAI 2
#define Fr 256
#define N 128
#define N_BROCHES 2
//#define ENTIERS
//#define RAPIDE

#include "cmd.h"

void setup() {
  CANInit();
  afficherInit();
  cmdInit();
  
  #if defined(intFFT_INCLUS)
  hannInit();
  #elif defined(FFT_INCLUS)
  fftInit();
  #endif
}

void loop() {
  acq();
  
  #ifndef CMD_INCLUS
  if (n == 0 && A_n == 0) {
    for (idx_t i=0; i<N_COMMANDES; i++) {
      Serial.print(i);
      Serial.print('\t');
      COMMANDES[i](i%N_BROCHES);
    }

    CANInit();
  }
  #else
  ecouter();
  #endif
}
