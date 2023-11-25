from pyo import *

s = Server().boot()
s.amp = 0.1

# Full scale sine wave
a = Sine()

# Creates a Dummy object `b` with `mul` attribute
# set to 0.5 and leaves `a` unchanged.
b = a * 0.5
b.out()

# Instance of Dummy class
print(b)

# Computes a ring modulation between two PyoObjects
# and scales the amplitude of the resulting signal.
c = Sine(300)
d = a * c * 0.3
d.out()

# PyoObject can be used with Exponent operator.
e = c ** 10 * 0.4
e.out(1)

# Displays the ringmod and the rectified signals.
sp = Spectrum([d, e])
sc = Scope([d, e])

s.gui(locals())