import pyo 

s = pyo.Server().boot()

base_freq = 440

scale_notes = [0,2,4,5,7,9,11,12]
scale_factors = [pow(2, deg/12.0) for deg in scale_notes]

choice_freq = pyo.Choice(choice=[0.5, 1, 2, 4], freq=1)
choice_note = pyo.Choice(choice=scale_factors, freq=choice_freq)

note = pyo.Sine(freq=base_freq * choice_note, mul=0.3).out()

s.gui(locals())
