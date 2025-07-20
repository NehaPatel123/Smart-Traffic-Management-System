int redLight = 2;
int yellowLight = 3;
int greenLight = 4;
int buzzer = 5;  // Pin for buzzer

int greenDuration = 5000;  // Default durations in milliseconds
int yellowDuration = 2000;
int redDuration = 5000;

void setup() {
  Serial.begin(9600);
  pinMode(redLight, OUTPUT);
  pinMode(yellowLight, OUTPUT);
  pinMode(greenLight, OUTPUT);
  pinMode(buzzer, OUTPUT);
}

void loop() {
  // Check for duration or buzzer update from Python
  if (Serial.available() > 0) {
    String data = Serial.readString();
    if (data.startsWith("BUZZER:ON")) {
      digitalWrite(buzzer, HIGH);
      delay(2000);  // Buzzer on for 1 second
      digitalWrite(buzzer, LOW);
    } else {
      parseDurations(data);
    }
  }
  
  // Normal cycle based on current duration settings
  digitalWrite(greenLight, HIGH);
  delay(greenDuration);
  digitalWrite(greenLight, LOW);

  digitalWrite(yellowLight, HIGH);
  delay(yellowDuration);
  digitalWrite(yellowLight, LOW);

  digitalWrite(redLight, HIGH);
  delay(redDuration);
  digitalWrite(redLight, LOW);
}

// Function to parse and update durations from serial input
void parseDurations(String data) {
  int greenIndex = data.indexOf("GREEN:") + 6;
  int yellowIndex = data.indexOf("YELLOW:") + 7;
  int redIndex = data.indexOf("RED:") + 4;

  greenDuration = data.substring(greenIndex, yellowIndex - 7).toInt() * 1000;
  yellowDuration = data.substring(yellowIndex, redIndex - 4).toInt() * 1000;
  redDuration = data.substring(redIndex).toInt() * 1000;
}
