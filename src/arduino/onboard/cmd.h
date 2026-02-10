#ifndef CMD_INCLUS
#define CMD_INCLUS

#include "afficher.h"

#ifndef N_BROCHES
#define N_BROCHES 8
#endif

#ifndef N_COMMANDES
#define N_COMMANDES (3*N_BROCHES)
#endif


void (*COMMANDES[N_COMMANDES]) (idx_t j);

void cmdInit() {
  for (idx_t i = 0; i < N_BROCHES; i++) {
    COMMANDES[i] = afficherBroche;
    COMMANDES[i + N_BROCHES] = fft;
    COMMANDES[i + 2*N_BROCHES] = afficherFFT;
  }
}

void ecouter() {
  if (Serial.available() > 0) {
    idx_t entree = Serial.read() % N_COMMANDES;
    idx_t arg = entree % N_BROCHES;
    COMMANDES[entree](arg);
  }
}

#endif