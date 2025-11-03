/*
* Titre: Oxymètre V1
* Auteurs:
*  - Jacques Massicotte <jacques-2.massicotte@polymtl.ca>
*  - Émile Jetzer <emile.jetzer@polymtl.ca>
* Date: Hiver 2025
* Màj: 2025-10
* Plateforme: Arduino Nano Every 
* Description : Programme qui fait l'acquisition de signaux de tension
* électrique reçus par deux photodiodes (visible et infrarouge) et envoie
* le signal converti sur le port série, afin qu'il soit traité par un code
* Python sur un ordinateur.
*/

// Définitions préliminaires
// L'instruction de pré-compilation `#define` permet de définir des
// valeurs nommées, comme des variables, mais sans utiliser de bloc mémoire.
// 
// #define <nom> <valeur>

void set_PF(unsigned char);

// Paramètres de la communication série.
// Un débit plus lent interfère avec les mesures
// et un débit plus rapide fait chauffer le micro-contrôleur
#define DEBIT 1000000 // baud (≅bit/s)
#define DELAI 2 // µs Le temps d'attente en lecture, compter 20µs/octet à 115200

// Si vous voulez mesurer les valeurs de plus de diodes,
// Augmentez la valeur de N_broches et ajoutez des valeurs
// aux listes en conséquence.
#define N_broches 1 // Nombre de broches
#define M_mesures 1700 // Nombre de mesures
const unsigned char broche[N_broches] = {A1}; // Liste pour les broches de lecture
unsigned char mesure[N_broches+1][M_mesures]; // Liste pour les lectures analogiques

// Initialisation du port série à 115200 bits par seconde et un timeout de DELAI
void setup() {
	// Initialisation du port série
	Serial.begin(DEBIT);
	Serial.setTimeout(DELAI);
	Serial.println();
	
	set_PF(2);
}

unsigned int j = 0;

void loop() {
	// Lecture des données des ports de conversion analogiques
	mesure[0][j] = micros();
	for (unsigned char i=0; i < N_broches; i++) {
		mesure[i+1][j] = analogRead(broche[i]);
	}
	
	j++;

	// Serial.available retourne le nombre d'octets (max. 64o) disponibles
	// dans le tampon du micro-contrôleur. Si la fonction retourne 0,
	// le bloc conditionnel sera ignoré.
	if ( j == M_mesures ) {
		// Envoyer toutes les données récoltées d'un coup
		for (int m=0; m<M_mesures; m++) {
			Serial.print(mesure[0][m]);
			for (byte n=1; n<=N_broches; n++) {
				Serial.print("\t");
				Serial.print(mesure[n][m]);
			}
			Serial.println();
		}
		j = 0;
	}
}

