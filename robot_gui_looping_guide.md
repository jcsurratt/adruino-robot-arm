# Robot GUI Looping Version Guide

This guide explains how to use `robot_gui_looping.py` to create routines, save them, load them, play them one time, and loop them automatically.

The looping version works like the original robot GUI, but it adds two important controls:

- **Loop Routine** repeats the saved routine automatically.
- **Stop Loop** stops the automatic repeating.

## What Is a Routine?

A routine is a list of saved robot arm positions.

Each time you click **Record Position**, the GUI saves the current positions of all five servo sliders. When you click **Replay Positions**, the robot moves through those saved positions in order one time.

When you click **Loop Routine**, the robot keeps replaying those saved positions until you click **Stop Loop**.

## Start the Looping GUI

Open PowerShell in the project folder:

```powershell
cd C:\python_apps\robot_arm
```

Activate the virtual environment:

```powershell
. .\.venv\Scripts\Activate.ps1
```

Run the looping GUI:

```powershell
python.exe robot_gui_looping.py
```

## Connect to the Arduino

1. Plug the Arduino into the computer.
2. Find the Arduino COM port, such as `COM3`, `COM4`, or `COM5`.
3. Type the COM port into the **Set Port** box.
4. Click **Enter**.

After the port is set, moving the sliders should move the robot arm.

## Make a New Routine

1. Move the servo sliders until the robot reaches the first important position.
2. Click **Record Position**.
3. Move the sliders until the robot reaches the next important position.
4. Click **Record Position** again.
5. Repeat this process until the full routine is recorded.

For a cup pickup routine, you might record positions like this:

1. Starting position with claw open.
2. Arm moved forward toward the cup.
3. Claw lowered around the cup.
4. Claw closed on the cup.
5. Arm lifted with the cup.
6. Base rotated toward the bin.
7. Arm lowered over the bin.
8. Claw opened to drop the cup.
9. Arm returned to the starting position.

## Test the Routine One Time

Click **Replay Positions**.

The robot will move through each recorded position one time, from the first saved position to the last saved position.

Always test a routine one time before using loop mode.

## Loop the Routine Automatically

After the routine works correctly one time:

1. Click **Loop Routine**.
2. The robot will play the saved routine.
3. When the routine finishes, the GUI waits briefly.
4. The GUI starts the same routine again.
5. The routine keeps repeating.

## Stop the Loop

To stop automatic repeating:

1. Click **Stop Loop**.
2. The loop will stop.

The robot may finish the current movement step before stopping.

## Save the Routine to a File

After the routine works:

1. Go to **File > Save File**.
2. Choose where to save the file.
3. Give the file a clear name, such as:

```text
cup_pickup_to_bin.txt
```

4. Click **Save**.

The file stores all of the recorded positions for that routine.

Important: the GUI does not automatically save while you record. You must use **File > Save File** before closing the GUI, or the recorded routine will be lost.

## Load a Saved Routine

To use a routine that was already saved:

1. Start `robot_gui_looping.py`.
2. Connect to the Arduino by typing the COM port and clicking **Enter**.
3. Go to **File > Open File**.
4. Select the saved `.txt` routine file.
5. Click **Open**.

The saved positions are now loaded into the GUI.

## Play a Loaded Routine One Time

After opening the saved routine file:

1. Click **Replay Positions**.
2. Wait for the robot to finish moving through the routine.

This plays the loaded routine one time.

## Loop a Loaded Routine

After opening the saved routine file:

1. Click **Replay Positions** once to test it.
2. If the test works, click **Loop Routine**.
3. Let the robot repeat the routine.
4. Click **Stop Loop** when finished.

## Fixing Mistakes While Recording

If the movement is not correct:

1. Click **Clear Last Position** to remove only the newest recorded position.
2. Click **Clear All Positions** to remove the entire routine and start over.
3. Adjust the sliders.
4. Record the corrected positions.
5. Test again with **Replay Positions**.

## Safety Checklist Before Looping

Before clicking **Loop Routine**:

1. Make sure the robot is stable.
2. Make sure the routine works one time with **Replay Positions**.
3. Make sure the cup, bin, and robot are lined up correctly.
4. Make sure no hands, wires, or loose objects are in the robot's path.
5. Be ready to click **Stop Loop**.

A routine that works once might not work forever if the object moves, the robot shifts, or the claw misses the object.

## Suggested Routine File Names

Use names that describe what the robot does:

```text
cup_pickup_to_bin.txt
block_stack_loop.txt
open_close_claw_test.txt
left_bin_drop.txt
right_bin_drop.txt
```

Clear file names make it easier to find and reuse routines later.

## Quick Checklist

To create, save, and loop a routine:

1. Start `robot_gui_looping.py`.
2. Connect to Arduino.
3. Move sliders to first important position.
4. Click **Record Position**.
5. Repeat for each important position.
6. Click **Replay Positions** to test once.
7. Go to **File > Save File**.
8. Click **Loop Routine** to repeat automatically.
9. Click **Stop Loop** when finished.

To load and loop a saved routine:

1. Start `robot_gui_looping.py`.
2. Connect to Arduino.
3. Go to **File > Open File**.
4. Select the saved routine file.
5. Click **Replay Positions** to test once.
6. Click **Loop Routine**.
7. Click **Stop Loop** when finished.
