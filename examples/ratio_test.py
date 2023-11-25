import pyo 

s = pyo.Server().boot().start()

a = pyo.Sine(freq=440).out()
b = pyo.SumOsc(a).out(1)
a.ctrl()
b.ctrl()

s.gui(locals())