#include "Cereal.h"

EchoSerie com;

void setup() {
  com = EchoSerie();
  com.setup();
}

void loop() {
  com.loop();
}
