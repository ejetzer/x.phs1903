#ifndef JOURNALISATION
#define JOURNALISATION

#include <ArduinoSTL.h>
#include <ctime>

enum Niveau_t {
  DEBUG,
  INFO,
  WARNING,
  ERROR,
  CRITICAL
};

char* texte_niveau(Niveau_t niveau);

class Journal {
public:
  void entrer(char* msg, Niveau_t niveau);
  void debug(char* msg);
  void warn(char* msg);
  void info(char* msg);
  void error(char* msg);
  void crit(char* msg);
};

#endif