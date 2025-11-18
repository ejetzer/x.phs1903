#ifdef CALCULER_FFT
ArduinoFFT<val_t> FFT = ArduinoFFT<val_t>(vReal, vImag, N, F);

void fft() {
  FFT.dcRemoval();                              // Enlève la composante DC
  FFT.windowing(cadre, FFTDirection::Forward);  // Cadrage des données
  FFT.compute(FFTDirection::Forward);           // Calcul de la FFT
  FFT.complexToMagnitude();                     // Converti la FFT complexe en valeurs réelles
  FFT.majorPeak(freq, mag);                     // Enregistre le pic de fréquence
}
#endif