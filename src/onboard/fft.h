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

/** Le nombre d'échantillons récoltés pour faire la
  * transformée. Cette valeur doit toujours être une
  * puissance de 2.
  * La valeur de :c:macro:`N` doit prendre en compte
  * la période du signal à détecter et la période
  * d'échantillonage :cpp:var:`T`.
  *
  * La documentation du module indique que des valeurs de 2048 et 4096
  * causent des erreurs d'overflow, et qu'elles devraient être évitées.
  */
#ifdef CALCULER_FFT
#define N 256
#elif defined(HAUTE_PRECISION)
#define N 128
#else
#define N 1024
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
#define cadre FFTWindow::Hann

/** La classe :cpp:class:`ArduinoFFT` permet d'utiliser soit le type
  * :cpp:type:`float` ou le type :cpp:type:`double` pour les valeurs
  * et les résultats. Pour faciliter la configuration, vous pouvez
  * redefinir le type :cpp:type:`val_t`.
  */
#if defined(HAUTE_PRECISION)
typedef double val_t;
#elif defined(CALCULER_FFT)
typedef float val_t;
#else
typedef int val_t;
#endif

/** La fréquence et la période d'échantillonage sont constants
  * dans ce programme, donc on peut les déclarer comme tels et
  * permettre au compilateur de mieux optimiser le programme.
  */
typedef const val_t cons_t;

typedef unsigned long int_t;

/** La fréquence d'échantillonage en Hz.
  * Idéalement un nombre qui divise 1000000
  * ou une puissance de 2
  * pour faire une conversion exacte entre
  * la fréquence :cpp:var:`F` en Hz et la période
  * :cpp:var:`T` en µs.
  */
val_t F = 10000.0;

/** La période d'échantillonage en µs, calculée une fois
  * à partir de la fréquence :c:macro:`F`.
  * :cpp:var:`T` est utilisée en comparaison avec 
  * l'horloge interne :cpp:func:`macros`.
  */
#define muS 1000000.0
val_t T = muS / F;

/** Composante réelle de la fonction dont on veut
  * calculer la transformée de Fourier. En pratique,
  * nos mesures sont toutes positives, mais comme
  * la transformée utilise la première moitiée de 
  * :cpp:var:`vReal` et :cpp:var:`vImag` pour
  * enregistrer le résultat de la transformée,
  * il faut permettre les valeurs négatives.
  * Pour plus de précision, vous pouvez utiliser
  * le type :cpp:type:`double`, qui prend par contre
  * deux fois plus de mémoire.
  */
#ifndef HAUTE_PRECISION
#ifndef CALCULER_FFT
unsigned char vReal[N];
#else
val_t vReal[N];
#endif
#else
val_t vReal[N];
#endif

/** Composante imaginaire de la fonction dont on veut
  * calculer la transformée de Fourier. En pratique,
  * nos mesures sont toutes positives, mais comme
  * la transformée utilise la première moitiée de 
  * :cpp:var:`vReal` et :cpp:var:`vImag` pour
  * enregistrer le résultat de la transformée,
  * il faut permettre les valeurs négatives.
  * Pour plus de précision, vous pouvez utiliser
  * le type :cpp:type:`double`, qui prend par contre
  * deux fois plus de mémoire.
  */
#ifndef HAUTE_PRECISION
#ifndef CALCULER_FFT
unsigned char vImag[N];
#else
val_t vImag[N];
#endif
#else
val_t vImag[N];
#endif

int_t ts[N];

#ifdef CALCULER_FFT
val_t* freq;
val_t* mag;

ArduinoFFT<val_t> FFT;

void fft();
#endif
