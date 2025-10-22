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
#define DEBUG

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

int broche[2] = {A0, A2}; // Liste pour les broches de lecture

byte mesure[2] = {0, 0}; // Liste pour les lectures analogiques

// Initialisation du port série à 115200 bits par seconde et un timeout de 100ms
void setup() {
	// Initialisation du port série
	Serial.begin(DEBIT);
	Serial.setTimeout(DELAI);
	delay(200);
}

void loop() {
	// Lecture des données des ports de conversion analogiques
	mesure[IR] = (byte) analogRead(broche[IR]);
	mesure[VIS] = (byte) analogRead(broche[VIS]);
	
	// Serial.available retourne le nombre d'octets (max. 64o) disponibles
	// dans le tampon du micro-contrôleur. Si la fonction retourne 0,
	// le bloc conditionnel sera ignoré.
	if ( Serial.available() > 0 ) {
		// cmd contient une instruction d'1 octet envoyé par un programme 
		// client via la communication série.
		int cmd = Serial.read(); // Lire 1 caractère

		#ifdef DEBUG
		Serial.print("Reçu le caractère "); Serial.print((int)cmd); Serial.print(" ou "); Serial.println((char)cmd);
		Serial.print("Mesure de "); Serial.print(mesure[IR]); Serial.print(" pour la photodiode IR, et de "); Serial.print(mesure[VIS]); Serial.println(" pour la photodiode visible.");
		#endif
		
		// Serial.availableForWrite indique si il y a suffisamment d'espace
		// libre dans le tampon d'écriture pour envoyer les données.
		if ( cmd == 'i' && Serial.availableForWrite() > 0 ) {
			#ifdef DEBUG
			Serial.print("Envoi de la valeur "); Serial.println((int)mesure[IR]);
			#endif

			Serial.write(mesure[IR]); // Envoyer la valeur IR dans un octet
			Serial.flush();
			#ifdef DEBUG
			Serial.println();
			#endif
		} else if ( cmd == 'v' && Serial.availableForWrite() > 0 ) {
			#ifdef DEBUG
			Serial.print("Envoi de la valeur "); Serial.println((int)mesure[IR]);
			#endif

			Serial.write(mesure[VIS]); // Envoyer la valeur vis. dans un octet
			Serial.flush();
			#ifdef DEBUG
			Serial.println();
			#endif
		}
		#ifdef DEBUG
		else if ( Serial.availableForWrite() > 0 ) {
			Serial.println("Aucune commande valide reçue.");
		}
		#endif
	}
}

