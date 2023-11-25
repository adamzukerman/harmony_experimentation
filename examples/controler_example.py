from pyo import *

s = Server().boot()
s.amp = 0.4

# Creates two objects with cool parameters, one per channel.
a = FM().out()
# b = FM().out(1)

# Opens the controller windows.
a.ctrl(title="Frequency modulation left channel")
# b.ctrl(title="Frequency modulation right channel")

# If a list of values is given at a particular argument, the ctrl
# window will show a multislider to set each value separately.

oscs = Sine([100, 200, 300, 400, 500, 600, 700, 800], mul=0.1).out()
oscs.ctrl(title="Simple additive synthesis")

s.gui(locals())
