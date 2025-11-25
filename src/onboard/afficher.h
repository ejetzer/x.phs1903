#ifndef AFFICHER_INCLUS
#define AFFICHER_INCLUS

#ifndef DEBIT
#define DEBIT 1000000
#endif

#ifndef DELAI
#define DELAI 2
#endif

#include <Arduino.h>
#include "types.h"
#include "adc.h"
#include "intFFT.h"


void afficherInit() {
  Serial.begin(DEBIT);
  Serial.setTimeout(DELAI);
  Serial.print("N ");
  Serial.print(N);
  Serial.print("\tN_BROCHES ");
  Serial.println(N_BROCHES);
}

void afficherBroche(idx_t j) {
  val_t d = (val_t)((float_t)(temps[j]) / (float_t)(N));
  Serial.print("d ");
  Serial.print(d);
  Serial.print("\tA");
  Serial.print(j);
  for (idx_t i=0; i < N; i++) {
    Serial.print(" ");
    Serial.print(reel[j][i]);
  }
  Serial.println();
}

void afficherFFT(idx_t j) {
  val_t d = (val_t)((float_t)(temps[j]) / (float_t)(N));
  Serial.print("d ");
  Serial.print(d);
  Serial.print("\tF");
  Serial.print(j);
  for (idx_t i=0; i < (N>>1); i++) {
    Serial.print(" ");
    Serial.print(reel[j][i]);
  }
  Serial.println();
}
#endif