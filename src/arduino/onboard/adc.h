#ifndef ADC_INCLUS
#define ADC_INCLUS
/* Basé sur https://www.gammon.com.au/adc
   Adapté pour l'Arduino Nano Every (ABX00028)
   et le processeur ATMega4809
   Les particularités du processeur proviennent de
   la :download:`fiche de données techniques <../../../refs/ATMega4809.pdf>`.
   Par Émile Jetzer

   Le ATmega4809 a une fréquence d'horloge de 20MHz.

   Le CAN du ATMega4809 a besoin d'une fréquence
   d'horloge entre 50kHz et 1.5MHz pour une
   résolution maximale.

   Les réglages du préfacteur sont contenus dans le registre désigné par
   :c:macro:`ADC0.CTRLC`, spécifiquement les bits 0, 1 & 2.

   ``ADC0.CTRLC``

   ==== ==== ==== ==== ==== ==== ==== ====
   0    1    2    3    4    5    6    7
   ==== ==== ==== ==== ==== ==== ==== ====
   PF0  PF1  PF2
   ==== ==== ====


 */

#include "types.h"
#include <avr/interrupt.h>

// Pré-facteur optimal pour le Arduino Nano Every
#ifndef PF_ARDNE
#define PF_ARDNE 2
#endif

#ifndef CAN
#define CAN ADC0
#endif

#ifndef N
#define N 1024
#endif

#ifndef N_BROCHES
#define N_BROCHES 8
#endif

#define reinit_freq_can() (CAN.CTRLC &= ~(0x7))

#define pf_puissanceRead() (CAN.CTRLC & 0x7)
#define pfRead() ((byte)(1 << pf_puissanceRead()))
#define pf_puissanceSet(v) (CAN.CTRLC &= (0x7 & v))
#define canClkRead() (20e6 / pfRead())

#define analogPrecisionRead() ((bitRead(CAN.CTRLA, 2)) ? 8 : 10)
#define analogPrecisionSet(n)                                                  \
  ((n == 10) ? bitClear(CAN.CTRLA, 2)                                          \
             : ((n == 8) ? bitSet(CAN.CTRLA, 2) : bitRead(CAN.CTRLA, 2)))

#define freeRunRead() (CAN.CTRLA & 0x2)
#define freeRunSet(v) ((v) ? (CAN.CTRLA &= ~(0x2)) : (CAN.CTRLA |= 0x2))
#define freeRun() (freeRunSet(1))

#define configInput(broche)                                                    \
  (CAN.MUXPOS &= ~(0x1F));                                                     \
  (CAN.MUXPOS |= broche)
#define enableAcq() (CAN.CTRLA |= 0x1)

#define startConversion() (CAN.COMMAND |= 0x1)
#define isConverting() (CAN.COMMAND & 0x1)

#define enInt()                                                                \
  (CAN.INTCTRL |= 0x1);                                                        \
  sei()
#define disInt()                                                               \
  (CAN.INTCTRL &= 0xFE);                                                        \
  cli()

#define portPinCtrlCfg(pinCtrl, v)                                             \
  (pinCtrl &= ~(0x7));                                                         \
  (pinCtrl |= (v))

#define maj(l, v) (l[A_n][n] = v)

bool calculer = false;

vol_val_t t;
vol_val_t t0;
vol_val_t m;
vol_idx_t A_n = 0;
vol_idx_t n = 0;
vol_idx_t c = 0;
vol_idx_t c0 = 0;

val_t temps[N_BROCHES];
val_t reel[N_BROCHES][N];
val_t imag[N_BROCHES][N];

const unsigned char BROCHES[8] = {PIN_A0, PIN_A1, PIN_A2, PIN_A3,
                                   PIN_A4, PIN_A5, PIN_A6, PIN_A7};

//const unsigned char PORTS_CTRL[8] = {
//    PORTD.PIN3CTRL, PORTD.PIN2CTRL, PORTD.PIN1CTRL, PORTD.PIN0CTRL,
//    PORTA.PIN2CTRL, PORTA.PIN2CTRL, PORTD.PIN4CTRL, PORTD.PIN5CTRL};

const unsigned char MUXPOS[8] = {0x3, 0x2, 0x1, 0x0,
                                 0x6, // Pas documenté?
                                 0xC, // (12) Pas documenté?
                                 0x4, 0x5};

void reglerBroche(byte broche) {
  configInput(MUXPOS[A_n]);
  // §29.3.1.1 du manuel du ATmega4809
  //portPinCtrlCfg(PORTS_CTRL[A_n], 0x4);
}

#if !defined(RAPIDE)

#ifndef Pe
// 500 µ
#define Pe 1e3
#endif

#ifndef Fr
#define Fr 1e6 / Pe
#endif

void acq() {
  t0 = t;
  t = micros();

  if ((t - t0) >= Pe) {
    A_n++;
    c++;
    if (A_n == N_BROCHES) {
      A_n = 0;
      n++;

      if (n == N) {
        n = 0;
      }
    }

    temps[A_n] += t - t0;
    reel[A_n][n] = analogRead(BROCHES[A_n]);
    #if defined(FFT_INCLUS) || defined(intFFT_INCLUS)
    imag[A_n][n] = 0;
    #endif
  }
}

void CANInit() {
  // Initialisation
  pf_puissanceSet(PF_ARDNE);
}

#else // ^ ~RAPIDE; v RAPIDE

void CANInit() {
  // Initialisation
  analogPrecisionSet(8);
  freeRunSet(false);
  pf_puissanceSet(2);
  enableAcq();
  enInt();
}

void acq() {
  if (m != 0 && t != t0) {
    t0 = t;
    temps[A_n] += t - t0;
    maj(reel, m);
    maj(imag, 0);
    m = 0;
  }
}

ISR(__vector_ADC_vect) {
  t = micros();
  m = CAN.RES;

  A_n++;
  if (A_n == N_BROCHES) {
    A_n = 0;
    n++;

    if (n == N) {
      n = 0;
      disInt();
    }
  }

  configInput(MUXPOS[A_n]);
  //portPinCtrlCfg(PORTS_CTRL[A_n], 0x4);

  enableAcq();
  enInt();
}

#endif // Rapide

#endif // ADC_INCLUS