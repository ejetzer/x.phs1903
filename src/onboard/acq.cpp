void acq() {
  ts[i] = micros();
  vReal[i] = analogRead(broche);
  vImag[i] = 0;
  i++;
}