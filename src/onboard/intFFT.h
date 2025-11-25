#ifndef intFFT_INCLUS
#define intFFT_INCLUS

#ifndef N
#define N 256
#endif

#ifndef N_BROCHES
#define N_BROCHES 2
#endif

#ifndef F
#define F 124
#endif

#ifndef T
#define T (1e6 / F)
#endif

#include <Arduino.h>
#include "types.h"
#include "adc.h"

#define COMPENSATION_HANN 3.7109453796
#define carre(x) (x*x)
#define subtract(a, b) for (idx_t _k=0; _k<N; _k++) { a[_k] -= b; }

float_t hann[N/2];

// Source - https://stackoverflow.com/a/34187992
// Posted by wildplasser, modified by community. See post 'Timeline' for change history
// Retrieved 2025-11-24, License - CC BY-SA 3.0

/* static will allow inlining */
static val_t racine(val_t val) {
    val_t a, b;

    if (val < 2) return val; /* avoid div/0 */

    a = 1255;       /* starting point is relatively unimportant */

    // 4 itérations.
    b = val / a; a = (a+b) /2;
    b = val / a; a = (a+b) /2;
    b = val / a; a = (a+b) /2;
    b = val / a; a = (a+b) /2;

    return a;
}

void abs(idx_t j) {
  for (idx_t i=0; i < (N >> 1); i++) {
    reel[j][i] = racine(carre(reel[j][i]) + carre(imag[j][i]));
  }
}

void enlever_dc(idx_t j) {
  val_t som = 0;
  for (idx_t i=0; i < N; i++) {
    som += reel[j][i];
  }
  val_t moy = (val_t)((float_t)som / (float_t)N);
  
  subtract(reel[j], moy)
}

void hannInit() {
  val_t idx_moins_un = (val_t(N) - 1);
  val_t facteur_compensation;
  
  for (idx_t i = 0; i < (N>>1); i++) {
    val_t i_moins_un = i - 1;
    float_t poids = 0.5 * (1.0 - cos(TWO_PI * (float_t)i_moins_un / (float_t)idx_moins_un));
    hann[i] = poids * COMPENSATION_HANN;
    hann[N - (i+1)] = poids * COMPENSATION_HANN;
  }
}

void cadre(idx_t j) {
  for (idx_t i=0; i < N/2; i++) {
    reel[j][i] = (val_t)((float_t)(reel[j][i]) * hann[i]);
    reel[j][N-i] = (val_t)((float_t)(reel[j][i]) * hann[i]);
  }
}

idx_t log_2(idx_t x) {
  idx_t res = 0;
  while (x >>= 1) res++;
  return res;
}

void fft(idx_t j) {
  enlever_dc(j);
  cadre(j);
  
  float_t c_1 = -1;
  float_t c_2 = 0;
  val_t puissance = log_2(N);
  
  int_t L_2 = 1;
  for (idx_t L=0; L < puissance; L++) {
    idx_t L_1 = L_2;
    L_2 <<= 1;
    
    float_t u_1 = 1;
    float_t u_2 = 0;
    for (idx_t j = 0; j < L_1; j++) {
      for (idx_t i = j; i < N; i += L_2) {
        idx_t i_1 = i + L_1;
        val_t t_1 = u_1 * (float_t)(reel[j][i_1]) - u_2 * (float_t)(imag[j][i_1]);
        val_t t_2 = u_1 * (float_t)(imag[j][i_1]) + u_2 * (float_t)(reel[j][i_1]);
        reel[j][i_1] = reel[j][i] - t_1;
        imag[j][i_1] = imag[j][i] - t_2;
        reel[j][i] += t_1;
        imag[j][i] += t_2;
      }

      float_t z = (u_1 * c_1) - (u_2 * c_2);
      u_2 = (u_1 * c_2) + (u_2 * c_1);
      u_1 = z;
    }
    
    float_t c_T = 0.5 * c_1;
    c_2 = -racine(0.5 - c_T);
    c_1 = racine(0.5 + c_T);
  }
  
  abs(j);
}

#endif