from pyo import *
import os
import time

# Audio inputs must be available.
s = Server(duplex=1).boot()

# Path of the recorded sound file.
path = os.path.join(os.path.expanduser("~"), "Desktop", "synth.wav")

# Creates a two seconds stereo empty table. The "feedback" argument
# is the amount of old data to mix with a new recording (overdub).
t = NewTable(length=2, chnls=2, feedback=0.5)

# Retrieves the stereo input
inp = Input([0, 1])

# Table recorder. Call rec.play() to start a recording, it stops
# when the table is full. Call it multiple times to overdub.
rec = TableRec(inp, table=t, fadetime=0.05).play()
# rec2 = TableRec(inp, table=t).play()
# Reads the content of the table in loop.
osc = Osc(table=t, freq=t.getRate(), mul=0.5).out()


def saveToDisk():
    savefileFromTable(table=t, path=path, fileformat=0, sampletype=3)
def recordOver():
    global rec2 
    rec2 = TableRec(inp, table=t).play()

# After two seconds, the table content is saved to a file on disk.
sv = CallAfter(saveToDisk, time=2).play()
CallAfter(recordOver, time=2)

s.gui(locals())