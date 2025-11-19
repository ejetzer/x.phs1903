#ifndef AFFICHER_INCLUS
#define AFFICHER_INCLUS

#ifndef SERIE_INCLUS
#include "serie.h"
#endif

// Impression d'une seule valeur
void afficherValeur(String nom, float val, String unit);
void afficherValeur(String nom, int val, String unit);
void afficherValeur(String nom, float val);
void afficherValeur(String nom, int val);

// Impression d'un élément d'une liste
void afficherValeurListe(float val, int i);
void afficherValeurListe(int val, int i);

// Impression d'une liste
void afficherListe(String nom, float liste[], int n);
void afficherListe(String nom, int liste[], int n);
void afficherListe(float liste[], int n);
void afficherListe(int liste[], int n);

// Afficher les paramètres du programme
void afficherParams();

// Raccourcis pour afficher les listes spécifiques de onboard.ino
void afficherValeurs();

# ifdef CALCULER_FFT
void afficherFFT();
void afficherPics();
# endif
#endif