/** Implémentation naïve d'un serveur
 * ====================================
 * 
 * Description
 * --------------
 *
 * Programme qui fait l'acquisition de signaux de tension
 * électrique reçus par deux photodiodes (visible et infrarouge) et envoie
 * le signal converti sur le port série, afin qu'il soit traité par un code
 * Python sur un ordinateur.
 */

/**
 * Définitions préliminaires
 * -----------------------------
 */

/** L'instruction de pré-compilation `#define` permet de définir des
 * valeurs nommées, comme des variables, mais sans utiliser de bloc mémoire.
 */

/**
 * .. code-block:: cpp
 *
 * 		#define <nom> <valeur>
 */

/** Paramètres de la communication série
 * ------------------------------------------
 */

/** Débit de la communication série.
 * Un débit plus lent interfère avec les mesures
 * et un débit plus rapide fait chauffer le micro-contrôleur.
 * Par défaut, Arduino utilise un débit de 9600, mais 115200 est
 * fréquemment utilisé. Le plus rapide qu'Émile Jetzer a réussi
 * à faire fonctionner est 1000000.
 *
 * Sur les lignes séries que nous utilisons, les bits ne sont
 * pas représentés simplement par un niveau :c:macro:`HAUT` et un
 * :c:macro:`BAS`. Pour des raisons techniques, un bit nul (``0``,
 * ou :c:macro:`BAS`) est représenté par une valeur constante sur
 * un cycle d'horloge, et un bit positif (``1`` ou :c:macro:`HAUT`)
 * par un changement de valeur sur un cycle d'horloge. Le débit qu'on
 * décrit pour la communication série représente le plus de changements
 * d'états à envoyer ou auxquels s'attendre sur la ligne de communication.
 * C'est la fréquence maximale qu'on observerait pour un signal composé
 * entièrement de ``1``.
 */
#define DEBIT 115200

/** Délai d'attente maximal en millisecondes avant d'abandonner une tentative de lecture.
 * Lors d'un appel de :arduino:`Serial.read <functions/communication/serial/read/>`
 * ou d'une fonction
 * similaire, l'activité du micro-contrôleur est bloquée jusqu'à ce que la
 * lecture soit complétée. Pour éviter d'attendre excessivement face à une
 * ligne série vide, on règle un temps d'attente maximal permettant
 * la communication, met ne limitant pas significativement notre fréquence
 * d'échantillonage. Voir :arduino:`Serial.setTimeout <functions/communication/serial/setTimeout/>`
 * pour plus de détails.
 *
 * Pour un débit autour proche de 100kHz, on peut raisonnablement ne laisser un temps d'attente
 * que de seulement 1ms. On ne pourrait pas descendre aussi bas que 1µs, à cause des codes
 * de détection et correction d'erreur, et l'encodage, utilisés dans la communication. Chaque lettre
 * représente au moins 1 octet, et généralement un peu plus.
 */
#define DELAI 1 // Le temps d'attente

/** Le nombre de broches utilisées dans votre programme.
 * Si vous voulez mesurer les valeurs de plus de diodes,
 * Augmentez la valeur de :c:macro:`N_broches` et ajoutez des valeurs
 * aux listes :cpp:var:`broche` et :cpp:var:`mesure` en conséquence.
 * 
 * Si la fréquence d'échantillonage est un enjeux, il sera important de
 * minimiser le nombre de broches utilisées, parce que chaque lecture prend
 * du temps. Suivre l'état de 2 broches prend plus de temps que d'en suivre
 * une seule.
 */
#define N_broches 2

/** Liste pour les broches de lecture.
 * La liste doit avoir :c:macro:`N_broches` pour que le programme fonctionne bien.
 * Les macros utilisées correspondent à des définitions implicites qui dépendent du
 * modèle de Arduino. Pour le :arduinocard:`Arduino Nano Every <nano-every/>`, en
 * comptant en sens horaire à partir du connecteur µUSB, les broches :c:macro:`A0` à
 * :c:macro:`A7` correspondent à la 4e jusqu'à la 7e broches.
 *
 * Le type :cpp:type:`unsigned char` est équivalent à :cpp:type:`byte`, c'est à dire
 * un nombre entier positif représenté sur 1 octet, donc entre 0 et 255 inclusivement.
 * Comme on n'a que 8 broches analogiques, on n'a définitivement pas besoin de plus grand.
 */
const unsigned char broche[N_broches] = {A0, A1};

/** Liste pour les valeurs des lectures analogiques.
 * L'indice auquel se trouve une valeur correspond
 * à l'indice auquel se trouve la broche dans :c:var:`broche`. Elle
 * aussi doit avoir exactement :c:macro:`N_broches` éléments.
 *
 * Le type :cpp:type:`unsigned int` correspond à un nombre entier positif sur 2 octets.
 * On a donc une plage de 0 à 4096. Le convertisseur analogique-à-numérique du Arduino
 * utilise typiquement 10 bits, et donc n'utilisera que la plage de 0 à 1024.
 */
unsigned int mesure[N_broches] = {0, 0};

/** Initialisation du port série à :c:macro:`DEBIT` bits par seconde
 * et un timeout de :c:macro:`DELAI`. La fonction :cpp:func:`setup` s'exécute une
 * seule fois au démarrage du Arduino.
 */
void setup() {
	Serial.begin(DEBIT);
	Serial.setTimeout(DELAI);
	delay(DELAI); // Donner le temps à la ligne série de se vider
}

/** Lecture des données et envoi à l'ordinateur.
 * La fonction :c:func:`loop` est exécutée à répétition
 * après que la fonction :c:func:`setup` soit complétée.
 * 
 * Ici, la fonction est divisée en deux blocs:
 * 
 * #. Une boucle qui met à jour les valeurs dans
 *    :cpp:var:`broches` avec la fonction
 *    :arduino:`analogRead <functions/analog-io/analogRead/>`.
 * #. Et un bloc conditionnel qui 
 */
void loop() {
	for (int i=0; i < N_broches; i++) {
		mesure[i] = analogRead(broche[i]);
	}
	
	/** Serial.available retourne le nombre d'octets (max. 64o) disponibles
	 * dans le tampon du micro-contrôleur. Si la fonction retourne 0,
	 * le bloc conditionnel sera ignoré.
	 */
	if ( Serial.available() > 0 ) {
		/** :c:var:`cmd` contient une instruction d'1 octet envoyé
		 * par un programme client via la communication série.
		 */
		int cmd = Serial.read(); // Lire 1 octet
		
		if ( cmd < N_broches && cmd > -1 ) {
			Serial.println(mesure[cmd], DEC);
		}
	}
}

