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

# the SndTable object does not send termination signals.
a = pyo.SndTable(path=str(path))
freq = a.getRate()
print("freq:", freq)

osc = pyo.Osc(table=a, freq=a.getRate()).out()

s.gui(locals())