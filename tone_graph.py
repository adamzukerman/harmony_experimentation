import time
import math
import numpy as np
import matplotlib
from matplotlib import animation
from matplotlib.widgets import Slider
import matplotlib.pyplot as plt
from scipy.optimize import Bounds, minimize
import pynput.keyboard as kb
import pyo
from tone import Tone
from circular_list import CircularList
import inputs
import notes
from note_collection import NoteCollection

# Setting up file-wide constants
# TODO Move this to a parameters file?
FRAME_RATE = 60
TRAIL_TIME = 5  # number of seconds to show of pitch history
FREQ_MAX = 4_000
FREQ_MIN = 30
STARTING_FREQ_1 = 440
STARTING_FREQ_2 = 220
dist_max = 0.1

# Directly derived from constants
frame_length = 1 / FRAME_RATE
freq_history1 = CircularList(TRAIL_TIME * FRAME_RATE, init_value=0)
freq_history2 = CircularList(TRAIL_TIME * FRAME_RATE, init_value=0)
dissonance_history = CircularList(TRAIL_TIME * FRAME_RATE, init_value=0)

    
# Setting up pyo objects
# output_device_name = "Adam’s AirPods Pro" # Requires weird single quote with opt+shift+]
# output_device_name = pyo.pa_get_output_devices()[0][0] # This is probably the better solution that connects to most headphones
# print("Audio output device: ", output_device_name)
s = pyo.Server()
# device_names, device_indexes = pyo.pa_get_output_devices()
# my_dev_index = device_names.index(output_device_name)
# pyo_output_location = device_indexes[my_dev_index]
# s.setOutputDevice(pyo_output_location)
s.boot()
s.start()
note_collection = NoteCollection()
note1 = Tone(fund_freq=notes.A4, mul=0.4, time=0.5)
note1.set_random_overtones(15)
note_collection.add_note(note1)
note2 = Tone(fund_freq=notes.A4/2, mul=0.4)
note2.set_random_overtones(15)
note_collection.add_note(note2)
active_notes = note_collection.active_notes
slctd_note_indx = 0
freq_history1.set_all_values(note1.get_fund_freq())
freq_history2.set_all_values(note2.get_fund_freq())


listener = kb.Listener(on_press=lambda key: inputs.on_press(key, active_notes, slctd_note_indx, {"server":s}))
listener.start()

# Initial setup of axes and gridspec
matplotlib.use("MacOSX")
fig = plt.figure(layout="constrained")
fig.set_size_inches(w=10, h=6)
widths = [1, 30]
heights = [1, 1, 1]
n_rows, n_cols = 2, 2
spec = fig.add_gridspec(nrows=3, ncols=2, width_ratios=widths, height_ratios=heights)
slider_ax = fig.add_subplot(spec[0, 0])
note_ax = fig.add_subplot(spec[0, 1])
dissonance_sensitivity_ax = fig.add_subplot(spec[1,1:])
dist_ax = fig.add_subplot(spec[2, 1:])
# Dissonance history axis settings
dist_ax.set_title("Dissonance History")
dist_ax.set_xlim(0, 1.1 * len(freq_history1))  # have the note in middle of graph
dist_ax.set_ylim(0, dist_max)  # used for dissonance equation
# note_ax (main axis) settings
note_ax.set_title("Note Pitches")
note_ax.set_ylim(0, TRAIL_TIME)  # have the note in middle of graph
note_ax.set_xscale("log")
note_ax.get_xaxis().set_major_formatter(matplotlib.ticker.NullFormatter())
note_ax.get_xaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())
note_ax.get_xaxis().set_minor_locator(matplotlib.ticker.NullLocator())
note_ax.get_xaxis().set_major_locator(matplotlib.ticker.NullLocator())
note_ax.set_xticks(notes.note_freqs, notes.note_labels)
#Dissonance sensitivity axis settings (mostly the same as note_axis)
dissonance_sensitivity_ax.set_title("Dissonance by Note1 Pitch")
dissonance_sensitivity_ax.set_xscale("log")
dissonance_sensitivity_ax.get_xaxis().set_major_formatter(matplotlib.ticker.NullFormatter())
dissonance_sensitivity_ax.get_xaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())
dissonance_sensitivity_ax.get_xaxis().set_minor_locator(matplotlib.ticker.NullLocator())
dissonance_sensitivity_ax.get_xaxis().set_major_locator(matplotlib.ticker.NullLocator())
dissonance_sensitivity_ax.set_xticks(notes.note_freqs, notes.note_labels)

slider = Slider(slider_ax, label="range_control", valmin=0, valmax=(math.log10(FREQ_MAX/FREQ_MIN)/2), orientation="vertical", valinit=0.25)
note_y = 0.03 * note_ax.get_ylim()[1]
dissonance_x = len(freq_history1)
trail_ys = np.linspace(start=note_ax.get_ylim()[1], stop=note_y, num=len(freq_history1)) 
note1_dot = note_ax.scatter([note1.get_fund_freq()], [note_y])
note2_dot = note_ax.scatter([note2.get_fund_freq()], [note_y])
(trail1,) = note_ax.plot(freq_history1.to_list(), trail_ys)
(trail2,) = note_ax.plot(freq_history2.to_list(), trail_ys)
dissonance_dot = dist_ax.scatter(x=[0], y=[note1.calc_tone_dissonance(note2)])
(dissonance_trail1,) = dist_ax.plot(dissonance_history.to_list())
(dissonance_plot,) = dissonance_sensitivity_ax.plot(dissonance_sensitivity_ax.get_xlim()[0], dissonance_sensitivity_ax.get_ylim()[0])
# Broken until I give inputs file access to axes
# press_id = fig.canvas.mpl_connect("button_press_event", lambda event: inputs.on_mouse_press(event, active_notes, slctd_note_indx))
# move_id = fig.canvas.mpl_connect("motion_notify_event", lambda event: inputs.on_mouse_move(event, active_notes, slctd_note_indx))
# release_id = fig.canvas.mpl_connect("button_release_event", lambda event: inputs.on_mouse_release(event, active_notes, slctd_note_indx))

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
    new_xmin = pow(10, middle - val)
    new_xmax = pow(10, middle + val)
    #Linear search through notes to find which which ticks to set
    # I'm sure there are possible budgs in this with the loose relationship between the scale and the fixed set of possible ticks
    min_indx = -1
    max_indx = -1
    for indx, freq in enumerate(notes.note_freqs):
        if min_indx == -1 and freq > new_xmin:
            min_indx = indx
        if max_indx == -1 and freq > new_xmax:
            max_indx = indx - 1
            break 
    note_ax.set_xlim(new_xmin, new_xmax) 
    note_ax.set_xticks(notes.note_freqs[min_indx:max_indx], notes.note_labels[min_indx:max_indx]) # Setting ticks is modifying the limits!
    dissonance_sensitivity_ax.set_xlim(new_xmin, new_xmax)
    dissonance_sensitivity_ax.set_xticks(notes.note_freqs[min_indx:max_indx], notes.note_labels[min_indx:max_indx]) # Setting ticks is modifying the limits!
slider.on_changed(slider_update)

def setup():
    # Setting up graph properties
    # If I put the actual setupt in here, the window shows up all black
    slider_update(slider.val)

def update_graph(frame):
    start_time = time.time()
    
    # update the values
    curr_fund_freq_1 = note1.get_fund_freq()
    curr_fund_freq_2 = note2.get_fund_freq()
    curr_dissonance = note1.calc_tone_dissonance(note2)

    # Udate graphs
    trail1.set_xdata(freq_history1.to_list())
    trail2.set_xdata(freq_history2.to_list())
    note1_dot.set_offsets([(curr_fund_freq_1, note_y)])
    note2_dot.set_offsets([(curr_fund_freq_2, note_y)])
    dissonance_dot.set_offsets([(dissonance_x, curr_dissonance)])
    dissonance_trail1.set_ydata(dissonance_history.to_list())
    diss_x = np.linspace(
        start=dissonance_sensitivity_ax.get_xlim()[0],
        stop=dissonance_sensitivity_ax.get_xlim()[1],
        num=200
        )
    # Need to re-make the calc_dissonance funditon to note require a played tone
    # Or I can add a copy function that produces a non-output version of the copied Tone
    diss_y = []
    temp_note = note1.copy()
    for x in diss_x:
        temp_note = Tone(fund_freq = float(x), mul=note1.get_mul(), overtones=note1.get_overtones())
        diss_y.append(temp_note.calc_tone_dissonance(note2))
    dissonance_plot.set_xdata(diss_x)
    dissonance_plot.set_ydata(diss_y)
    global dist_max
    if curr_dissonance > dist_max or max(diss_y) > dist_max:
        new_max = 1.1 * max(max(diss_y), curr_dissonance)
        dist_max = new_max
        dist_ax.set_ylim((0, new_max))
        dissonance_sensitivity_ax.set_ylim((0, dist_max))
        print("resetting dissonance range")

    # update histoiries
    freq_history1.set_curr_value(curr_fund_freq_1)
    freq_history1.advance() # advance so it points to the oldest value for plotting
    freq_history2.set_curr_value(curr_fund_freq_2)
    freq_history2.advance() # advance so it points to the oldest value for plotting
    dissonance_history.set_curr_value(curr_dissonance)
    dissonance_history.advance()
    
    # fig.canvas.flush_events()

    end_time = time.time()
    # Try to make evey frame a standard amount of time.
    extra_frame_time = max(0, frame_length - (end_time - start_time))
    if extra_frame_time > 0:
        time.sleep(extra_frame_time)

ani = animation.FuncAnimation(fig=fig, func=update_graph, init_func=setup, interval=1_000*1/FRAME_RATE)
fig.show()
plt.show()