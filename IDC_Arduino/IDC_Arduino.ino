#include <DHT.h>
#include "CytronMotorDriver.h"

// Constants for DHT sensor
#define DHTPIN 12      // Pin to activate DHT22 sensor
#define DHTTYPE DHT22  // DHT 22 (AM2302)

// Constants for motor driver
#define PWM_LEFT 3
#define PWM_RIGHT 10
#define DIR_LEFT 9
#define DIR_RIGHT 11

#define BUTTON 2
#define PIEZO 8
#define IR_LEFT A1
#define IR_RIGHT A2

#define NOTE_G4 392
#define NOTE_C5 523
#define NOTE_G5 784
#define NOTE_C6 1047
#define MOTOR_PIN 6

// DHT sensor instance
DHT dht(DHTPIN, DHTTYPE);

// Motor driver instances
CytronMD motor1(PWM_PWM, PWM_LEFT, DIR_LEFT);    // Motor 1 pins configuration
CytronMD motor2(PWM_PWM, PWM_RIGHT, DIR_RIGHT);  // Motor 2 pins configuration

// Melodies for start and stop
int startMelody[] = {NOTE_G5, NOTE_C6};
int startNoteDurations[] = {12, 8};

int stopMelody[] = {NOTE_C6, NOTE_G5};
int stopNoteDurations[] = {12, 8};

#define playStartMelody() playMelody(startMelody, startNoteDurations, 2)
#define playStopMelody() playMelody(stopMelody, stopNoteDurations, 2)

void setup() {
  pinMode(BUTTON, INPUT_PULLUP);
  pinMode(PIEZO, OUTPUT);
  pinMode(IR_LEFT, INPUT);
  pinMode(IR_RIGHT, INPUT);
  pinMode(DHTPIN, OUTPUT);
  //  pinMode(MOTOR_PIN, OUTPUT);
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  bool notdetected = true;
  if (digitalRead(BUTTON) == LOW) {
    playStartMelody();
    int leftvalue = 1000;
    int rightvalue = 200;
    Serial.println("Working...");
    while (notdetected) {
      Serial.println(analogRead(IR_LEFT));
      if (analogRead(IR_LEFT) <= leftvalue && analogRead(IR_RIGHT) <= rightvalue) {
        robotForward();
        Serial.println("Forward");
      } else if (analogRead(IR_LEFT) <= leftvalue && analogRead(IR_RIGHT) > rightvalue) {
        robotTurnRight();
        Serial.println("Right");
      } else if (analogRead(IR_LEFT) >= leftvalue && analogRead(IR_RIGHT) < rightvalue) {
        robotTurnLeft();
        Serial.println("Left");
      } else if (analogRead(IR_LEFT) > leftvalue && analogRead(IR_RIGHT) > rightvalue) {
          Serial.println("stop");
          robotStop();
          delay(10000);
          String command = Serial.readStringUntil('\n');
          if (command == "Take Temperature") {
          taketemp();
        }
        else if (command == "Fan to start running"){
          playStartMelody();
          OnMotor();
        }
        else if (command == "Nothing"){
          robotStop();
        }
        playStopMelody();
        robotTurnRight();
        delay(1000);
        robotStop();
      } 
    }
  }
}

void playMelody(int *melody, int *noteDurations, int notesLength) {
  pinMode(PIEZO, OUTPUT);
  for (int thisNote = 0; thisNote < notesLength; thisNote++) {
    int noteDuration = 1000 / noteDurations[thisNote];
    tone(PIEZO, melody[thisNote], noteDuration);
    int pauseBetweenNotes = noteDuration * 1.30;
    delay(pauseBetweenNotes);
    noTone(PIEZO);
  }
}
void taketemp(){
// Read temperature and humidity
  float hum = dht.readHumidity();
  float temp = dht.readTemperature();

  ```Serial.print("Humidity: ");
  Serial.print(hum);
  Serial.print(" %, Temp: ");
  Serial.print(temp);
  Serial.println(" Celsius");
  ```

}
void OnMotor() {
  Serial.println("Fire detected");
  digitalWrite(MOTOR_PIN, HIGH);
  delay(1000);
  digitalWrite(MOTOR_PIN, LOW);
  delay(1000);
}

void robotStop() {

  motor1.setSpeed(0);  // Motor 1 stops.
  motor2.setSpeed(0);  // Motor 2 stops.
}

void robotForward() {
  motor1.setSpeed(150);  // Motor 1 runs forward.
  motor2.setSpeed(150);  // Motor 2 runs forward.
}

void robotReverse() {
  motor1.setSpeed(-150);  // Motor 1 runs backward.
  motor2.setSpeed(-150);  // Motor 2 runs backward.
}

void robotTurnLeft() {
  motor1.setSpeed(-150);  // Motor 1 runs backward.
  motor2.setSpeed(150);   // Motor 2 runs forward.
}

void robotTurnRight() {
  motor1.setSpeed(150);   // Motor 1 runs forward.
  motor2.setSpeed(-150);  // Motor 2 runs backward.
}