// Test de précision des préfacteurs du CAN
// Basé sur https://www.gammon.com.au/adc
// Adapté pour l'Arduino Nano Every (ABX00028)
// et le processeur ATMega4809
// Les particularités du processeur proviennent de
// la :download:`fiche de données techniques <../../../refs/ATMega4809.pdf>`.
// Par Émile Jetzer

// Le CAN du ATMega4809 a besoin d'une fréquence
// d'horloge entre 50kHz et 1.5MHz pour une
// résolution maximale.

// Connections
// ------------
//
//                A0(4) -- rail+ -- 5V(12)
//                A1(5)          -- 3V3(2)
// rail- -- R2 -- A2(6) -- R1    -- 5V(12)
//                A3(7) -- rail- -- GND(15)
//
// R1 = R2 = 2kΩ

const int PRESC[3] = {bit(0), bit(1), bit(2)};
const int PF_null = ~( PRESC[0] | PRESC[1] | PRESC[2] ); // 0b11100000
const int ports[4] = {A0, A1, A2, A3};

int clear_PF() {
	// Régler à 256
	ADC0.CTRLC &= PF_null;

	return ADC0.CTRLC;
}

int set_PF() {
	set_PF(7);
}

int set_PF(int pf_pow) {
	clear_PF();
	
	int unites = pf_pow % 8 / 1;
	int deuxaines = pf_pow % 4 / 2;
	int quatraines = pf_pow % 1 / 4;
	
	ADC0.CTRLC |= PRESC[0] * (pf_pow % 8);
	ADC0.CTRLC |= PRESC[1] * ( (pf_pow % 4) / 2 );
	ADC0.CTRLC |= PRESC[2] * ( pf_pow / 4 );
	
	return ADC0.CTRLC;
}

void show_adc0() {
	Serial.print("ADC0    ");
	for (int i=7; i>=0; i--) {
		Serial.print("\t");
		Serial.print(i);
	}
	Serial.println();

	Serial.print(".CTRLA    ");
	for (int i=7; i >= 0; i--) {
		Serial.print("\t");
		Serial.print(bitRead(ADC0.CTRLA, i));
	}
	Serial.println();

	Serial.print(".CTRLB    ");
	for (int i=7; i >= 0; i--) {
		Serial.print("\t");
		Serial.print(bitRead(ADC0.CTRLB, i));
	}
	Serial.println();

	Serial.print(".CTRLC    ");
	for (int i=7; i >= 0; i--) {
		Serial.print("\t");
		Serial.print(bitRead(ADC0.CTRLC, i));
	}
	Serial.println();

	Serial.print(".CTRLD    ");
	for (int i=7; i >= 0; i--) {
		Serial.print("\t");
		Serial.print(bitRead(ADC0.CTRLD, i));
	}
	Serial.println();

	Serial.print(".CTRLE    ");
	for (int i=7; i >= 0; i--) {
		Serial.print("\t");
		Serial.print(bitRead(ADC0.CTRLE, i));
	}
	Serial.println();

	Serial.print(".SAMPCTRL");
	for (int i=7; i >= 0; i--) {
		Serial.print("\t");
		Serial.print(bitRead(ADC0.SAMPCTRL, i));
	}
	Serial.println();

	Serial.print(".MUXPOS   ");
	for (int i=7; i >= 0; i--) {
		Serial.print("\t");
		Serial.print(bitRead(ADC0.MUXPOS, i));
	}
	Serial.println();

	Serial.print(".COMMAND");
	for (int i=7; i >= 0; i--) {
		Serial.print("\t");
		Serial.print(bitRead(ADC0.COMMAND, i));
	}
	Serial.println();

	Serial.print(".CALIB   ");
	for (int i=7; i >= 0; i--) {
		Serial.print("\t");
		Serial.print(bitRead(ADC0.CALIB, i));
	}
	Serial.println();
}

void setup() {
	Serial.begin(115200);
	Serial.println();
	set_PF();
	analogReadResolution(16);
}

const int ITERATIONS = 1000;
unsigned long totaux[8];
const int port_bas = 0;
const int port_haut = 3;
int puissance_courante = 0;

void loop() {
	// Régler les préfacteurs
	set_PF(puissance_courante);
	show_adc0();
	Serial.println();
	Serial.print("puissance_courante = ");
	Serial.println(puissance_courante);
	Serial.print("Préfacteur = ");
	Serial.println(pow(2, puissance_courante+1));
	
	// Réinitialiser les totaux
	for (int quel_port = port_bas; quel_port <= port_haut; quel_port++) {
		int i = quel_port - port_bas;
		totaux[i] = 0;
	}

	unsigned long temps_debut = micros();
	for (int i = 0; i < ITERATIONS; i++) {
		for (int quel_port = port_bas; quel_port <= port_haut; quel_port++) {
			int p = ports[quel_port];
			int resultat = analogRead(p);
			int j = quel_port - port_bas;
			totaux[j] += resultat;
		}
	}
	unsigned long temps_fin = micros();
	
	unsigned long temps_debut_placebo = micros();
	for (int i = 0; i < ITERATIONS; i++) {
		for (int quel_port = port_bas; quel_port <= port_haut; quel_port++) {
			int p = ports[quel_port];
			//int resultat = 10;
			int j = quel_port - port_bas;
			//totaux[j+port_haut] += 10;
		}
	}
	unsigned long temps_fin_placebo = micros();
	float placebo = temps_fin_placebo - temps_debut_placebo;
	
	for (int quel_port = port_bas; quel_port <= port_haut; quel_port++) {
		Serial.print("Port analogique = ");
		Serial.print(quel_port);
		Serial.print(", moyenne = ");
		
		int i = quel_port - port_bas;
		float moyenne = totaux[i] / ITERATIONS / (port_haut - port_bas + 1);
		Serial.println(moyenne);
	}
	Serial.print("Temps pour ");
	Serial.print(ITERATIONS);
	Serial.print(" essais = ");
	long temps = temps_fin - temps_debut - placebo;
	Serial.print(temps/1e3);
	Serial.print("ms, en moyenne ");
	float temps_moyen = temps / ITERATIONS / 4;
	Serial.print(temps_moyen);
	Serial.println("µs par mesure.");
	float freq = 1.0 / temps_moyen;
	Serial.print("Fréquence d'échantillonage = ");
	Serial.print(freq*1e3);
	Serial.println("kHz");
	Serial.print("Estimé de la fréquence d'horloge = ");
	Serial.print(freq*13.5*1e3);
	Serial.print("kHz");
	Serial.println(" (devrait être entre 50-1500kHz)");
	
	Serial.println();
	Serial.flush();
	
	puissance_courante++;
	puissance_courante %= 8;

	while ( ! Serial.available() )
		delay(0.1);
	Serial.read();

	Serial.println();
}