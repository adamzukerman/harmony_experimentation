import pyo
import pynput.keyboard as kb
import matplotlib.pyplot as plt
import time

MOUSE_PRESSED = False

plt.ion()
fig, ax = plt.subplots(1, 1)
ax.set_aspect('equal')
ax.set_xlim(0, 1000)
ax.set_ylim(0, 1000)

s = pyo.Server().boot()
s.start()
note1 = pyo.Sine(freq=440, mul=0.4).out()

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
    elif key == kb.Key.shift:
        pass
    else:
        print("key behavior undefined")

def on_mouse_press(event):
    y_pos = float(event.ydata) # pyo can't handle numpy dtypes
    note1.freq = float(y_pos) 
    global MOUSE_PRESSED
    MOUSE_PRESSED = True

def on_mouse_release(event):
    global MOUSE_PRESSED
    MOUSE_PRESSED = False

def on_mouse_move(event):
    global MOUSE_PRESSED
    if not MOUSE_PRESSED:
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
dot1 = ax.scatter([500], [note1.freq])
while listener.is_alive():
    dot1.set_offsets([(500, note1.freq)])
    fig.canvas.flush_events()
    # fig.show() # This doens't work?? I'm supposed to use another way of refreshing with interactive mode.
