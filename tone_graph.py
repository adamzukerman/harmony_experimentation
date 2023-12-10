import pyo
from tone import Tone
import pynput.keyboard as kb
import matplotlib.pyplot as plt
import time
import math
from circular_list import CircularList

# Setting up file-wide constants
# TODO Move this to a parameters file?
MOUSE_PRESSED = False
FRAME_RATE = 30
TRAIL_TIME = 5  # number of seconds to show of pitch history
PITCH_MAX = 4_000
A = 440
STARTING_FREQ_1 = 440
STARTING_FREQ_2 = 220
NOTES = [A * pow(2, i * 1 / 12) for i in range(40)] + [
    A * pow(2, i * -1 / 12) for i in range(1, 40)
]  # notes to snap to

# Directly derived from constants
frame_length = 1 / FRAME_RATE
freq_history = CircularList(TRAIL_TIME * FRAME_RATE)
freq_history.set_all_values(value=0)
dissonance_history = CircularList(TRAIL_TIME * FRAME_RATE)
dissonance_history.set_all_values(value=0)

# Setting up graph properties
plt.ion()
fig, (note_ax, dist_ax) = plt.subplots(2, 1)
note_ax.set_xlim(0, 2 * len(freq_history))  # have the note in middle of graph
note_ax.set_yscale("log")
note_ax.set_ylim(50, PITCH_MAX)
dist_ax.set_xlim(0, 2 * len(freq_history))  # have the note in middle of graph
dist_max = 0.1
dist_ax.set_ylim(0, dist_max)  # used for dissonance equation
note_x = len(freq_history)

# Setting up pyo objects
s = pyo.Server().boot()
s.start()
note1 = Tone(fund_freq=440, mul=0.4)
note1.set_random_overtones(15)
print("nummber of overtones for note1: ", len(note1._get_sines().items()))
note1.out()
note2 = Tone(fund_freq=220, mul=0.4)
note2.set_random_overtones(15)
note2.out()


def on_press(key):
    if key == kb.KeyCode.from_char("q"):
        global s
        s.stop()
        print("Terminating")
        return False
    elif key == kb.KeyCode.from_char("u"):
        note1.set_fund_freq(note1.get_fund_freq() * pow(2, 1 / 12))
    elif key == kb.KeyCode.from_char("U"):
        note1.set_fund_freq(note1.get_fund_freq() * pow(2, -1 / 12))
    elif key == kb.KeyCode.from_char("i"):
        note2.set_fund_freq(note2.get_fund_freq() * pow(2, 1 / 12))
    elif key == kb.KeyCode.from_char("I"):
        note2.set_fund_freq(note2.get_fund_freq() * pow(2, -1 / 12))
    elif key == kb.KeyCode.from_char("o"):
        print("Resetting overtones randomly")
        note1.set_random_overtones(15)
        note2.set_random_overtones(15)
    elif key == kb.Key.shift:
        pass
    elif key == kb.KeyCode.from_char("r"):
        note1.set_fund_freq(STARTING_FREQ_1)
        note2.set_fund_freq(STARTING_FREQ_2)
    elif key == kb.KeyCode.from_char("R"):
        return 1  # ignoring this section until bug is fixed. Reprioritizing
        closest_note1 = min(
            [abs(note1.get_fund_freq() - pitch) for pitch in notes]
        )  # BUG fix this
        closest_note2 = min([abs(note2.get_fund_freq() - pitch) for pitch in notes])
        note1.set_fund_freq(closest_note1)
        note2.set_fund_freq(closest_note2)
    else:
        print("key behavior undefined")


def on_mouse_press(event):
    if not event.ydata:
        return None
    y_pos = float(event.ydata)  # pyo can't handle numpy dtypes
    note1.set_fund_freq(float(y_pos))
    global MOUSE_PRESSED
    MOUSE_PRESSED = True


def on_mouse_release(event):
    global MOUSE_PRESSED
    MOUSE_PRESSED = False


def on_mouse_move(event):
    global MOUSE_PRESSED
    if (not MOUSE_PRESSED) or (not event.ydata):
        return None
    note1.set_fund_freq(float(event.ydata))


listener = kb.Listener(on_press=on_press)
listener.start()
press_id = fig.canvas.mpl_connect("button_press_event", on_mouse_press)
move_id = fig.canvas.mpl_connect("motion_notify_event", on_mouse_move)
release_id = fig.canvas.mpl_connect("button_release_event", on_mouse_release)


fig.show()
note1_dot = note_ax.scatter([len(freq_history)], [note1.get_fund_freq()])
note2_dot = note_ax.scatter([len(freq_history)], [note2.get_fund_freq()])
(trail,) = note_ax.plot(freq_history.to_list())
dissonance_dot = dist_ax.scatter(x=[0], y=[note1.calc_tone_dissonance(note2)])
(dissonance_trail,) = dist_ax.plot(dissonance_history.to_list())

frame_count = 1
while listener.is_alive():
    start = time.time()
    
    # update the values
    curr_fund_freq_1 = note1.get_fund_freq()
    curr_fund_freq_2 = note2.get_fund_freq()
    curr_dissonance = note1.calc_tone_dissonance(note2)

    # Udate graphs
    trail.set_ydata(freq_history.to_list())
    note1_dot.set_offsets([(note_x, curr_fund_freq_1)])
    note2_dot.set_offsets([(note_x, curr_fund_freq_2)])
    dissonance_dot.set_offsets([(note_x, curr_dissonance)])
    dissonance_trail.set_ydata(dissonance_history.to_list())
    if curr_dissonance > dist_max:
        dist_max = 1.1 * curr_dissonance
        dist_ax.set_ylim((0, dist_max))
        print("resetting dissonance range")

    # get old values and update histoiries
    prev_fund_freq_1 = curr_fund_freq_1
    prev_fund_freq_2 = curr_fund_freq_2
    prev_dissonance = curr_dissonance
    freq_history.set_curr_value(prev_fund_freq_1)
    freq_history.advance() # advance so it points to the oldest value for plotting
    dissonance_history.set_curr_value(prev_dissonance)
    dissonance_history.advance()
    # TODO: Add a history for note 2
    
    fig.canvas.flush_events()

    frame_count += 1
    end = time.time()
    extra_frame_time = max(0, frame_length - (end - start))
    time.sleep(
        max(0, extra_frame_time)
    )  # Try to make evey frame a standard amount of time.
