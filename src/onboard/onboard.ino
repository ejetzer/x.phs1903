#define DEBIT 1000000
#define DELAI 2
#define BROCHE A0
#define N_BROCHE 1
#define N 256
#define RAPIDE

#include "adc.h"
#include "fft.h"
#include "acq.h"
#include "afficher.h"
#include "cmd.h"

void setup() {
  CANInit();
  T = 200 // us
}

void loop() {
#ifndef RAPIDE
  acq();
#endif
  else if (i == N) {
    #if defined(RECEVOIR_COMMANDES)
    prendre_mesure = false;
    #else
    printValues();
    #if defined(CALCULER_FFT)
    fft();
    printFFT();
    #endif
    Serial.println();
    #endif
    i = 0;
  }
  #ifdef RECEVOIR_COMMANDES
  else if ( Serial.available() > 0 ) {
    String commande = Serial.readStringUntil('\n');
    if (commande == "arrêter") {
      return; // Arrête l'exécution du programme.
    }
    #ifdef CALCULER_FFT
    else if (commande == "fft") {
      fft();
      printFFT();
      Serial.println();
    }
    #endif
    else if (commande == "données") {
      printValues();
      Serial.println();
    } else if (commande == "mesures") {
      prendre_mesure = true;
    } else if (commande == "paramètres") {
      printParams();
    } else if (commande == "allumer") {
      digitalWrite(LED_BUILTIN, HIGH);
    } else if (commande == "éteindre") {
      digitalWrite(LED_BUILTIN, LOW);
    } else if (commande == "cycler pf") {
      pre_facteur = (pre_facteur + 1) % 7;
      Serial.println(pre_facteur);
      set_PF(pre_facteur);
    } else if (commande == "cycler freq") {
      F = 10.0 * F;
      if (F >= 1000000.0) {
        F = 1;
      }
      T = muS / F;
      Serial.print("F = ");
      Serial.print(F);
      Serial.print("; T = ");
      Serial.print(T);
      Serial.println();
    }
  }
  #endif
}
