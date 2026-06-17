# Robot GUI Routine Guide

This guide explains how to use the robot GUI to create a routine, save it to a file, open it later, and replay it.

## What Is a Routine?

A routine is a list of saved robot arm positions.

Each time you click **Record Position**, the GUI saves the current positions of all five servo sliders. When you click **Replay Positions**, the robot moves through those saved positions in order.

The GUI records important steps, not a continuous video of the movement. Think of each recorded position as one checkpoint in the robot's motion.

Example routine:

1. Move toward the cup.
2. Lower the claw around the cup.
3. Close the claw.
4. Lift the cup.
5. Rotate toward the bin.
6. Lower the cup.
7. Open the claw to drop the cup.
8. Return to the starting position.

## Start the GUI

Open PowerShell in the project folder:

```powershell
cd C:\python_apps\robot_arm
```

Activate the virtual environment:

```powershell
. .\.venv\Scripts\Activate.ps1
```

Run the GUI:

```powershell
python.exe robot_gui.py
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

## Test the Routine

Click **Replay Positions**.

The robot will move through each recorded position one time, from the first saved position to the last saved position.

If the movement is not correct:

1. Click **Clear Last Position** to remove only the newest recorded position.
2. Click **Clear All Positions** to remove the entire routine and start over.
3. Adjust the sliders.
4. Record the corrected positions.
5. Test again with **Replay Positions**.

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

1. Start the GUI.
2. Connect to the Arduino by typing the COM port and clicking **Enter**.
3. Go to **File > Open File**.
4. Select the saved `.txt` routine file.
5. Click **Open**.

The saved positions are now loaded into the GUI.

## Play a Loaded Routine

After opening the saved routine file:

1. Click **Replay Positions**.
2. Wait for the robot to finish moving through the routine.

The routine plays one time.

## Repeating a Routine

The current GUI does not automatically loop a routine.

If you want the robot to repeat the same routine, wait until the routine finishes, then click **Replay Positions** again.

Each click of **Replay Positions** runs the loaded routine one time.

## Suggested Routine File Names

Use names that describe what the robot does:

```text
cup_pickup_to_bin.txt
block_stack.txt
open_close_claw_test.txt
left_bin_drop.txt
right_bin_drop.txt
```

Clear file names make it easier to find and reuse routines later.

## Quick Checklist

To create and save a routine:

1. Connect to Arduino.
2. Move sliders to first important position.
3. Click **Record Position**.
4. Repeat for each important position.
5. Click **Replay Positions** to test.
6. Go to **File > Save File**.

To load and play a routine:

1. Connect to Arduino.
2. Go to **File > Open File**.
3. Select the saved routine file.
4. Click **Replay Positions**.
5. Click **Replay Positions** again if you want to run it another time.
