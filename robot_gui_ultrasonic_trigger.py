from tkinter import *
from tkinter import filedialog
import ast
import serial


# ============================================================
# STUDENT / TEACHER SETTINGS
# These are the main values students may need to change.
# ============================================================

# The Arduino sketch must use the same baud rate in Serial.begin(...).
BAUD_RATE = 9600

# Servo angles usually go from 0 to 180 degrees.
SERVO_MIN_ANGLE = 0
SERVO_MAX_ANGLE = 180

# This is how long Python waits between saved positions during playback.
REPLAY_DELAY_SECONDS = 1

# This is the position sent after a sensor-triggered routine finishes.
# Adjust this to match the robot arm's safe starting position.
HOME_POSITION = [90, 90, 90, 90, 90]

# The file window starts here when students open a saved movement file.
STARTING_FILE_FOLDER = "/"

# This controls how often the GUI sends the live slider values to the Arduino.
LIVE_SEND_DELAY_SECONDS = 0.25

# This controls how often Python checks for sensor messages from Arduino.
SERIAL_POLL_DELAY_SECONDS = 0.1


port_opened = False
arduino = None

saved_positions = []

playing = False
current_play_index = 0

sensor_watch_enabled = False
sensor_armed = False
waiting_for_clear = True
last_sensor_message = "No sensor message yet."


def set_status(message):
    """Show a short message in the GUI and print it in the console."""
    status_label.config(text=message)
    print(message)


def set_sensor_status(message):
    """Show the newest ultrasonic sensor state."""
    sensor_status_label.config(text=message)
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


def set_sliders_to_position(position):
    """Move the GUI sliders to match a position."""
    servo1_slider.set(position[0])
    servo2_slider.set(position[1])
    servo3_slider.set(position[2])
    servo4_slider.set(position[3])
    servo5_slider.set(position[4])


def set_port():
    """Connect Python to the Arduino using the COM port typed by the student."""
    global port_opened, arduino, sensor_armed, waiting_for_clear, last_sensor_message

    com_port = port_input.get().strip()

    if not com_port:
        set_status("Type a COM port first, such as COM3.")
        return

    try:
        arduino = serial.Serial(com_port, BAUD_RATE, timeout=0)
        arduino.reset_input_buffer()
    except serial.SerialException as error:
        port_opened = False
        set_status("Could not open " + com_port + ": " + str(error))
        return

    port_opened = True
    sensor_armed = False
    waiting_for_clear = True
    last_sensor_message = "No sensor message yet."
    set_status("COM port set to: " + com_port)
    set_sensor_status("Waiting for CLEAR before arming sensor trigger.")
    send_positions(HOME_POSITION)
    set_sliders_to_position(HOME_POSITION)


def send_positions(position):
    """Send one full robot arm position to the Arduino."""
    if not port_opened or arduino is None:
        return

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
    if port_opened and not playing:
        send_positions(get_current_position())

    window.after(int(LIVE_SEND_DELAY_SECONDS * 1000), send_live_slider_position)


def poll_serial_messages():
    """Read sensor messages from Arduino without freezing the GUI."""
    if port_opened and arduino is not None:
        try:
            while arduino.in_waiting:
                raw_message = arduino.readline().decode("utf-8", errors="ignore").strip()
                if raw_message:
                    handle_arduino_message(raw_message)
        except serial.SerialException as error:
            set_status("Serial connection error: " + str(error))

    window.after(int(SERIAL_POLL_DELAY_SECONDS * 1000), poll_serial_messages)


def handle_arduino_message(message):
    """React to OBJECT_DETECTED and CLEAR messages from the Arduino."""
    global sensor_armed, waiting_for_clear, last_sensor_message

    last_sensor_message = message

    if message.startswith("DISTANCE:"):
        set_sensor_status(message)
        return

    if message.startswith("CLEAR"):
        waiting_for_clear = False
        sensor_armed = sensor_watch_enabled and not playing
        if sensor_watch_enabled:
            set_sensor_status("Sensor clear. Ready for the next object.")
        else:
            set_sensor_status("Sensor clear. Sensor watch is off.")
        return

    if message.startswith("OBJECT_DETECTED"):
        set_sensor_status(message)
        if sensor_watch_enabled and sensor_armed and not playing:
            start_sensor_routine()
        return

    print("Arduino:", message)


def save_positions():
    """Record the current slider values as one saved robot arm position."""
    saved_positions.append(get_current_position())
    set_status("Recorded position " + str(len(saved_positions)))
    print("saved positions: " + str(saved_positions))


def start_replay():
    """Replay all saved robot arm positions one time."""
    start_routine("Playing routine one time.")


def start_sensor_routine():
    """Run the saved routine one time because the ultrasonic sensor saw an object."""
    global sensor_armed, waiting_for_clear

    sensor_armed = False
    waiting_for_clear = True
    start_routine("Object detected. Playing routine once.")


def start_routine(message):
    """Begin routine playback if the robot is connected and a routine exists."""
    global playing, current_play_index

    if not saved_positions:
        set_status("No saved positions to replay.")
        return

    if not port_opened:
        set_status("Connect to the Arduino before replaying.")
        return

    playing = True
    current_play_index = 0
    set_status(message)
    play_next_position()


def play_next_position():
    """Send the next saved position, then schedule the next playback step."""
    global playing

    if not playing:
        return

    if current_play_index < len(saved_positions):
        play_current_position()
        return

    finish_routine()


def play_current_position():
    """Send the current routine step and schedule the following step."""
    global current_play_index

    position = saved_positions[current_play_index]
    print("playing: " + str(position))
    set_sliders_to_position(position)
    send_positions(position)
    current_play_index += 1
    window.after(int(REPLAY_DELAY_SECONDS * 1000), play_next_position)


def finish_routine():
    """Return home after playback and wait for the object area to clear."""
    global playing, sensor_armed, waiting_for_clear

    playing = False
    set_sliders_to_position(HOME_POSITION)
    send_positions(HOME_POSITION)

    if sensor_watch_enabled:
        set_status("Routine finished. Returned home.")
        arm_sensor_if_area_is_clear()
    else:
        sensor_armed = False
        waiting_for_clear = True
        set_status("Routine finished. Returned home.")


def arm_sensor_if_area_is_clear():
    """Arm the sensor now if Arduino's most recent state is already clear."""
    global sensor_armed, waiting_for_clear

    if last_sensor_message.startswith("CLEAR"):
        waiting_for_clear = False
        sensor_armed = True
        set_sensor_status("Sensor clear. Ready for the next object.")
    else:
        waiting_for_clear = True
        sensor_armed = False
        set_sensor_status("Waiting for object to be removed before re-arming.")


def start_sensor_watch():
    """Turn on sensor-triggered routine mode."""
    global sensor_watch_enabled, sensor_armed, waiting_for_clear

    if not port_opened:
        set_status("Connect to the Arduino before starting sensor watch.")
        return

    if not saved_positions:
        set_status("Open or record a routine before starting sensor watch.")
        return

    sensor_watch_enabled = True

    if last_sensor_message.startswith("CLEAR"):
        waiting_for_clear = False
        sensor_armed = not playing
        set_sensor_status("Sensor watch on. Ready for an object.")
    elif waiting_for_clear:
        sensor_armed = False
        set_sensor_status("Sensor watch on. Waiting for CLEAR before arming.")
    else:
        sensor_armed = not playing
        set_sensor_status("Sensor watch on. Ready for an object.")

    set_status("Sensor watch started.")


def stop_sensor_watch():
    """Turn off sensor-triggered routine mode."""
    global sensor_watch_enabled, sensor_armed

    sensor_watch_enabled = False
    sensor_armed = False
    set_status("Sensor watch stopped.")
    set_sensor_status("Sensor watch off. Last message: " + last_sensor_message)


def stop_motion():
    """Stop scheduled playback after the current step."""
    global playing, sensor_armed

    playing = False
    sensor_armed = False
    set_status("Routine stopped.")


def go_home():
    """Send the robot to the configured home position."""
    set_sliders_to_position(HOME_POSITION)
    send_positions(HOME_POSITION)
    set_status("Sent robot to home position.")


def clear_all_positions():
    """Delete every recorded position."""
    global saved_positions, playing, current_play_index

    saved_positions = []
    playing = False
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
    global saved_positions, playing, current_play_index

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
    print("1.) Upload robot_arm_ultrasonic_sensor_only.ino to the Arduino.")
    print("2.) Start this Python file and connect to the Arduino COM port.")
    print("3.) Record or open a saved robot routine.")
    print("4.) Click Replay Positions once to test the routine.")
    print("5.) Click Start Sensor Watch.")
    print("6.) Place an object in front of the ultrasonic sensor.")
    print("7.) The robot plays the routine once, returns home, then waits for CLEAR.")


# ============================================================
# BUILD THE WINDOW
# ============================================================

window = Tk()
window.title("Robot Arm Controller - Ultrasonic Trigger")
window.minsize(520, 390)

port_label = Label(window, text="Set Port:")
port_label.place(x=10, y=10)
port_input = Entry(window)
port_input.place(x=10, y=35)
port_button = Button(window, text="Enter", command=set_port)
port_button.place(x=135, y=32)

servo1_slider = Scale(window, from_=SERVO_MAX_ANGLE, to=SERVO_MIN_ANGLE)
servo1_slider.place(x=0, y=100)
servo1_label = Label(window, text="Servo 1")
servo1_label.place(x=10, y=80)

servo2_slider = Scale(window, from_=SERVO_MAX_ANGLE, to=SERVO_MIN_ANGLE)
servo2_slider.place(x=70, y=100)
servo2_label = Label(window, text="Servo 2")
servo2_label.place(x=80, y=80)

servo3_slider = Scale(window, from_=SERVO_MAX_ANGLE, to=SERVO_MIN_ANGLE)
servo3_slider.place(x=140, y=100)
servo3_label = Label(window, text="Servo 3")
servo3_label.place(x=150, y=80)

servo4_slider = Scale(window, from_=SERVO_MAX_ANGLE, to=SERVO_MIN_ANGLE)
servo4_slider.place(x=210, y=100)
servo4_label = Label(window, text="Servo 4")
servo4_label.place(x=220, y=80)

servo5_slider = Scale(window, from_=SERVO_MAX_ANGLE, to=SERVO_MIN_ANGLE)
servo5_slider.place(x=280, y=100)
servo5_label = Label(window, text="Servo 5")
servo5_label.place(x=290, y=80)

save_button = Button(window, text="Record Position", command=save_positions)
save_button.place(x=10, y=220)

clear_last_button = Button(window, text="Clear Last Position", command=clear_last_positions)
clear_last_button.place(x=120, y=220)

clear_all_button = Button(window, text="Clear All Positions", command=clear_all_positions)
clear_all_button.place(x=120, y=255)

play_button = Button(window, text="Replay Positions", command=start_replay, height=3)
play_button.place(x=250, y=220)

home_button = Button(window, text="Home", command=go_home)
home_button.place(x=380, y=220)

sensor_start_button = Button(window, text="Start Sensor Watch", command=start_sensor_watch)
sensor_start_button.place(x=10, y=295)

sensor_stop_button = Button(window, text="Stop Sensor Watch", command=stop_sensor_watch)
sensor_stop_button.place(x=145, y=295)

stop_button = Button(window, text="Stop Motion", command=stop_motion)
stop_button.place(x=285, y=295)

status_label = Label(window, text="Connect to the Arduino, then move the sliders.", anchor="w")
status_label.place(x=10, y=335)

sensor_status_label = Label(window, text="Sensor watch off.", anchor="w")
sensor_status_label.place(x=10, y=360)

menubar = Menu(window)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Open File", command=open_file)
filemenu.add_command(label="Save File", command=save_file)
menubar.add_cascade(label="File", menu=filemenu)

editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Clear last position", command=clear_last_positions)
editmenu.add_command(label="Clear all positions", command=clear_all_positions)
menubar.add_cascade(label="Edit", menu=editmenu)

routinemenu = Menu(menubar, tearoff=0)
routinemenu.add_command(label="Replay once", command=start_replay)
routinemenu.add_command(label="Go home", command=go_home)
routinemenu.add_command(label="Stop motion", command=stop_motion)
menubar.add_cascade(label="Routine", menu=routinemenu)

sensormenu = Menu(menubar, tearoff=0)
sensormenu.add_command(label="Start sensor watch", command=start_sensor_watch)
sensormenu.add_command(label="Stop sensor watch", command=stop_sensor_watch)
menubar.add_cascade(label="Sensor", menu=sensormenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="How to use (printed in console)", command=instructions)
menubar.add_cascade(label="Help", menu=helpmenu)

window.config(menu=menubar)


# ============================================================
# MAIN PROGRAM LOOP
# ============================================================

send_live_slider_position()
poll_serial_messages()
window.mainloop()
