from pyo import *

s = Server().boot()

### Using multichannel-expansion to create a square wave ###

# Sets fundamental frequency.
freq = 100
# Sets the highest harmonic.
high = 20

# Generates the list of harmonic frequencies (odd only).
harms = [freq * i for i in range(1, high) if i % 2 == 1]
# Generates the list of harmonic amplitudes (1 / n).
amps = [0.33 / i for i in range(1, high) if i % 2 == 1]

# Creates all sine waves at once.
a = Sine(freq=harms, mul=amps)
# Prints the number of streams managed by "a".
print(len(a))

# The mix(voices) method (defined in PyoObject) mixes
# the object streams into `voices` streams.
b = a.mix(voices=1).out()

# Displays the waveform.
sc = Scope(b)

# does this create a controller for all streams?
a.ctrl()

s.gui(locals())