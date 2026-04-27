#include <hautefrequence.h>

phs::BrocheAnalogique_HF::BrocheAnalogique_HF();
phs::BrocheAnalogique_HF::BrocheAnalogique_HF(uint8_t);
void phs::BrocheAnalogique_HF::setup();
uint8_t phs::BrocheAnalogique_HF::obtCTRLC();
uint8_t phs::BrocheAnalogique_HF::obtPrefacteur();
uint8_t phs::BrocheAnalogique_HF::obtPuissance();
void phs::BrocheAnalogique_HF::regCTRLC(uint8_t);
void phs::BrocheAnalogique_HF::regPrefacteur(uint8_t);
void phs::BrocheAnalogique_HF::regPuissance(uint8_t);
void phs::BrocheAnalogique_HF::reinitCTRLC();
ufloat32_t phs::BrocheAnalogique_HF::obtFrequence();
void phs::BrocheAnalogique_HF::regFrequence();