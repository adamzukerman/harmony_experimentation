import pyo 
import os 
import sys 
import pathlib

# verify sound file exists
print(pathlib.Path.home())
path = pathlib.Path.home() / "Downloads/sample-3s.mp3"
print(pathlib.Path.exists(path))

# pyo actions
s = pyo.Server().boot().start()
print(pyo.pa_get_output_devices())

a = pyo.SfPlayer(path=str(path), speed=[1], loop=True, mul=0.4).out(2)
scope = pyo.Scope(a)
sp = pyo.Spectrum(a)

def loop_count():
    loop_count.iter += 1
    print("number of time recording ended: ", loop_count.iter)
loop_count.iter = 0

trig_event = pyo.TrigFunc(a["trig"][0], loop_count)
s.gui(locals())