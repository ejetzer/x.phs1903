#define BUFLEN 2
uint8_t buffer[BUFLEN];
uint8_t pos = 0;
uint8_t dispo = 0;
uint8_t len = 0;

void setup() {
  Serial.begin(115200);
}

void loop() {
  dispo = Serial.available();
  if ( dispo > 0 ) {
    len = (BUFLEN > dispo)? dispo:BUFLEN;
    pos += Serial.readBytes(buffer, len);
  }
  
  dispo = Serial.availableForWrite();
  if ( dispo > 0 && pos > 0 ) {
    len = (pos > dispo)? dispo:pos;
    len = (BUFLEN > len)? len:BUFLEN;
    pos -= Serial.write(buffer, len);
  }
}