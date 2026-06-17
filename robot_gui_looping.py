from tkinter import *
from tkinter import filedialog
import ast
import serial


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

# This is how long Python waits before starting the routine again in loop mode.
LOOP_DELAY_SECONDS = 2

# The file window starts here when students open a saved movement file.
# "/" means the file picker starts near the top of the computer's folders.
STARTING_FILE_FOLDER = "/"

# This controls how often the GUI sends the live slider values to the Arduino.
LIVE_SEND_DELAY_SECONDS = 0.25


# This starts as False because the program has not connected to the Arduino yet.
port_opened = False
arduino = None

# This list stores recorded robot arm positions.
# Each saved position contains five numbers, one for each servo.
saved_positions = []

# These variables control replay and loop mode.
playing = False
looping = False
current_play_index = 0


def set_status(message):
    """Show a short message in the GUI and print it in the console."""
    status_label.config(text=message)
    print(message)


def get_current_position():
    """Read all five sliders as one robot arm position."""
    return [
        servo1_slider.get(),
        servo2_slider.get(),
        servo3_slider.get(),
        servo4_slider.get(),
        servo5_slider.get(),
    ]


def set_port():
    """Connect Python to the Arduino using the COM port typed by the student."""
    global port_opened, arduino

    com_port = port_input.get().strip()

    if not com_port:
        set_status("Type a COM port first, such as COM3.")
        return

    try:
        arduino = serial.Serial(com_port, BAUD_RATE)
    except serial.SerialException as error:
        port_opened = False
        set_status("Could not open " + com_port + ": " + str(error))
        return

    port_opened = True
    set_status("COM port set to: " + com_port)


def send_positions(position):
    """Send one full robot arm position to the Arduino."""
    if not port_opened or arduino is None:
        return

    # The Arduino expects one long message with five 3-digit numbers.
    # Example: [90, 5, 180, 45, 0] becomes "090005180045000"
    # The "\n" at the end tells the Arduino that the message is finished.
    message = (
        "{0:0=3d}".format(position[0])
        + "{0:0=3d}".format(position[1])
        + "{0:0=3d}".format(position[2])
        + "{0:0=3d}".format(position[3])
        + "{0:0=3d}".format(position[4])
        + "\n"
    )

    arduino.write(str.encode(message))
    print(message, end="")


def send_live_slider_position():
    """Keep sending slider positions when the robot is not replaying a routine."""
    if port_opened and not playing and not looping:
        send_positions(get_current_position())

    window.after(int(LIVE_SEND_DELAY_SECONDS * 1000), send_live_slider_position)


def save_positions():
    """Record the current slider values as one saved robot arm position."""
    saved_positions.append(get_current_position())
    set_status("Recorded position " + str(len(saved_positions)))
    print("saved positions: " + str(saved_positions))


def start_replay():
    """Replay all saved robot arm positions one time."""
    global playing, looping, current_play_index

    if not saved_positions:
        set_status("No saved positions to replay.")
        return

    if not port_opened:
        set_status("Connect to the Arduino before replaying.")
        return

    looping = False
    playing = True
    current_play_index = 0
    set_status("Playing routine one time.")
    play_next_position()


def start_loop():
    """Keep replaying all saved robot arm positions until Stop Loop is clicked."""
    global playing, looping, current_play_index

    if not saved_positions:
        set_status("No saved positions to loop.")
        return

    if not port_opened:
        set_status("Connect to the Arduino before looping.")
        return

    looping = True
    playing = True
    current_play_index = 0
    set_status("Looping routine. Click Stop Loop to stop.")
    play_next_position()


def stop_loop():
    """Stop loop mode after the current movement step finishes."""
    global playing, looping

    looping = False
    playing = False
    set_status("Loop stopped.")


def play_next_position():
    """Send the next saved position, then schedule the next playback step."""
    global playing, current_play_index

    if not playing:
        return

    if current_play_index < len(saved_positions):
        position = saved_positions[current_play_index]
        print("playing: " + str(position))
        send_positions(position)
        current_play_index += 1
        window.after(int(REPLAY_DELAY_SECONDS * 1000), play_next_position)
        return

    if looping:
        current_play_index = 0
        set_status("Routine finished. Restarting loop soon.")
        window.after(int(LOOP_DELAY_SECONDS * 1000), play_next_position)
    else:
        playing = False
        set_status("Routine finished.")


def clear_all_positions():
    """Delete every recorded position."""
    global saved_positions, playing, looping, current_play_index

    saved_positions = []
    playing = False
    looping = False
    current_play_index = 0
    set_status("Cleared all positions.")


def clear_last_positions():
    """Delete only the most recently recorded position."""
    if not saved_positions:
        set_status("No saved positions to clear.")
        return

    removed = saved_positions.pop()
    set_status("Removed last position.")
    print("removed: " + str(removed))
    print("saved positions: " + str(saved_positions))


def open_file():
    """Open a previously saved list of robot arm positions."""
    global saved_positions, playing, looping, current_play_index

    filename = filedialog.askopenfilename(
        initialdir=STARTING_FILE_FOLDER,
        title="Select a File",
        filetypes=(("Text files", "*.txt*"), ("all files", "*.*")),
    )

    if not filename:
        set_status("Open file canceled.")
        return

    try:
        with open(filename, "r") as file:
            data = file.read()
        loaded_positions = ast.literal_eval(data)
    except (OSError, SyntaxError, ValueError) as error:
        set_status("Could not open routine file: " + str(error))
        return

    if not is_valid_position_list(loaded_positions):
        set_status("That file does not look like a robot routine.")
        return

    saved_positions = loaded_positions
    playing = False
    looping = False
    current_play_index = 0
    set_status("Opened " + filename)


def is_valid_position_list(positions):
    """Check that loaded routine data is a list of five-servo positions."""
    if not isinstance(positions, list):
        return False

    for position in positions:
        if not isinstance(position, list) or len(position) != 5:
            return False

        for angle in position:
            if not isinstance(angle, int):
                return False

            if angle < SERVO_MIN_ANGLE or angle > SERVO_MAX_ANGLE:
                return False

    return True


def save_file():
    """Save the recorded robot arm positions to a text file."""
    routine_file = filedialog.asksaveasfile(mode="w", defaultextension=".txt")

    if routine_file is None:
        set_status("Save file canceled.")
        return

    routine_file.write(str(saved_positions))
    routine_file.close()
    set_status("Saved routine file.")


def instructions():
    """Print student instructions in the console."""
    print("1.) Set the Arduino's COM port and click Enter. This can be found in Device Manager in Windows")
    print("2.) Move the arm's servos using the sliders")
    print("3.) To record a position, click on Record Position")
    print("4.) To replay the recorded positions once, click Replay Positions")
    print("5.) To repeat the routine automatically, click Loop Routine")
    print("6.) To stop automatic repeating, click Stop Loop")
    print("\nTo save what you've recorded, go to File > Save File.")
    print("To open a previously saved file, go to File > Open File.")


# ============================================================
# BUILD THE WINDOW
# This section creates the buttons, sliders, labels, and menus.
# ============================================================

window = Tk()
window.title("Robot Arm Controller - Looping")
window.minsize(430, 350)

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
clear_last_button = Button(window, text="Clear Last Position", command=clear_last_positions)
clear_last_button.place(x=120, y=220)

# Button that removes every recorded position.
clear_all_button = Button(window, text="Clear All Positions", command=clear_all_positions)
clear_all_button.place(x=120, y=255)

# Button that replays recorded positions one time.
play_button = Button(window, text="Replay Positions", command=start_replay, height=3)
play_button.place(x=250, y=220)

# Buttons that start and stop automatic looping.
loop_button = Button(window, text="Loop Routine", command=start_loop)
loop_button.place(x=10, y=255)

stop_loop_button = Button(window, text="Stop Loop", command=stop_loop)
stop_loop_button.place(x=10, y=290)

# Short status line for student feedback.
status_label = Label(window, text="Connect to the Arduino, then move the sliders.", anchor="w")
status_label.place(x=10, y=325)

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

# Routine menu for replaying or looping recorded positions.
routinemenu = Menu(menubar, tearoff=0)
routinemenu.add_command(label="Replay once", command=start_replay)
routinemenu.add_command(label="Loop routine", command=start_loop)
routinemenu.add_command(label="Stop loop", command=stop_loop)
menubar.add_cascade(label="Routine", menu=routinemenu)

# Help menu that prints instructions in the console.
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="How to use (printed in console)", command=instructions)
menubar.add_cascade(label="Help", menu=helpmenu)

window.config(menu=menubar)


# ============================================================
# MAIN PROGRAM LOOP
# Tkinter's mainloop keeps the window alive.
# window.after schedules live sending and routine playback.
# ============================================================

send_live_slider_position()
window.mainloop()
