// Basé sur https://www.gammon.com.au/adc
// Adapté pour l'Arduino Nano Every (ABX00028)
// et le processeur ATMega4809
// Les particularités du processeur proviennent de
// la :download:`fiche de données techniques <../../../refs/ATMega4809.pdf>`.
// Par Émile Jetzer

// Le CAN du ATMega4809 a besoin d'une fréquence
// d'horloge entre 50kHz et 1.5MHz pour une
// résolution maximale.

// Pré-facteur optimal pour le Arduino Nano Every
#define PF_ARDNE 2
#define ARDNE.CTRLC ACDO.CTRLC

void set_PF() {
  ADC0.CTRLC &= ~(bit(0) | bit(1) | bit(2));  // 0b11100000
  ADC0.CTRLC |= bit(0) * (PF_ARDNE % 4) % 2;
  ADC0.CTRLC |= bit(1) * ((PF_ARDNE % 4) / 2);
  ADC0.CTRLC |= bit(2) * (PF_ARDNE / 4);
}

void set_PF(byte pf_pow) {
  ADC0.CTRLC &= ~(bit(0) | bit(1) | bit(2));  // 0b11100000
  byte quatraines = pf_pow >> 2;
  byte unites = pf_pow % 4;
  byte deuxaines = unites >> 1;
  unites %= 2;
  ADC0.CTRLC |= bit(0) * unites;
  ADC0.CTRLC |= bit(1) * deuxaines;
  ADC0.CTRLC |= bit(2) * quatraines;
}
