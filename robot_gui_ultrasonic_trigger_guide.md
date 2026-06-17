# Robot GUI Ultrasonic Trigger Version Guide

This guide explains how to use `robot_gui_ultrasonic_trigger.py` with `robot_arm_ultrasonic_sensor_only.ino`.

In this version, the Arduino still receives servo positions from Python, but it also watches an ultrasonic sensor. When the Arduino sees an object, it sends a message such as:

```text
OBJECT_DETECTED:18
```

When the table area is clear again, it sends:

```text
CLEAR:0
```

Python decides when to run the robot routine. The Arduino does not choose or play the routine.

## Files

- `robot_arm_ultrasonic_sensor_only.ino` is the Arduino sketch.
- `robot_gui_ultrasonic_trigger.py` is the Python GUI.
- Saved `.txt` routine files still work the same way as the other GUI versions.

## Ultrasonic Sensor Wiring

For an HC-SR04 ultrasonic sensor:

```text
VCC  -> Arduino 5V
GND  -> Arduino GND
TRIG -> Arduino pin 11
ECHO -> Arduino pin 12
```

If you use different pins, change these lines in `robot_arm_ultrasonic_sensor_only.ino`:

```cpp
const int TRIG_PIN = 11;
const int ECHO_PIN = 12;
```

## Upload the Arduino Sketch

1. Open `robot_arm_ultrasonic_sensor_only.ino` in the Arduino IDE.
2. Select the correct board and COM port.
3. Upload the sketch.
4. Close the Arduino Serial Monitor before starting Python.

Only one program can use the Arduino COM port at a time.

## Start the Python GUI

Open PowerShell in the project folder:

```powershell
cd C:\python_apps\robot_arm
```

Activate the virtual environment:

```powershell
. .\.venv\Scripts\Activate.ps1
```

Run the ultrasonic trigger GUI:

```powershell
python.exe robot_gui_ultrasonic_trigger.py
```

## Basic Workflow

1. Type the Arduino COM port into the **Set Port** box.
2. Click **Enter**.
3. Record a new routine or open a saved routine file.
4. Click **Replay Positions** once to test the routine.
5. Click **Start Sensor Watch**.
6. Place an object in front of the ultrasonic sensor.
7. The robot plays the routine one time.
8. The robot returns to `HOME_POSITION`.
9. Remove the object so the Arduino sends `CLEAR`.
10. The Python GUI arms itself for the next object.

## How Re-Triggering Works

The Python GUI uses this pattern:

```text
wait for CLEAR
arm the trigger
wait for OBJECT_DETECTED
play routine once
return home
ignore more detections
wait for CLEAR again
arm the trigger again
```

This prevents the same cup from triggering the routine over and over while it is still sitting in front of the sensor.

## Adjust the Detection Distance

In `robot_arm_ultrasonic_sensor_only.ino`, this range controls what counts as an object:

```cpp
const int MIN_OBJECT_DISTANCE_CM = 4;
const int MAX_OBJECT_DISTANCE_CM = 35;
```

This line controls when the sensor area counts as clear again:

```cpp
const int CLEAR_DISTANCE_CM = 45;
```

Keep `CLEAR_DISTANCE_CM` a little larger than `MAX_OBJECT_DISTANCE_CM`. That gap helps prevent the sensor from flickering between detected and clear.

## Adjust the Home Position

In `robot_gui_ultrasonic_trigger.py`, change this list to match the arm's safe start position:

```python
HOME_POSITION = [90, 90, 90, 90, 90]
```

The robot returns to this position after each sensor-triggered routine.

## Safety Checklist

Before starting sensor watch:

1. Test the routine once with **Replay Positions**.
2. Make sure the robot can safely return home.
3. Make sure the ultrasonic sensor points at the object area, not the robot arm.
4. Keep hands and wires out of the robot path.
5. Be ready to click **Stop Motion** or disconnect power.

## Troubleshooting

If the robot never triggers:

1. Make sure the Arduino Serial Monitor is closed.
2. Check the COM port.
3. Move the object into the detection range.
4. Try increasing `MAX_OBJECT_DISTANCE_CM`.
5. Set `SEND_DISTANCE_DEBUG` to `true` in the Arduino sketch and watch the Python console.

If the robot triggers repeatedly:

1. Increase `CLEAR_DISTANCE_CM`.
2. Move the sensor so it does not see the robot arm.
3. Require more stable readings by increasing `STABLE_READING_COUNT`.

If the robot moves but the sensor does not work:

1. Check the ultrasonic sensor wiring.
2. Make sure TRIG and ECHO are not swapped.
3. Confirm that all grounds are connected together.
