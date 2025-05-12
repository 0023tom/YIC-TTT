#define BUZZER_PIN 9

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'C') {
      tone(BUZZER_PIN, 1000, 500);  // Correct
    } else if (c == 'W') {
      tone(BUZZER_PIN, 300, 500);   // Wrong
    }
  }
}