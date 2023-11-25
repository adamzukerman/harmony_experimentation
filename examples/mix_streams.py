from pyo import *

s = Server().boot()

# Sets fundamental frequency and highest harmonic.
freq = 100
high = 20

# Generates lists for frequencies and amplitudes
harms = [freq * i for i in range(1, high) if i % 2 == 1]
amps = [0.33 / i for i in range(1, high) if i % 2 == 1]

# Creates a square wave by additive synthesis.
a = Sine(freq=harms, mul=amps)
print("Number of Sine streams: %d" % len(a))

# Mix down the number of streams of "a" before computing the Chorus.
b = Chorus(a.mix(2), feedback=0.5).out()
print("Number of Chorus streams: %d" % len(b))

s.gui(locals())