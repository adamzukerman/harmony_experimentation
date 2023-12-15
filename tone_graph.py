import pyo
from tone import Tone
from circular_list import CircularList
import pynput.keyboard as kb
import matplotlib
from matplotlib import animation
from matplotlib.widgets import Slider
import matplotlib.pyplot as plt
import time
import math
import numpy as np

# Setting up file-wide constants
# TODO Move this to a parameters file?
MOUSE_PRESSED = False
FRAME_RATE = 60
TRAIL_TIME = 5  # number of seconds to show of pitch history
FREQ_MAX = 4_000
FREQ_MIN = 30
A = 440
STARTING_FREQ_1 = 440
STARTING_FREQ_2 = 220
dist_max = 0.1
NOTES_RANGE = 40
NOTE_NAMES = ['A', 'A#/Bb', 'B', 'C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab']

# Directly derived from constants
frame_length = 1 / FRAME_RATE
freq_history1 = CircularList(TRAIL_TIME * FRAME_RATE)
freq_history1.set_all_values(value=0)
freq_history2 = CircularList(TRAIL_TIME * FRAME_RATE)
freq_history2.set_all_values(value=0)
dissonance_history = CircularList(TRAIL_TIME * FRAME_RATE)
dissonance_history.set_all_values(value=0)
note_freqs = [A * pow(2, i * 1 / 12) for i in range(NOTES_RANGE)] 
note_freqs = [A * pow(2, i * -1 / 12) for i in range(1, NOTES_RANGE)][::-1] + note_freqs
note_labels = [NOTE_NAMES[indx % 12] for indx in range(NOTES_RANGE)]
note_labels = [NOTE_NAMES[(-1*indx) % 12] for indx in range(1, NOTES_RANGE)][::-1] + note_labels

    
# Setting up pyo objects
# output_device_name = "Adam’s AirPods Pro" # Requires weird single quote with opt+shift+]
output_device_name = pyo.pa_get_output_devices()[0][0] # This is probably the better solution that connects to most headphones
s = pyo.Server()
device_names, device_indexes = pyo.pa_get_output_devices()
my_dev_index = device_names.index(output_device_name)
pyo_output_location = device_indexes[my_dev_index]
s.setOutputDevice(pyo_output_location)
s.boot()
s.start()
note1 = Tone(fund_freq=A, mul=0.4)
note1.set_random_overtones(15)
print("nummber of overtones for note1: ", len(note1._get_sines().items()))
note1.out()
note2 = Tone(fund_freq=A/2, mul=0.4)
note2.set_random_overtones(15)
note2.out()
freq_history1.set_all_values(note1.get_fund_freq())
freq_history2.set_all_values(note2.get_fund_freq())


def on_press(key):
    if key == kb.KeyCode.from_char("q"):
        global s
        s.stop()
        print("Terminating")
        plt.close("all")
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
    elif key == kb.KeyCode.from_char("a"):
        note_ax.set_yticklabels([])
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
    if not event.ydata or not note_ax == event.inaxes:
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

# Initial setup of axes and gridspec
matplotlib.use("MacOSX")
fig = plt.figure()
fig.set_size_inches(w=10, h=9)
widths = [1, 30]
heights = [1, 1]
n_rows, n_cols = 2, 2
spec = fig.add_gridspec(nrows=2, ncols=2, width_ratios=widths, height_ratios=heights)
slider_ax = fig.add_subplot(spec[0, 0])
note_ax = fig.add_subplot(spec[0, 1])
dist_ax = fig.add_subplot(spec[1, 1])
note_ax.set_xlim(0, 2 * len(freq_history1))  # have the note in middle of graph
note_ax.set_yscale("log")
# Get rid of default ticks
note_ax.get_yaxis().set_major_formatter(matplotlib.ticker.NullFormatter())
note_ax.get_yaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())
note_ax.get_yaxis().set_minor_locator(matplotlib.ticker.NullLocator())
note_ax.get_yaxis().set_major_locator(matplotlib.ticker.NullLocator())
note_ax.set_yticks(note_freqs, note_labels)
dist_ax.set_xlim(0, 2 * len(freq_history1))  # have the note in middle of graph
dist_ax.set_ylim(0, dist_max)  # used for dissonance equation

slider = Slider(slider_ax, label="range_control", valmin=0, valmax=(math.log10(FREQ_MAX/FREQ_MIN)/2), orientation="vertical", valinit=0.25)
note_x = len(freq_history1)
note1_dot = note_ax.scatter([len(freq_history1)], [note1.get_fund_freq()])
note2_dot = note_ax.scatter([len(freq_history2)], [note2.get_fund_freq()])
(trail1,) = note_ax.plot(freq_history1.to_list())
(trail2,) = note_ax.plot(freq_history2.to_list())
dissonance_dot = dist_ax.scatter(x=[0], y=[note1.calc_tone_dissonance(note2)])
(dissonance_trail1,) = dist_ax.plot(dissonance_history.to_list())
press_id = fig.canvas.mpl_connect("button_press_event", on_mouse_press)
move_id = fig.canvas.mpl_connect("motion_notify_event", on_mouse_move)
release_id = fig.canvas.mpl_connect("button_release_event", on_mouse_release)

def slider_update(val):
    """
    Zoom out/in from center of (currently 2) notes. 
    Requires translating out of and into log scale
    """
    log_f1 = math.log10(note1.get_fund_freq())
    log_f2 = math.log10(note2.get_fund_freq())
    middle = (log_f1 + log_f2)/2
    log_min = math.log10(FREQ_MIN)
    log_max = math.log10(FREQ_MAX)
    new_ymin = pow(10, middle - val)
    new_ymax = pow(10, middle + val)
    #Linear search through notes to find which which ticks to set
    # I'm sure there are possible budgs in this with the loose relationship between the scale and the fixed set of possible ticks
    min_indx = -1
    max_indx = -1
    for indx, freq in enumerate(note_freqs):
        if min_indx == -1 and freq > new_ymin:
            min_indx = indx
        if max_indx == -1 and freq > new_ymax:
            max_indx = indx - 1
            break 
    note_ax.set_ylim(new_ymin, new_ymax) 
    note_ax.set_yticks(note_freqs[min_indx:max_indx], note_labels[min_indx:max_indx]) # Setting ticks is modifying the limits!
slider.on_changed(slider_update)

def set_note_ticks():
    note_ax.set_yticks(note_freqs, note_labels)

def setup():
    # Setting up graph properties
    slider_update(slider.val)

def update(frame):
    start = time.time()
    
    # update the values
    curr_fund_freq_1 = note1.get_fund_freq()
    curr_fund_freq_2 = note2.get_fund_freq()
    curr_dissonance = note1.calc_tone_dissonance(note2)

    # Udate graphs
    trail1.set_ydata(freq_history1.to_list())
    trail2.set_ydata(freq_history2.to_list())
    note1_dot.set_offsets([(note_x, curr_fund_freq_1)])
    note2_dot.set_offsets([(note_x, curr_fund_freq_2)])
    dissonance_dot.set_offsets([(note_x, curr_dissonance)])
    dissonance_trail1.set_ydata(dissonance_history.to_list())
    global dist_max
    if curr_dissonance > dist_max:
        dist_max = 1.1 * curr_dissonance
        dist_ax.set_ylim((0, dist_max))
        print("resetting dissonance range")

    # update histoiries
    freq_history1.set_curr_value(curr_fund_freq_1)
    freq_history1.advance() # advance so it points to the oldest value for plotting
    freq_history2.set_curr_value(curr_fund_freq_2)
    freq_history2.advance() # advance so it points to the oldest value for plotting
    # TODO: Add a history for note 2
    dissonance_history.set_curr_value(curr_dissonance)
    dissonance_history.advance()
    
    fig.canvas.flush_events()

    end = time.time()
    extra_frame_time = max(0, frame_length - (end - start))
    time.sleep(
        max(0, extra_frame_time)
    )  # Try to make evey frame a standard amount of time.
    pass

ani = animation.FuncAnimation(fig=fig, func=update, init_func=setup, interval=1_000*1/FRAME_RATE)
fig.show()
plt.show()
time.sleep(1)