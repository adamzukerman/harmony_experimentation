from pyo import *

s = Server().boot()

# Two streams of midi pitches chosen randomly in a predefined list.
# The argument `choice` of Choice object can be a list of lists to
# list-expansion.
notes = [60, 62, 63, 65, 67, 69, 71, 72]
mid = Choice(choice=notes, freq=[4])
mid2 = Choice(choice=[note - 8 for note in notes], freq=[3])

# Two small jitters applied on frequency streams.
# Randi interpolates between old and new values.
jit = Randi(min=0.993, max=1.007, freq=[4.3, 3.5])

# Converts midi pitches to frequencies and applies the jitters.
fr = MToF([mid, mid2], mul=jit)

# Chooses a new feedback value, between 0 and 0.15, every 4 seconds.
fd = Randi(min=0, max=0.15, freq=0.25)

# RandInt generates a pseudo-random integer number between 0 and `max`
# values at a frequency specified by `freq` parameter. It holds the
# value until the next generation.
# Generates an new LFO frequency once per second.
sp = RandInt(max=6, freq=1, add=8)
# Creates an LFO oscillating between 0 and 0.4.
amp = Sine(sp, mul=0.2, add=0.2)

# A simple synth...
a = SineLoop(freq=fr, feedback=fd, mul=0.3).out()

s.gui(locals())