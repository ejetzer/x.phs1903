#ifndef FFT_INCLUS
#ifndef intFFT_INCLUS
#define FFT_INCLUS

#ifdef ENTIERS
#undef ENTIERS
#endif

#include "adc.h"

#ifndef ArduinoFFT_h
/** Au lieu d'utiliser l'opérateur de division,
  * utilise la multiplication.
  * Introduit potentiellement des erreurs dues
  * à la précision des :cpp:type:`float`.
  */
#define FFT_SPEED_OVER_PRECISION

/** Utilise une méthode d'approximation
  * très rapide pour les calculs.
  */
#define FFT_SQRT_APPROXIMATION

/** Garde en mémoire les facteurs utilisés
  * pour les calculs au lieu de les recalculer.
  * Si votre fréquence d'échantillonage est
  * plus grande que nécessaire, vous pouvez
  * essayer de commenter :c:macro:`USE_AVR_PROGMEM`.
  * Ça peut théoriquement vous permettre d'utiliser
  * plus d'échantillons, en libérant de la mémoire.
  */
#define USE_AVR_PROGMEM

/** Importer le module.
  * :arduinoFFT:`arduinoFFT </>` est une librairie
  * bien maintenue et utilisée. Elle permet plusieurs
  * optimisations
  */
#include <arduinoFFT.h>
#endif

/** Le nombre d'échantillons récoltés pour faire la
  * transformée. Cette valeur doit toujours être une
  * puissance de 2.
  * La valeur de :c:macro:`N` doit prendre en compte
  * la période du signal à détecter et la période
  * d'échantillonage :cpp:var:`T`.
  *
  * La documentation du module indique que des valeurs de 2048 et 4096
  * causent des erreurs d'overflow, et qu'elles devraient être évitées.
  *
  * Le processeur ATmega4809 du Arduino Nano Every a
  * 
  * - 48Ko de mémoire flash
  * - 6Ko de SRAM
  * - 256o de EEPROM
  * - 64o 
  */

#ifndef N
#define N 256
#endif

#ifndef N_BROCHES
#define N_BROCHES 1
#endif


/** Type de cadre à utiliser dans le calcul de la transformée.
  * Dans l'analyse de l'échantillon d'un signal, si on n'utilise
  * pas une fenêtre appropriée, on peut se retrouver avec des fuites
  * d'amplitude, de la fréquence réellement présente à des fréquences
  * adjacentes, ou vers de hautes fréquences.
  *
  * La fenêtre Hann fonctionne adéquatement pour des fonctions
  * arbitraires, mais si vous savez précisément quelles fréquences
  * vous allez devoir détecter, d'autres cadres peuvent être plus
  * pertinents.
  */
#ifndef CADRE
#define CADRE FFTWindow::Hann
#endif

/** La classe :cpp:class:`ArduinoFFT` permet d'utiliser soit le type
  * :cpp:type:`float` ou le type :cpp:type:`double` pour les valeurs
  * et les résultats. Pour faciliter la configuration, vous pouvez
  * redefinir le type :cpp:type:`val_t`.
  */

/** La fréquence et la période d'échantillonage sont constants
  * dans ce programme, donc on peut les déclarer comme tels et
  * permettre au compilateur de mieux optimiser le programme.
  */

/** La fréquence d'échantillonage en Hz.
  * Idéalement un nombre qui divise 1000000
  * ou une puissance de 2
  * pour faire une conversion exacte entre
  * la fréquence :cpp:var:`F` en Hz et la période
  * :cpp:var:`T` en µs.
  */
#ifndef Fr
#define Fr 75.0
#endif

/** La période d'échantillonage en µs, calculée une fois
  * à partir de la fréquence :c:macro:`F`.
  * :cpp:var:`T` est utilisée en comparaison avec 
  * l'horloge interne :cpp:func:`micros`.
  */
#ifndef Pe
#define Pe (1e6/Fr)
#endif

ArduinoFFT<float> (FFT[N_BROCHES]);

void fftInit() {
  for (idx_t i=0; i<N_BROCHES; i++) {
    FFT[i] = ArduinoFFT<float>(reel[i], imag[i], N, Fr);
  }
}

void fft(idx_t j) {
  FFT[j].dcRemoval();                              // Enlève la composante DC
  FFT[j].windowing(CADRE, FFTDirection::Forward);  // Cadrage des données
  FFT[j].compute(FFTDirection::Forward);           // Calcul de la FFT
  FFT[j].complexToMagnitude();                     // Converti la FFT complexe en valeurs réelles
}

#endif
#endif