#ifdef AFFICHER_INCLUS

// Impression d'une seule valeur
void afficherValeur(String nom, float val, String unit) {
  Serial.print(nom);
  Serial.print(" = ");
  Serial.print(val);
  Serial.print(unit);
}

void afficherValeur(String nom, int val, String unit) {
  Serial.print(nom);
  Serial.print(" = ");
  Serial.print(val);
  Serial.print(unit);
}

void afficherValeur(String nom, float val) {
  Serial.print(nom);
  Serial.print(" = ");
  Serial.print(val);
}

void afficherValeur(String nom, int val) {
  Serial.print(nom);
  Serial.print(" = ");
  Serial.print(val);
}

void afficherValeur(String nom, int val, int fmt) {
  Serial.print(nom);
  Serial.print(" = ");
  Serial.print(val, fmt);
}

// Impression d'un élément d'une liste
void afficherValeurListe(float val, int i, int n) {
  
  if (i != 0) {
    Serial.print(" ");
  }

  Serial.print(val);

  if (i != n-1) {
    Serial.print(", ");
  }
}

void afficherValeurListe(int val, int i, int n) {
  
  if (i != 0) {
    Serial.print(" ");
  }

  Serial.print(val);

  if (i != n-1) {
    Serial.print(", ");
  }
}

// Impression d'une liste
void afficherListe(String nom, float liste[], int n) {
  Serial.print(nom);
  Serial.print(" = [ ");

  for (int i=0; i < n; i++) {
    afficherValeurListe(liste[i], i, n);
  }

  Serial.print(" ]");
}

void afficherListe(String nom, int liste[], int n) {
  Serial.print(nom);
  Serial.print(" = [ ");

  for (int i=0; i < n; i++) {
    afficherValeurListe(liste[i], i, n);
  }

  Serial.print(" ]");
}

void afficherListe(float liste[], int n) {
  Serial.print("[ ");

  for (int i=0; i < n; i++) {
    afficherValeurListe(liste[i], i, n);
  }

  Serial.print(" ]");
}

void afficherListe(int liste[], int n) {
  Serial.print("[ ");

  for (int i=0; i < n; i++) {
    afficherValeurListe(liste[i], i, n);
  }

  Serial.print(" ]");
}


void afficherParams() {
  #ifdef SERIE_INCLUS
  afficherValeur("DEBIT", DEBIT, "Hz");
  Serial.print("; ");

  afficherValeur("DELAI", DELAI, "µs");
  Serial.print("; ");
  #endif

  #ifdef ACQ_INCLUS
  afficherValeur("F", F, "Hz");
  Serial.print("; ");

  afficherValeur("T", T, "µs");
  Serial.print("; ");

  afficherValeur("N", N);
  Serial.print("; ");
  #endif

  #ifdef CAN_INCLUS
  afficherValeur("ADC0.CTRLC", ADC0.CTRLC, BIN);
  Serial.print("; ");
  #endif

  Serial.println();
}

#ifdef ACQ_INCLUS
void printValues() {
  afficherListe("ts", TEMPS, N_ACQ);

  #if N_BROCHES > 1
  for (int i=0; i<N_BROCHES; i++) {
    afficherListe(BROCHES[i], MESURES[i], N_ACQ);
  }
  #else
  afficherListe(BROCHE, MESURES, N_ACQ);
  #endif

  Serial.println();
}
#endif

#ifdef FFT_INCLUS
void afficherFFT() {
  afficherListe("F", RES_FFT, N_FFT);
  Serial.println();
}

void afficherPics() {
  afficherValeur("F{V}(f)", MAGNITUDE_PIC);
  afficherValeur("f", FREQUENCE_PIC);
  Serial.println();
}
#endif

#endif
