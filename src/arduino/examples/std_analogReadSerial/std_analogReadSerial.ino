uint32_t etampe;
uint32_t delai;

void setup() {
  Serial.begin(9600);
  while (!Serial);
  pinMode(A0, INPUT_PULLUP);
  delai = 1000;
  etampe = 0;
}

void loop() {
  if ( (millis() - etampe) > delai ) {
    Serial.println(analogRead(A0));
  }
}