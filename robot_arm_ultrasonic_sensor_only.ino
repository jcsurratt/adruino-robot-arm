#include <Servo.h>


// ============================================================
// STUDENT / TEACHER SETTINGS
// These are the main values students may need to change.
// ============================================================

// This must match BAUD_RATE in robot_gui_ultrasonic_trigger.py.
const int BAUD_RATE = 9600;

// These are the Arduino pins connected to each servo signal wire.
const int SERVO_1_PIN = 3;
const int SERVO_2_PIN = 5;
const int SERVO_3_PIN = 6;
const int SERVO_4_PIN = 9;
const int SERVO_5_PIN = 10;

// Ultrasonic sensor pins.
// HC-SR04 wiring: VCC to 5V, GND to GND, TRIG to TRIG_PIN, ECHO to ECHO_PIN.
const int TRIG_PIN = 11;
const int ECHO_PIN = 12;

// Detection range in centimeters.
// The Arduino reports OBJECT_DETECTED only when something is inside this range.
const int MIN_OBJECT_DISTANCE_CM = 4;
const int MAX_OBJECT_DISTANCE_CM = 35;

// A reading farther than this means the table area is clear again.
// Make this a little bigger than MAX_OBJECT_DISTANCE_CM to prevent flicker.
const int CLEAR_DISTANCE_CM = 45;

// Require several matching readings before changing states.
const int STABLE_READING_COUNT = 3;

// How often the ultrasonic sensor is checked.
const unsigned long SENSOR_CHECK_INTERVAL_MS = 100;

// Set to true if you want to see distance readings in Python's console.
const bool SEND_DISTANCE_DEBUG = false;


// ============================================================
// SERVO SETUP
// ============================================================

Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;
Servo servo5;

int servoPositions[5] = {90, 90, 90, 90, 90};


// ============================================================
// SENSOR STATE
// ============================================================

bool objectDetected = false;
int detectedReadingCount = 0;
int clearReadingCount = 0;
unsigned long lastSensorCheck = 0;


void setup() {
  Serial.begin(BAUD_RATE);
  Serial.setTimeout(20);

  servo1.attach(SERVO_1_PIN);
  servo2.attach(SERVO_2_PIN);
  servo3.attach(SERVO_3_PIN);
  servo4.attach(SERVO_4_PIN);
  servo5.attach(SERVO_5_PIN);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  writeServos();
  Serial.println("CLEAR");
}


void loop() {
  readServoCommandFromPython();
  checkUltrasonicSensor();
  writeServos();
}


void readServoCommandFromPython() {
  while (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    // Python sends five 3-digit numbers stuck together.
    // Example: "090045120010180"
    if (input.length() != 15) {
      continue;
    }

    servoPositions[0] = constrain(input.substring(0, 3).toInt(), 0, 180);
    servoPositions[1] = constrain(input.substring(3, 6).toInt(), 0, 180);
    servoPositions[2] = constrain(input.substring(6, 9).toInt(), 0, 180);
    servoPositions[3] = constrain(input.substring(9, 12).toInt(), 0, 180);
    servoPositions[4] = constrain(input.substring(12, 15).toInt(), 0, 180);
  }
}


void writeServos() {
  servo1.write(servoPositions[0]);
  servo2.write(servoPositions[1]);
  servo3.write(servoPositions[2]);
  servo4.write(servoPositions[3]);
  servo5.write(servoPositions[4]);
}


void checkUltrasonicSensor() {
  unsigned long now = millis();

  if (now - lastSensorCheck < SENSOR_CHECK_INTERVAL_MS) {
    return;
  }

  lastSensorCheck = now;
  int distanceCm = readDistanceCm();

  if (SEND_DISTANCE_DEBUG && distanceCm > 0) {
    Serial.print("DISTANCE:");
    Serial.println(distanceCm);
  }

  bool inObjectRange = distanceCm >= MIN_OBJECT_DISTANCE_CM && distanceCm <= MAX_OBJECT_DISTANCE_CM;
  bool inClearRange = distanceCm <= 0 || distanceCm >= CLEAR_DISTANCE_CM;

  if (!objectDetected) {
    if (inObjectRange) {
      detectedReadingCount++;
    } else {
      detectedReadingCount = 0;
    }

    if (detectedReadingCount >= STABLE_READING_COUNT) {
      objectDetected = true;
      clearReadingCount = 0;
      Serial.print("OBJECT_DETECTED:");
      Serial.println(distanceCm);
    }

    return;
  }

  if (inClearRange) {
    clearReadingCount++;
  } else {
    clearReadingCount = 0;
  }

  if (clearReadingCount >= STABLE_READING_COUNT) {
    objectDetected = false;
    detectedReadingCount = 0;
    Serial.print("CLEAR:");
    Serial.println(distanceCm);
  }
}


int readDistanceCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Timeout after about 4 meters. A timeout returns 0.
  unsigned long duration = pulseIn(ECHO_PIN, HIGH, 24000);

  if (duration == 0) {
    return 0;
  }

  return duration / 58;
}
