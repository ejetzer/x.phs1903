#include "fft.h"
#include "adc.h"
#include "print.h"

#define DEBIT 1000000
#define DELAI 2
#define broche A0

/** Active ou désactive la transformée de Fourier
 * Permet de modifier le programme sans avoir à touche au code.
 */
//#define CALCULER_FFT

/** Active la réception et l'exécution de commandes
 * Permet de plus facilement contrôler l'Arduino.
 */
//#define RECEVOIR_COMMANDES

#ifdef RECEVOIR_COMMANDES
bool prendre_mesure = false;
#endif

int_t i;

void acq() {
  ts[i] = micros();
  vReal[i] = analogRead(broche);
  vImag[i] = 0;
  i++;
}

int_t pre_facteur = 2;

void setup() {
  set_PF(pre_facteur);
  Serial.begin(DEBIT);
  Serial.setTimeout(DELAI);
  #ifdef CALCULER_FFT
  FFT = ArduinoFFT<val_t>(vReal, vImag, N, F);
  #endif
  #ifndef RECEVOIR_COMMANDES
  printParams();
  #endif
}

void loop() {
  #if defined(RECEVOIR_COMMANDES)
  if (prendre_mesure && (micros() - ts[i-1] >= T)) {
    acq();
  }
  #else
  if (micros() - ts[i-1] >= T) {
    acq();
  }
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
