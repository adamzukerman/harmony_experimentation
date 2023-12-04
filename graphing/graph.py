import pyo
import pynput.keyboard as kb
import matplotlib.pyplot as plt
import time

MOUSE_PRESSED = False
FRAME_RATE = 30
TRAIL_TIME = 2 # number of seconds to show of pitch history
PITCH_MAX = 1000


frame_length = 1/FRAME_RATE
freq_history = [0]*(TRAIL_TIME * FRAME_RATE)

plt.ion()
fig, ax = plt.subplots(1, 1)
ax.set_xlim(0, 2*len(freq_history)) # have the note in middle of graph
ax.set_ylim(0, PITCH_MAX)
ax.set_aspect((2 * len(freq_history)) / PITCH_MAX)
note_x = len(freq_history)

s = pyo.Server().boot()
s.start()
note1 = pyo.Sine(freq=440, mul=0.4).out()
note2 = pyo.Sine(freq=note1.freq/2, mul=note1.mul).out()

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

plt.show()
trail, = ax.plot(freq_history)
note1_dot = ax.scatter([len(freq_history)], [note1.freq])
note2_dot = ax.scatter([len(freq_history)], [note2.freq])
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
    fig.canvas.flush_events()
    # fig.show() # This doens't work?? I'm supposed to use another way of refreshing with interactive mode.

    frame_count += 1
    end = time.time()
    break_time = max(0, frame_length - (end - start)) 
    time.sleep(max(0, break_time)) # Try to make evey frame a standard amount of time.
