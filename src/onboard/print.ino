void printParams() {
  Serial.print("DEBIT = ");
  Serial.print(DEBIT);
  Serial.print("Hz; ");
  Serial.print("DELAI = ");
  Serial.print(DELAI);
  Serial.print("µs; ");
  Serial.print("F = ");
  Serial.print(F);
  Serial.print("Hz; ");
  Serial.print("T = ");
  Serial.print(T);
  Serial.print("µs; ");
  Serial.print("N = ");
  Serial.print(N);
  Serial.print("; ");
  Serial.print("ADC0.CTRLC = ");
  Serial.print(ADC0.CTRLC, BIN);
  Serial.println(";");
  Serial.println();
}

void printValues() {
  Serial.print("ts = [ ");
  Serial.print(ts[0]);
  for (int j = 1; j < N; j++) {
    Serial.print(", ");
    Serial.print(ts[j]);
  }
  Serial.println(" ]");

  Serial.print("A0 = [ ");
  Serial.print(vReal[0]);
  for (int j = 1; j < N; j++) {
    Serial.print(", ");
    Serial.print(vReal[j]);
  }
  Serial.println(" ]");
}

#ifdef CALCULER_FFT
void printFFT() {
  Serial.print("F = [ ");
  Serial.print(vReal[0]);
  for (int j = 1; j < N / 2; j++) {
    Serial.print(", ");
    Serial.print(vReal[j]);
  }
  Serial.println(" ]");
}

void printPeak() {
  Serial.print("F{V}(f) = ");
  Serial.print(*mag);
  Serial.print("; f = ");
  Serial.print(*freq);
  Serial.println(";");
}
#endif
