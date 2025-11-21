#ifdef ACQ_INCLUS

void acq() {
  ts[i] = micros();
  vReal[i] = analogRead(broche);
  vImag[i] = 0;
  i++;
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

void CANInitRapide() {
  // Initialisation
  analogPrecisionSet(8);
  freeRunSet(true);
  pf_puissanceSet(2);
  enableAcq();
  enInt();
}

void reglerBroche(byte broche) {
  configInput(MUXPOS[A_n]);
  portPinCtrlCfg(PORTS_CTRL[A_n], 0x4);
}

ISR(ADC_vect) {
  configInput(MUXPOS[A_n]);
  portPinCtrlCfg(PORTS_CTRL[A_n], 0x4);
  ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
    temps[A_n][n] = micros();
    mesures[A_n][n] = CAN.RES;
  }

  A_n++;
  if (A_n == N_BROCHES) {
    A_n = 0;
    n++;

    if (n == N) {
      n = 0;
    }
  }
}

#endif