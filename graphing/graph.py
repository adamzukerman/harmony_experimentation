import pyo
import pynput.keyboard as kb
import matplotlib.pyplot as plt
import time
import math

MOUSE_PRESSED = False
FRAME_RATE = 30
TRAIL_TIME = 2 # number of seconds to show of pitch history
PITCH_MAX = 1000
A = 440
STARTING_FREQ_1 = 440
STARTING_FREQ_2 = 220
notes = [A * pow(2, i * 1/12) for i in range(40)] + [A * pow(2, i * -1/12) for i in range(1,40)]


frame_length = 1/FRAME_RATE
freq_history = [0]*(TRAIL_TIME * FRAME_RATE)

plt.ion()
fig, (note_ax, dist_ax) = plt.subplots(1, 2)
note_ax.set_xlim(0, 2*len(freq_history)) # have the note in middle of graph
note_ax.set_ylim(0, PITCH_MAX)
note_ax.set_aspect((2 * len(freq_history)) / PITCH_MAX)
dist_ax.set_xlim(-1, 1)
# dist_ax.set_ylim(0, PITCH_MAX)
dist_ax.set_ylim(0, 0.1) # used for dissonance equation
note_x = len(freq_history)

s = pyo.Server().boot()
s.start()
note1 = pyo.Sine(freq=STARTING_FREQ_1, mul=0.4).out()
note2 = pyo.Sine(freq=STARTING_FREQ_2, mul=note1.mul).out()

def dissonance(note1, note2):
    # Optimization note: calculating constants on every call
    X = note1.mul * note2.mul
    Y = 2*min(note1.mul, note2.mul)/(note1.mul + note2.mul)
    b1 = 3.5
    b2 = 5.75
    s1 = 0.0207
    s2 = 18.96
    s = 0.24/(s1*min(note1.freq, note2.freq) + s2) 
    dist = abs(note1.freq - note2.freq)
    Z = pow(math.e, -1*b1*s*dist) - pow(math.e, -1*b2*s*dist)
    R = pow(X, 0.1) * 0.5*pow(Y,3.11) * Z 
    return R

def on_press(key):
    if key == kb.KeyCode.from_char('q'):
        global s
        s.stop()
        print("Terminating")
        return False
    elif key == kb.KeyCode.from_char('u'):
        note1.freq *= pow(2, 1/12)
    elif key == kb.KeyCode.from_char('U'):
        note1.freq *= pow(2, -1/12)
    elif key == kb.KeyCode.from_char('i'):
        note2.freq *= pow(2, 1/12)
    elif key == kb.KeyCode.from_char('I'):
        note2.freq *= pow(2, -1/12)
    elif key == kb.Key.shift:
        pass
    elif key == kb.KeyCode.from_char('r'):
        note1.freq = STARTING_FREQ_1
        note2.freq = STARTING_FREQ_2
    elif key == kb.KeyCode.from_char('R'):
        return 1 # ignoring this section until bug is fixed. Reprioritizing
        closest_note1 = min([abs(note1.freq - pitch) for pitch in notes]) #BUG fix this
        closest_note2 = min([abs(note2.freq - pitch) for pitch in notes])
        note1.freq = closest_note1
        note2.freq = closest_note2
    else:
        print("key behavior undefined")

def on_mouse_press(event):
    if not event.ydata:
        return None
    y_pos = float(event.ydata) # pyo can't handle numpy dtypes
    note1.freq = float(y_pos) 
    global MOUSE_PRESSED
    MOUSE_PRESSED = True

def on_mouse_release(event):
    global MOUSE_PRESSED
    MOUSE_PRESSED = False

def on_mouse_move(event):
    global MOUSE_PRESSED
    if (not MOUSE_PRESSED) or (not event.ydata):
        return None
    note1.freq = float(event.ydata)

listener = kb.Listener(on_press=on_press)
listener.start()
press_id = fig.canvas.mpl_connect('button_press_event', on_mouse_press)
move_id = fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)
release_id = fig.canvas.mpl_connect('button_release_event', on_mouse_release)

# Looks like I can't mix matplotlib and pyo GUI
# s.gui(locals())

fig.show()
trail, = note_ax.plot(freq_history)
note1_dot = note_ax.scatter([len(freq_history)], [note1.freq])
note2_dot = note_ax.scatter([len(freq_history)], [note2.freq])
(bar,) = dist_ax.bar(x=[0], height=dissonance(note1, note2))

frame_count = 1
while listener.is_alive():
    start = time.time()
    history_index = frame_count % len(freq_history)
    freq_history[history_index] = note1.freq

    if history_index == len(freq_history) - 1:
        trail.set_ydata(freq_history)
    else:
        trail.set_ydata(freq_history[history_index + 1:] + freq_history[:history_index + 1])
    
    note1_dot.set_offsets([(note_x, note1.freq)])
    bar.set_height(dissonance(note1, note2))
    fig.canvas.flush_events()
    # fig.show() # This doens't work?? I'm supposed to use another way of refreshing with interactive mode.

    frame_count += 1
    end = time.time()
    extra_frame_time = max(0, frame_length - (end - start)) 
    time.sleep(max(0, extra_frame_time)) # Try to make evey frame a standard amount of time.
