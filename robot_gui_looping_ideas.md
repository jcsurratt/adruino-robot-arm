# Ideas for Looping a Saved Robot Routine

This guide explains how a saved robot routine could be automated so it repeats over and over.

The current robot GUI does not automatically loop routines. It plays a loaded or recorded routine one time each time the user clicks **Replay Positions**.

This guide is only an idea guide. It does not change the current program.

## Current Behavior

The current GUI works like this:

1. Start the GUI.
2. Connect to the Arduino COM port.
3. Open a saved `.txt` routine file.
4. Click **Replay Positions**.
5. The robot plays the routine one time.
6. To run it again, click **Replay Positions** again.

The `.txt` file stores the servo positions for the routine. It does not tell the robot whether to repeat. Looping would need to be controlled by the Python GUI.

## What Looping Would Mean

Looping means the GUI would keep replaying the saved positions until the user tells it to stop.

Example:

```text
play routine
wait
play routine again
wait
play routine again
wait
stop when requested
```

For a cup pickup routine, that could mean:

1. Move to cup.
2. Close claw on cup.
3. Lift cup.
4. Rotate to bin.
5. Lower cup.
6. Open claw.
7. Return to start.
8. Repeat the same routine again.

## Safety Warning

Looping a robot arm can be risky if the workspace changes.

Before looping:

1. Make sure the robot is stable.
2. Make sure the cup, bin, and table are positioned correctly.
3. Make sure no hands, wires, or loose objects are in the robot's path.
4. Test the routine one time before looping it.
5. Be ready to stop the robot or disconnect power if something goes wrong.

Even a routine that works once can miss the object on the next loop if the cup or robot arm shifts.

## Feature Idea

A simple loop feature could add:

1. A **Loop Routine** button.
2. A **Stop Loop** button.
3. A variable that remembers whether looping is turned on.
4. A short delay between each repeat.

The basic idea:

```text
When Loop Routine is clicked:
    turn looping on
    replay the saved positions
    if looping is still on, replay them again

When Stop Loop is clicked:
    turn looping off
```

## Sample Python Idea

This is sample code showing the idea. It is not currently part of the robot GUI.

```python
looping = False


def start_loop():
    global looping
    looping = True
    loop_positions()


def stop_loop():
    global looping
    looping = False


def loop_positions():
    if not looping:
        return

    for position in saved_positions:
        if not looping:
            return

        print("looping: " + str(position))
        send_positions(position)
        time.sleep(REPLAY_DELAY_SECONDS)

    if looping:
        window.after(2000, loop_positions)
```

In this example:

- `looping = False` means the loop starts turned off.
- `start_loop()` turns looping on.
- `stop_loop()` turns looping off.
- `loop_positions()` replays the saved routine.
- `window.after(2000, loop_positions)` waits 2 seconds, then starts the routine again.

The number `2000` means 2000 milliseconds, or 2 seconds.

## Example Buttons

A future version of the GUI could add two buttons like this:

```python
loop_button = Button(window, text="Loop Routine", command=start_loop)
loop_button.place(x=10, y=255)

stop_loop_button = Button(window, text="Stop Loop", command=stop_loop)
stop_loop_button.place(x=10, y=285)
```

These buttons would let the user start and stop the repeated routine from the GUI.

## Why Use window.after Instead of a Forever Loop?

Tkinter GUIs need time to update the window and respond to button clicks.

A normal forever loop like this can cause problems:

```python
while looping:
    play_positions()
```

That kind of loop may make the GUI freeze, which means the **Stop Loop** button might not respond.

Using `window.after(...)` is better because it gives Tkinter time to handle button clicks and window updates.

## Possible User Workflow

If a loop feature were added, the user workflow might be:

1. Start the GUI.
2. Connect to the Arduino.
3. Go to **File > Open File**.
4. Select a saved routine, such as `cup_pickup_to_bin.txt`.
5. Click **Replay Positions** once to test the routine.
6. If the test works, click **Loop Routine**.
7. Let the robot repeat the routine.
8. Click **Stop Loop** when finished.

## Manual Repeating With the Current GUI

Without changing the program, the current way to repeat a routine is manual:

1. Open the saved routine file.
2. Click **Replay Positions**.
3. Wait for the routine to finish.
4. Click **Replay Positions** again.

Each click runs the routine one time.

## Summary

The current GUI can save and replay routines, but it does not automatically loop them.

To make routines loop automatically, the GUI would need a new loop feature. A good loop feature should include both a start button and a stop button so the user can safely control the repeated motion.
