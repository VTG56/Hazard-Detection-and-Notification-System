// --- Pin Definitions ---
const int soilPin = A0;             // Soil moisture (analog)
const int smokeSensorPin = A2;      // Smoke sensor (analog)
const int ldrAnalogPin = A7;        // LDR (analog)
const int flameDigitalPin = 2;      // Flame sensor (digital)
const int sensorPin = A4;     

// --- Variables ---
int soilValue = 0;
int smokeValue = 0;
int ldrValue = 0;
int flameDetected = 0;

void setup() {
  Serial.begin(9600);               // Start Serial Monitor
  pinMode(flameDigitalPin, INPUT);  // Set flame pin as input
}

void loop() {
  // Read sensor values
  soilValue = analogRead(soilPin);            // 0–1023
  smokeValue = analogRead(smokeSensorPin);    // 0–1023
  ldrValue = analogRead(ldrAnalogPin);        // 0–1023
  flameDetected = digitalRead(flameDigitalPin);
  int analogValue = analogRead(sensorPin);       // Read analog value (0 - 1023)
  float voltage = analogValue * (5.0 / 1023.0);   // Convert to voltage
  float temperatureC = voltage*100 ;   // 0 = flame, 1 = no flame

  // Send comma-separated values over serial (for Python to read)
  Serial.print(soilValue);
  Serial.print(",");
  Serial.print(smokeValue);
  Serial.print(",");
  Serial.print(ldrValue);
  Serial.print(",");
  Serial.print(temperatureC);
  Serial.print(",");
  Serial.println(flameDetected);
   // newline ends the data packet

  delay(2000);  // Read every 2 seconds
}
