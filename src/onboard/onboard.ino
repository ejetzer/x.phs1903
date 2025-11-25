#define DEBIT 1000000
#define DELAI 2
#define Fr 256
#define N 128
#define N_BROCHES 2
//#define RAPIDE

#include <Arduino.h>
#include "types.h"
#include "adc.h"
//#include "intFFT.h"
#include "fft.h"
#include "afficher.h"
#include "cmd.h"

void setup() {
  CANInit();
  hannInit();
  afficherInit();
  cmdInit();
}

void loop() {
  acq();
  
  if (n == 0 && A_n == 0) {
    for (idx_t i=0; i<N_COMMANDES; i++) {
      COMMANDES[i](i%N_BROCHES);
    }
    enInt();
  }
  
  //ecouter();
}
