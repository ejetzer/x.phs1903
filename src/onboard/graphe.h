#ifndef PLOT_INCLUS
#define PLOT_INCLUS

#include <Arduino.h>
#include "types.h"
#include "adc.h"
#include "intFFT.h"
#include "afficher.h"

void dessiner() {
  for (idx_t l=0; l<N_BROCHES) {
    Serial.print("A"); Serial.print(l);
    Serial.print(":");
    Serial.print(reel[i][n]);
    if l + 1 != N_BROCHES {
      Serial.print(" ");
    }
  }
  Serial.println();
}
#endif