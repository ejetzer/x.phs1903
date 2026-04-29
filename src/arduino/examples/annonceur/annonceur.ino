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

/**
 * Programme qui fait l'acquisition de signaux de tension
 * électrique reçus par deux photodiodes (visible et infrarouge) et envoie
 * le signal converti sur le port série, afin qu'il soit traité par un code
 * Python sur un ordinateur.
 */

#include <xphs1903.h>

/**
 * Définitions préliminaires
 * ---------------------------
 *
 * L'instruction de pré-compilation ``#define`` permet de définir des
 * valeurs nommées, comme des variables, mais sans utiliser de bloc mémoire.
 *
 * .. code-block:: cpp
 * 		#define <nom> <valeur>
 *
 */

/**
 * Paramètres de la communication série.
 * Un débit plus lent interfère avec les mesures
 * et un débit plus rapide fait chauffer le micro-contrôleur
 */
#define DEBIT 1000000 // baud (≅bit/s)

#define DELAI                                                                 \
  2 /** µs Le temps d'attente en lecture, compter 20µs/octet à 115200 */

/**
 * Si vous voulez mesurer les valeurs de plus de diodes,
 * Augmentez la valeur de :c:var:`N_broches` et ajoutez des valeurs
 * aux listes en conséquence.
 */
#define N_broches 2

/** Nombre de mesures, dépend de :c:var:`N_broches` et de la mémoire disponible
 */
#define M_mesures 400

/** Liste pour les broches de lecture */
const uint8_t broche[N_broches] = { A1, A2 };

/** Liste pour les lectures analogiques */
uint32_t mesure[N_broches + 1][M_mesures];

/** Initialisation du port série à 115200 bits par seconde et un timeout de
 * :c:macro:DELAI */
void
setup ()
{
  // Initialisation du port série
  Serial.begin (DEBIT);
  Serial.setTimeout (DELAI);
  Serial.println ();

  set_PF (2); /** Réglage du pré-facteur */
}

uint16_t j = 0;

void
loop ()
{
  mesure[0][j] = micros ();
  for (uint8_t i = 0; i < N_broches; i++)
    {
      /* Lecture des données des ports de conversion analogiques */
      mesure[i + 1][j] = analogRead (broche[i]);
    }

  j++;

  /*
   * :c:func:`Serial.available` retourne le nombre d'octets (max. 64o)
   * disponibles dans le tampon du micro-contrôleur. Si la fonction retourne 0,
   * le bloc conditionnel sera ignoré.
   */
  if (j == M_mesures)
    {
      // Envoyer toutes les données récoltées d'un coup
      for (int m = 0; m < M_mesures; m++)
        {
          Serial.print (mesure[0][m]);
          for (int n = 1; n <= N_broches; n++)
            {
              Serial.print ("\t");
              Serial.print (mesure[n][m]);
            }
          Serial.println ();
        }
      j = 0;
    }
}
