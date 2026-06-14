from tkinter import *
from tkinter import filedialog
import serial
import time


# ============================================================
# STUDENT / TEACHER SETTINGS
# These are the main values students may need to change.
# ============================================================

# The Arduino sketch must use the same baud rate in Serial.begin(...).
# Example Arduino code: Serial.begin(9600);
BAUD_RATE = 9600

# Servo angles usually go from 0 to 180 degrees.
# Change these if your servo or robot arm needs a smaller safe range.
SERVO_MIN_ANGLE = 0
SERVO_MAX_ANGLE = 180

# This is how long Python waits after sending each position to the Arduino.
# If the robot arm moves too fast or misses commands, try a larger number.
SEND_DELAY_SECONDS = 0.2

# This is how long Python waits between saved positions during playback.
REPLAY_DELAY_SECONDS = 1

# The file window starts here when students open a saved movement file.
# "/" means the file picker starts near the top of the computer's folders.
STARTING_FILE_FOLDER = "/"

# The program asks the student to type the COM port in the window.
# On Windows, the COM port often looks like COM3, COM4, COM5, etc.
# Students can find it in Device Manager under "Ports (COM & LPT)".


# This starts as False because the program has not connected to the Arduino yet.
port_opened = False


def set_port():
    """Connect Python to the Arduino using the COM port typed by the student."""
    global port_opened, arduino

    # Read the COM port from the text box in the GUI.
    com_port = port_input.get()

    # Open a serial connection to the Arduino.
    # The baud rate must match the Arduino code.
    arduino = serial.Serial(com_port, BAUD_RATE)

    # Remember that the port is open so the main loop can start sending data.
    port_opened = True
    print("COM port set to: " + com_port)


def send_positions(position):
    """Send one full robot arm position to the Arduino."""

    # The Arduino expects one long message with five 3-digit numbers.
    # Example: [90, 5, 180, 45, 0] becomes "090005180045000"
    # The "\n" at the end tells the Arduino that the message is finished.
    message = "{0:0=3d}".format(position[0]) + "{0:0=3d}".format(position[1]) + "{0:0=3d}".format(
        position[2]) + "{0:0=3d}".format(position[3]) + "{0:0=3d}".format(position[4]) + "\n"

    # Convert the message into bytes and send it through the USB cable.
    arduino.write(str.encode(message))

    # Print the message so students can see what Python is sending.
    print(message, end='')

    # Give the Arduino and servos a short moment to react.
    time.sleep(SEND_DELAY_SECONDS)


# This list stores recorded robot arm positions.
# Each saved position contains five numbers, one for each servo.
saved_positions = []


def save_positions():
    """Record the current slider values as one saved robot arm position."""

    # Read all five sliders and save their values together.
    saved_positions.append([servo1_slider.get(), servo2_slider.get(
    ), servo3_slider.get(), servo4_slider.get(), servo5_slider.get()])
    print("saved positions: " + str(saved_positions))


def play_positions():
    """Replay all saved robot arm positions in order."""

    # Go through the saved list one position at a time.
    for position in saved_positions:
        print("playing: " + str(position))
        send_positions(position)
        time.sleep(REPLAY_DELAY_SECONDS)


def clear_all_positions():
    """Delete every recorded position."""
    global saved_positions

    # Replace the saved list with a new empty list.
    saved_positions = []
    print("cleared all positions")


def clear_last_positions():
    """Delete only the most recently recorded position."""
    global saved_positions

    # Remove the last item from the saved list.
    removed = saved_positions.pop()
    print("removed: " + str(removed))
    print("saved positions: " + str(saved_positions))


def open_file():
    """Open a previously saved list of robot arm positions."""
    global saved_positions

    # Ask the student to choose a text file.
    filename = filedialog.askopenfilename(
        initialdir=STARTING_FILE_FOLDER, title="Select a File", filetypes=(("Text files", "*.txt*"), ("all files", "*.*")))

    # Read the saved text file.
    file = open(filename, "r")
    data = file.read()

    # Turn the text back into a Python list.
    # Only open files that were saved by this program.
    saved_positions = eval(data)

    file.close()
    print("opened: " + filename)


def save_file():
    """Save the recorded robot arm positions to a text file."""

    # Ask the student where to save the file.
    save_file = filedialog.asksaveasfile(mode='w', defaultextension=".txt")

    # Save the Python list as text.
    save_file.write(str(saved_positions))
    save_file.close()
    print("saved file")


def instructions():
    """Print student instructions in the console."""
    print("1.) Set the Arduino's COM port and click Enter. This can be found in Device Manager in Windows")
    print("2.) Move the arm's servos using the sliders")
    print("3.) To record a position, click on Record Position")
    print("4.) To replay the recorded positions, click on Replay Positions")
    print("\nTo save what you've recorded, got to File > Save File.")
    print("To open a previously saved file, got to File > Open File.")


# ============================================================
# BUILD THE WINDOW
# This section creates the buttons, sliders, labels, and menus.
# ============================================================

window = Tk()
window.title("Robot Arm Controller 2")
window.minsize(355, 300)

# Text box and button for the Arduino COM port.
port_label = Label(window, text="Set Port:")
port_label.place(x=10, y=10)
port_input = Entry(window)
port_input.place(x=10, y=35)
port_button = Button(window, text="Enter", command=set_port)
port_button.place(x=135, y=32)

# Servo 1 slider.
servo1_slider = Scale(window, from_=SERVO_MAX_ANGLE, to=SERVO_MIN_ANGLE)
servo1_slider.place(x=0, y=100)
servo1_label = Label(window, text="Servo 1")
servo1_label.place(x=10, y=80)

# Servo 2 slider.
servo2_slider = Scale(window, from_=SERVO_MAX_ANGLE, to=SERVO_MIN_ANGLE)
servo2_slider.place(x=70, y=100)
servo2_label = Label(window, text="Servo 2")
servo2_label.place(x=80, y=80)

# Servo 3 slider.
servo3_slider = Scale(window, from_=SERVO_MAX_ANGLE, to=SERVO_MIN_ANGLE)
servo3_slider.place(x=140, y=100)
servo3_label = Label(window, text="Servo 3")
servo3_label.place(x=150, y=80)

# Servo 4 slider.
servo4_slider = Scale(window, from_=SERVO_MAX_ANGLE, to=SERVO_MIN_ANGLE)
servo4_slider.place(x=210, y=100)
servo4_label = Label(window, text="Servo 4")
servo4_label.place(x=220, y=80)

# Servo 5 slider.
servo5_slider = Scale(window, from_=SERVO_MAX_ANGLE, to=SERVO_MIN_ANGLE)
servo5_slider.place(x=280, y=100)
servo5_label = Label(window, text="Servo 5")
servo5_label.place(x=290, y=80)

# Button that records the current slider positions.
save_button = Button(window, text="Record Position", command=save_positions)
save_button.place(x=10, y=220)

# Button that removes the newest recorded position.
clear_button = Button(window, text="Clear Last Position",
                      command=clear_last_positions)
clear_button.place(x=120, y=220)

# Button that removes every recorded position.
clear_button = Button(window, text="Clear All Positions",
                      command=clear_all_positions)
clear_button.place(x=120, y=255)

# Button that replays recorded positions.
play_button = Button(window, text="Replay Positions",
                     command=play_positions, height=3)
play_button.place(x=250, y=220)

# File menu for opening and saving movement files.
menubar = Menu(window)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Open File", command=open_file)
filemenu.add_command(label="Save File", command=save_file)
menubar.add_cascade(label="File", menu=filemenu)

# Edit menu for clearing recorded positions.
editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Clear last position", command=clear_last_positions)
editmenu.add_command(label="Clear all positions", command=clear_all_positions)
menubar.add_cascade(label="Edit", menu=editmenu)

# Help menu that prints instructions in the console.
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(
    label="How to use (printed in console)", command=instructions)
menubar.add_cascade(label="Help", menu=helpmenu)

window.config(menu=menubar)


# ============================================================
# MAIN PROGRAM LOOP
# This keeps the window alive and sends slider values to Arduino.
# ============================================================

while True:
    # Let tkinter check for button clicks, slider moves, and menu choices.
    window.update()

    # Only send servo positions after the Arduino COM port is connected.
    if (port_opened):
        send_positions([servo1_slider.get(), servo2_slider.get(
        ), servo3_slider.get(), servo4_slider.get(), servo5_slider.get()])
