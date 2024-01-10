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
from note_collection import ToneCollection

# Setting up file-wide constants
# TODO Move this to a parameters file?
FRAME_RATE = 60
TRAIL_TIME = 5  # number of seconds to show of pitch history
FREQ_MAX = 4_000
FREQ_MIN = 30
STARTING_FREQ_1 = 440
STARTING_FREQ_2 = 220
NORM_SIZE = 20
TONE_MOVE_TIME = 0.5
SLCTD_SIZE = 80
dist_max = 0.1
prev_frame_time = time.time()

# Directly derived from constants
min_frame_length = 1 / FRAME_RATE
freq_histories = {}
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
tone_collection = ToneCollection()
note1 = Tone(fund_freq=notes.A4, mul=0.4, time=TONE_MOVE_TIME)
note2 = Tone(fund_freq=notes.A4 / 2, mul=0.4, time=TONE_MOVE_TIME)
note1.set_random_overtones(15)
note2.set_random_overtones(15)
note1_id = tone_collection.add_tone(note1)
note2_id = tone_collection.add_tone(note2)
tone_collection.play_all()
freq_histories[note1_id] = CircularList(
    size=TRAIL_TIME * FRAME_RATE, init_value=note1.get_fund_freq()
)
freq_histories[note2_id] = CircularList(
    size=TRAIL_TIME * FRAME_RATE, init_value=note2.get_fund_freq()
)


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
dissonance_sensitivity_ax = fig.add_subplot(spec[1, 1:])
dist_ax = fig.add_subplot(spec[2, 1:])
# Dissonance history axis settings
dist_ax.set_title("Dissonance History")
dist_ax.set_xlim(
    0, 1.1 * len(list(freq_histories.values())[0])
)  # have the note in middle of graph
dist_ax.set_ylim(0, dist_max)  # used for dissonance equation
dist_ax.get_xaxis().set_major_locator(matplotlib.ticker.NullLocator())
dist_ax.get_xaxis().set_major_formatter(matplotlib.ticker.NullFormatter())
dist_ax.yaxis.tick_right()
dist_ax.tick_params(labelright=True, labelleft=True)
# note_ax (main axis) settings
note_ax.set_title("Note Pitches")
note_ax.set_ylim(0, TRAIL_TIME)  # have the note in middle of graph
note_ax.set_xscale("log")
note_ax.get_xaxis().set_major_formatter(matplotlib.ticker.NullFormatter())
note_ax.get_xaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())
note_ax.get_xaxis().set_minor_locator(matplotlib.ticker.NullLocator())
note_ax.get_xaxis().set_major_locator(matplotlib.ticker.NullLocator())
note_ax.set_xticks(notes.note_freqs, notes.note_labels)
# Dissonance sensitivity axis settings (mostly the same as note_axis)
dissonance_sensitivity_ax.set_title("Dissonance by Selected Pitch")
dissonance_sensitivity_ax.set_xscale("log")
dissonance_sensitivity_ax.get_xaxis().set_major_formatter(
    matplotlib.ticker.NullFormatter()
)
dissonance_sensitivity_ax.get_xaxis().set_minor_formatter(
    matplotlib.ticker.NullFormatter()
)
dissonance_sensitivity_ax.get_xaxis().set_minor_locator(matplotlib.ticker.NullLocator())
dissonance_sensitivity_ax.get_xaxis().set_major_locator(matplotlib.ticker.NullLocator())
dissonance_sensitivity_ax.set_xticks(notes.note_freqs, notes.note_labels)

slider = Slider(
    slider_ax,
    label="range_control",
    valmin=0,
    valmax=(math.log10(FREQ_MAX / FREQ_MIN) / 2),
    orientation="vertical",
    valinit=0.25,
)
note_y = 0.03 * note_ax.get_ylim()[1]
dissonance_x = len(list(freq_histories.values())[0])
trail_ys = np.linspace(
    start=note_ax.get_ylim()[1], stop=note_y, num=len(list(freq_histories.values())[0])
)
tone_dots = {
    tone_id: note_ax.scatter([tone.get_fund_freq()], [note_y])
    for tone_id, tone in tone_collection
}
tone_trails = {
    tone_id: note_ax.plot(freq_histories[tone_id].to_list(), trail_ys)[0]
    for tone_id, tone in tone_collection
}
dissonance_dot = dist_ax.scatter(x=[0], y=[note1.calc_tone_dissonance(note2)])
(dissonance_trail1,) = dist_ax.plot(dissonance_history.to_list())
(dissonance_plot,) = dissonance_sensitivity_ax.plot(
    dissonance_sensitivity_ax.get_xlim()[0], dissonance_sensitivity_ax.get_ylim()[0]
)

# mouse events
press_id = fig.canvas.mpl_connect(
    "button_press_event",
    lambda event: inputs.on_mouse_press(
        event, tone_collection=tone_collection, note_ax=note_ax
    ),
)
move_id = fig.canvas.mpl_connect(
    "motion_notify_event",
    lambda event: inputs.on_mouse_move(
        event, tone_collection=tone_collection, note_ax=note_ax
    ),
)
release_id = fig.canvas.mpl_connect(
    "button_release_event", lambda event: inputs.on_mouse_release(event)
)

listener = kb.Listener(
    on_press=lambda key: inputs.on_press(
        key,
        tone_collection=tone_collection,
        tone_trails=tone_trails,
        tone_dots=tone_dots,
        freq_histories=freq_histories,
        globals={
            "server": s,
            "TRAIL_TIME": TRAIL_TIME,
            "FRAME_RATE": FRAME_RATE,
            "note_ax": note_ax,
            "note_y": note_y,
            "trail_ys": trail_ys,
            "TONE_MOVE_TIME": TONE_MOVE_TIME,
        },
    )
)
listener.start()


def slider_update(val):
    """
    Zoom out/in from center of (currently 2) notes.
    Requires translating out of and into log scale
    """
    pitches = [
        math.log10(note.get_fund_freq())
        for note in tone_collection.active_tones.values()
    ]
    max_pitch = max(pitches)
    min_pitch = min(pitches)
    middle = (max_pitch + min_pitch) / 2
    new_xmin = pow(10, middle - val)
    new_xmax = pow(10, middle + val)
    # Linear search through notes to find which which ticks to set
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
    note_ax.set_xticks(
        notes.note_freqs[min_indx:max_indx], notes.note_labels[min_indx:max_indx]
    )  # Setting ticks is modifying the limits!
    dissonance_sensitivity_ax.set_xlim(new_xmin, new_xmax)
    dissonance_sensitivity_ax.set_xticks(
        notes.note_freqs[min_indx:max_indx], notes.note_labels[min_indx:max_indx]
    )  # Setting ticks is modifying the limits!


slider.on_changed(slider_update)


def setup_graph():
    # Setting up graph properties
    # If I put the actual setupt in here, the window shows up all black
    slider_update(slider.val)
    artists = (
        list(tone_dots.values())
        + list(tone_trails.values())
        + [dissonance_plot, dissonance_trail1, dissonance_dot]
    )
    return artists


def update_graph(frame):
    global prev_frame_time
    start_time = time.time()

    curr_dissonance = tone_collection.calc_dissonance()

    # Update tones and tone_graphs
    for tone_id, tone in tone_collection:
        tone_trails[tone_id].set_xdata(freq_histories[tone_id].to_list())
        tone_dots[tone_id].set_offsets([(tone.get_fund_freq_curr(), note_y)])
        tone_dots[tone_id].set_sizes(
            [SLCTD_SIZE if tone_collection.slctd_tone_id == tone_id else NORM_SIZE]
        )
        freq_histories[tone_id].set_curr_value(tone.get_fund_freq_curr())
        freq_histories[tone_id].advance()
    for tone_id, tone in tone_collection.removed_tones.items():
        if tone_id in tone_trails:
            # erase data for artist because removing artist doesn't work with blitting
            tone_trails[tone_id].set_xdata([])
            tone_trails[tone_id].set_ydata([])
        if tone_id in tone_dots:
            # make dot disappear because deleting is difficult
            tone_dots[tone_id].set_sizes([0])
        if tone_id in freq_histories:
            freq_histories.pop(tone_id)
    tone_collection.flush_removed_tones()

    # Update the dissonance dot
    dissonance_dot.set_offsets([(dissonance_x, curr_dissonance)])
    dissonance_trail1.set_ydata(dissonance_history.to_list())

    # Update the dissonance sensitivity plot
    if tone_collection.get_selected_tone_update_time() > prev_frame_time: 
        diss_x = np.linspace(
            start=dissonance_sensitivity_ax.get_xlim()[0],
            stop=dissonance_sensitivity_ax.get_xlim()[1],
            num=200,
        )
        diss_y = []
        temp_collection = tone_collection.copy()
        temp_slctd_tone = temp_collection.get_selected_tone()
        for x in diss_x:
            if temp_slctd_tone == None: break
            temp_slctd_tone.set_fund_freq(x)
            diss_y.append(temp_collection.calc_dissonance())
        dissonance_plot.set_xdata(diss_x)
        dissonance_plot.set_ydata(diss_y)
    
        # Update dissonance y-axes
        global dist_max
        if diss_y and (curr_dissonance > dist_max or max(diss_y) > dist_max):
            new_max = 1.1 * max(max(diss_y), curr_dissonance)
            dist_max = new_max
            dist_ax.set_ylim((0, new_max))
            dissonance_sensitivity_ax.set_ylim((0, dist_max))
            print("resetting dissonance range")

    # update histoiries
    dissonance_history.set_curr_value(curr_dissonance)
    dissonance_history.advance()

    end_time = time.time()
    # Try to make evey frame a standard amount of time.
    extra_frame_time = max(0, min_frame_length - (end_time - start_time))
    if extra_frame_time > 0:
        # print("stalling to maintain max frame rate")
        time.sleep(extra_frame_time)

    prev_frame_time = end_time
    artists = (
        list(tone_dots.values())
        + list(tone_trails.values())
        + [dissonance_plot, dissonance_trail1, dissonance_dot]
    )
    return artists


ani = animation.FuncAnimation(
    fig=fig, func=update_graph, init_func=setup_graph, interval=0, blit=True
)
# ani = animation.FuncAnimation(fig=fig, func=update_graph, init_func=setup_graph, interval=0, blit=False)
fig.show()
plt.show()
