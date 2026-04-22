#include "journal.h"

using namespace phs;

char* texte_niveau(Niveau_t niveau) {
  switch (niveau) {
    case DEBUG:
      return "DÉBOGAGE";
    case INFO:
      return "INFO";
    case WARNING:
      return "ATTENTION";
    case ERROR:
      return "ERREUR";
    case CRITICAL:
      return "CRITIQUE";
    default:
      return "MESSAGE";
  }
}

void Journal::entrer(char* msg, Niveau_t niveau) {
  Serial.print(texte_niveau(niveau));
  Serial.print("::");
  Serial.print(millis());
  Serial.print("::");
  Serial.println(msg);
}

void Journal::debug(char* msg) {
  entrer(msg, DEBUG);
}

void Journal::info(char* msg) {
  entrer(msg, INFO);
}

void Journal::warn(char* msg) {
  entrer(msg, WARNING);
}

void Journal::error(char* msg) {
  entrer(msg, ERROR);
}

void Journal::crit(char* msg) {
  entrer(msg, CRITICAL);
}
