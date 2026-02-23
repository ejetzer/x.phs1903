/**
 * Module pour le cours PHS1903,
 * basé sur `une compilation de M. Gammon`_.
 * Adapté pour l'Arduino Nano Every (ABX00028)
 * et le processeur ATMega4809.
 * Les particularités du processeur proviennent de
 * la :download:`fiche de données techniques <../../refs/ATMega4809.pdf>`.
 * Par Émile Jetzer, à l'hiver 2026.
 *
 * .. _une compilation de M. Gammon: https://www.gammon.com.au/adc
 */

#ifndef XPHS1903
#define XPHS1903

uint8_t clear_PF() {
	// Régler à 256
	ADC0.CTRLC &= ~( bit(0) | bit(1) | bit(2) ); // 0b11100000

	return ADC0.CTRLC;
}

/**
 * Horloge du CAN
 * ---------------
 *
 * Le :abbr:`CAN (Convertisseur Analogue-à-Numérique)` du ATMega4809 a besoin d'une fréquence
 * d'horloge entre 50kHz et 1.5MHz pour une
 * résolution maximale.
 */

/**
 * Préfacteur
 * -----------
 *
 * Le préfacteur du CAN est une puissance de deux qui
 * divise la fréquence de l'horloge du processeur.
 * :c:var:`pf_pow` est la puissance associée au préfacteur
 * :math:`2^{pf_pow}`.
 *
 * Le préfacteur (et tous les réglages du Arduino) est
 * réglé à partir de valeurs binaire dans un registre
 * de mémoire vive. Les registres précis dépendent du
 * processeur précis, et ne peuvent pas être assumés
 * pour d'autres plate-formes. Sur le Arduino Nano Every,
 * avec un processeur ``ATMega4809``, le CAN est géré par
 * le registre accessible via le nom :c:var:``ADC0``, et le 
 * préfacteur est réglé dans les 3 premiers bits du
 * sous-registre :c:var:`ADC0.CTRLC`.
 */

/** La fonction :c:func:`set_PF` règle le préfacteur selon
 * la valeur de :c:var:`pf_pow`. La fonction ne touche
 * qu'aux trois bits concernant le pré-facteur, et laisse
 * les autres bits intacts.
 */
uint8_t set_PF(uint8_t pf_pow) {
	ADC0.CTRLC &= ~( bit(0) | bit(1) | bit(2) ); // 0b11100000
	ADC0.CTRLC |= bit(0) * (pf_pow % 8);
	ADC0.CTRLC |= bit(1) * ( (pf_pow % 4) / 2 );
	ADC0.CTRLC |= bit(2) * ( pf_pow / 4 );
	
	return ADC0.CTRLC;
}

uint8_t set_PF() {
	return set_PF(7);
}
#endif