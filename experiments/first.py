import pyo
import time

asdf = 1
s = pyo.Server(nchnls=1).boot()
s.start()
time.sleep(1)
a = pyo.Sine(mul=0.1, freq=440)
print("playing the first tone")
a.out()
time.sleep(2)
b = pyo.Sine(mul=0.2, freq=a*1.5)
print("playing the second tone")
b.out()
time.sleep(2)
# s.gui(locals())
a.stop()
b.stop()
s.stop()
time.sleep(2)
s.gui(locals())
