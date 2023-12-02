import pyo
import pynput.keyboard as kb
import matplotlib.pyplot as plt
import time

fig, ax = plt.subplots(1, 1)
ax.set_aspect('equal')
ax.set_xlim(0, 1000)
ax.set_ylim(0, 1000)

s = pyo.Server().boot()
s.start()

def on_press(key):
    if key == kb.KeyCode.from_char('q'):
        global s
        s.stop()
        print("Terminating")
        return False
    if key == kb.KeyCode.from_char('u'):
        note1.setFreq(note1.freq * pow(2, 1/12))
    if key == kb.KeyCode.from_char('U'):
        note1.freq *= pow(2, -1/12)
    else:
        print("key behavior undefined")

listener = kb.Listener(on_press=on_press)
listener.start()

note1 = pyo.Sine(freq=440, mul=0.4).out()
# note1.ctrl()

# Looks like I can't mix matplotlib and pyo GUI
# s.gui(locals())

while listener.is_alive():
    # plt.scatter(x=[500], y=note1.freq)
    # plt.show()
    print(note1.freq)
    time.sleep(0.5)