from pyo import *

s = Server().boot()

# White noise
n1 = Noise(0.3)

# Pink noise
n2 = PinkNoise(0.3)

# Brown noise
n3 = BrownNoise(0.3)

# Interpolates between input objects to produce a single output
sel = Selector([n1, n2, n3]).out()
sel.ctrl(title="Input interpolator (0=White, 1=Pink, 2=Brown)")

# Displays the spectrum contents of the chosen source
sp = Spectrum(sel)

s.gui(locals())