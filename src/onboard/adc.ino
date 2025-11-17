// Basé sur https://www.gammon.com.au/adc
// Adapté pour l'Arduino Nano Every (ABX00028)
// et le processeur ATMega4809
// Les particularités du processeur proviennent de
// la :download:`fiche de données techniques <../../../refs/ATMega4809.pdf>`.
// Par Émile Jetzer

// Le CAN du ATMega4809 a besoin d'une fréquence
// d'horloge entre 50kHz et 1.5MHz pour une
// résolution maximale.

void set_PF(unsigned char pf_pow) {
  ADC0.CTRLC &= ~(bit(0) | bit(1) | bit(2));  // 0b11100000
  ADC0.CTRLC |= bit(0) * (pf_pow % 8);
  ADC0.CTRLC |= bit(1) * ((pf_pow % 4) / 2);
  ADC0.CTRLC |= bit(2) * (pf_pow / 4);
}
