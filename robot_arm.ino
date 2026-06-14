#include <Servo.h>


// ============================================================
// STUDENT / TEACHER SETTINGS
// These are the main values students may need to change.
// ============================================================

// This must match BAUD_RATE in robot_gui.py.
// Python and Arduino need to "talk" at the same speed.
const int BAUD_RATE = 9600;

// These are the Arduino pins connected to each servo signal wire.
// Change these numbers if you plug the servos into different pins.
const int SERVO_1_PIN = 3;
const int SERVO_2_PIN = 5;
const int SERVO_3_PIN = 6;
const int SERVO_4_PIN = 9;
const int SERVO_5_PIN = 10;


// Create five servo objects.
// Each object lets Arduino control one physical servo motor.
Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;
Servo servo5;

// This array stores the latest angle for each servo.
// Example: {90, 45, 120, 10, 180}
int servoPositions[5];


void setup() {
  // Start serial communication with the computer.
  // This speed must match the Python BAUD_RATE.
  Serial.begin(BAUD_RATE);

  // Tell Arduino which pin controls each servo.
  servo1.attach(SERVO_1_PIN);
  servo2.attach(SERVO_2_PIN);
  servo3.attach(SERVO_3_PIN);
  servo4.attach(SERVO_4_PIN);
  servo5.attach(SERVO_5_PIN);
}


void loop() {
  // Check whether Python has sent a new line of data over the USB cable.
  while (Serial.available()) {
    // Read one complete message from Python.
    // Python ends each message with '\n', which means "new line".
    String input = Serial.readStringUntil('\n');

    // Python sends five 3-digit numbers stuck together.
    // Example: "090045120010180"
    // Arduino splits that message back into five servo angles.
    servoPositions[0] = input.substring(0, 3).toInt();
    servoPositions[1] = input.substring(3, 6).toInt();
    servoPositions[2] = input.substring(6, 9).toInt();
    servoPositions[3] = input.substring(9, 12).toInt();
    servoPositions[4] = input.substring(12, 15).toInt();
  }

  // Move each servo to its latest angle.
  servo1.write(servoPositions[0]);
  servo2.write(servoPositions[1]);
  servo3.write(servoPositions[2]);
  servo4.write(servoPositions[3]);
  servo5.write(servoPositions[4]);

  // Wait a short time before checking again.
  delay(500);
}
