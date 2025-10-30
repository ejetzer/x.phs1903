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

// Utilitaires de débogage
// Laisser l'instruction suivante commentée pour masquer les messages de débogage.
//#define DEBUG

// Les instructions à exécuter pour le débogage seront inclusent de cette façon:
// #ifdef DEBUG
// <instructions de débogage>
// #endif
// ce qui fait qu'elles ne seront pas inclusent dans le programme compilé si DEBUG n'est pas défini.

// Indices pour les différentes broches
// La DÉL ou photodiode IR est toujours à l'index 0.
// La DÉL ou photodiode visible est toujours à l'index 1.
#define IR 0
#define VIS 1

// Paramètres de la communication série.
// Un débit plus lent interfère avec les mesures
// et un débit plus rapide fait chauffer le micro-contrôleur
#define DEBIT 115200
#define DELAI 100 // Le temps d'attente

// Si vous voulez mesurer les valeurs de plus de diodes,
// Augmentez la valeur de N_broches et ajoutez des valeurs
// aux listes en conséquence.
const int N_broches = 2; // Nombre de broches
const int broche[N_broches] = {A0, A2}; // Liste pour les broches de lecture
int mesure[N_broches] = {0, 0}; // Liste pour les lectures analogiques

// Initialisation du port série à 115200 bits par seconde et un timeout de DELAI
void setup() {
	// Initialisation du port série
	Serial.begin(DEBIT);
	Serial.setTimeout(DELAI);
	delay(200);
}

void loop() {
	// Lecture des données des ports de conversion analogiques
	for (int i=0; i < N_broches; i++) {
		mesure[i] = analogRead(broche[i]);
	}
	
	// Serial.available retourne le nombre d'octets (max. 64o) disponibles
	// dans le tampon du micro-contrôleur. Si la fonction retourne 0,
	// le bloc conditionnel sera ignoré.
	while ( Serial.available() > 0 ) {
		// cmd contient une instruction d'1 octet envoyé par un programme 
		// client via la communication série.
		int cmd = Serial.read(); // Lire 1 octet
		
		if ( cmd < N_broches ) {
			Serial.println(mesure[cmd]);
		}
	}
}

