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

#include <Arduino.h>
#include <avr/interrupt.h>

// Pré-facteur optimal pour le Arduino Nano Every
#ifndef PF_ARDNE
#define PF_ARDNE 2
#endif

#ifndef CAN
#define CAN ADC0
#endif

#ifndef bit
#define bit(n) (1 << (n))
#define bitClear(value, n) ((value) &= ~(1UL << (n)))
#define bitRead(value, n) (((value) & bit(n)) >> (n))
#define bitSet(value, n) ((value) |= (1UL << (n)))
#define bitWrite(value, n, b) ((b) == 1 ? bitSet(value, n) : bitClear(value, n))
#define highByte(w) ((byte)(((w) >> 8) & 0xFF))
#define lowByte(w) ((byte)((w) & 0xFF))
#endif

#define reinit_freq_can() (CAN.CTRLC &= ~(0x7))

#define pf_puissanceRead() (CAN.CTRL0 & 0x7)
#define pfRead() ((byte)(1 << pf_puissanceRead()))
#define pf_puissanceSet(v) (CAN.CTRL0 &= (0x7 & v))
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
  (CPU.SREG |= 0x80)

#define portPinCtrlCfg(pinCtrl, v)                                             \
  (pinCtrl &= ~(0x7));                                                         \
  (pinCtrl |= (v))

#ifndef N
#define N 1024
#endif

#ifndef N_BROCHES
#define N_BROCHES 8
#endif

volatile unsigned long int temps[N_BROCHES][N];
volatile unsigned int mesures[N_BROCHES][N];
volatile unsigned char A_n = 0;
volatile unsigned long int n = 0;

const unsigned char _BROCHES[8] = {PIN_A0, PIN_A1, PIN_A2, PIN_A3,
                                   PIN_A4, PIN_A5, PIN_A6, PIN_A7};

unsigned char BROCHES[N_BROCHES];
for (unsigned char i = 0; i < N_BROCHES; i++) {
  BROCHES[i] = _BROCHES[i];
}

const unsigned char PORTS_CTRL[8] = {
    PORTD.PIN3CTRL, PORTD.PIN2CTRL, PORTD.PIN1CTRL, PORTD.PIN0CTRL,
    PORTA.PIN2CTRL, PORTA.PIN2CTRL, PORTD.PIN4CTRL, PORTD.PIN5CTRL};

const unsigned char MUXPOS[8] = {0x3, 0x2, 0x1, 0x0,
                                 0x6, // Pas documenté?
                                 0xC, // (12) Pas documenté?
                                 0x4, 0x5};

#ifndef RAPIDE

unsigned long int T;
bool enAcq = true;

void acq(unsigned long int i, unsigned char a, unsigned long int *t,
         unsigned int *m) {
  t[a][i] = micros();
  m[a][i] = analogRead(BROCHES[a]);
}

void acq() {
  static unsigned char a;
  static unsigned long int i;
  static unsigned long int t0;
  static unsigned long int t = micros();

  if ((t - t0) >= T && enAcq) {
    A_n++;
    if (A_n == N_BROCHES) {
      A_n = 0;
      n++;

      if (n == N) {
        n = 0;
      }
    }

    temps[a][i] = micros();
    mesures[a][i] = analogRead(BROCHES[a]);

    t0 = t;
  }
}

void CANInit(unsigned char res, unsigned char pf_puissance,
             unsigned char free_run) {
  // Initialisation
  analogPrecisionSet(res);
  freeRunSet(free_run);
  pf_puissanceSet(pf_puissance);
  enableAcq();
  enInt();
}

void CANInit() {
  // Initialisation
  analogPrecisionSet(10);
  freeRunSet(false);
  pf_puissanceSet(7);
  enableAcq();
  enInt();
}
#endif // ~RAPIDE

#ifdef RAPIDE
volatile unsigned char temps[N_BROCHES][N];
volatile unsigned char mesures[N_BROCHES][N];
volatile unsigned char A_n = 0;
volatile unsigned long int n = 0;

void CANInit() {
  // Initialisation
  analogPrecisionSet(8);
  freeRunSet(false);
  pf_puissanceSet(2);
  enableAcq();
  enInt();
}

void reglerBroche(byte broche) {
  configInput(MUXPOS[A_n]);
  portPinCtrlCfg(PORTS_CTRL[A_n], 0x4);
}

ISR(ADC_vect) {
  temps[A_n][n] = micros();
  mesures[A_n][n] = CAN.RES;

  A_n++;
  if (A_n == N_BROCHES) {
    A_n = 0;
    n++;

    if (n == N) {
      n = 0;
    }
  }

  configInput(MUXPOS[A_n]);
  portPinCtrlCfg(PORTS_CTRL[A_n], 0x4);

  enableAcq();
  enInt();
}
#endif // Rapide

#endif
