import pyo 

s = pyo.Server().boot().start()

a = pyo.Sine(440, mul=0.1).out()
b = pyo.Sine(freq=0.1, mul=200, add=440)
shifting_note = pyo.Sine(freq=b, mul=0.1).out()
shifting_note.ctrl(title="shifting note")

pyo.Scope([a, shifting_note])

s.gui(locals())