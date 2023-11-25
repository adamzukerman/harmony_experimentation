import pyo

s = pyo.Server().boot().start()

# The `mul` attribute multiplies each sample by its value.
a = pyo.Sine(freq=100, mul=0.1)

# The `add` attribute adds an offset to each sample.
# The multiplication is applied before the addition.
b = pyo.Sine(freq=100, mul=0.5, add=0.5)

# Using the range(min, max) method allows to automatically
# compute both `mul` and `add` attributes.
c = pyo.Sine(freq=100).range(-0.25, 0.5)

# Displays the waveforms
sc = pyo.Scope([a, b, c])

s.gui(locals())