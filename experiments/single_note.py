import pyo

# Function to play the A note


def play_a_note():
    midi_note = 69  # MIDI note number for A4
    freq = pyo.midiToHz(midi_note)  # Convert MIDI note to frequency
    # Create a sine wave oscillator and send it to the audio output
    a_note = pyo.Sine(freq).out()


# Create the GUI interface
s = pyo.Server().boot()
s.start()

tone = pyo.Sine(freq=440, mul=0.5)

a = tone.out()
a.ctrl(title="input controller")
h1 = pyo.Harmonizer(a).out()
h2 = pyo.Harmonizer(h1).out(1)
h3 = pyo.Harmonizer(h2).out(1)
# hr = pyo.Harmonizer(tone).out()

# ch = pyo.Chorus(tone).out()

# sh = pyo.FreqShift(tone, shift = 10).out()

print(locals())
# Run the GUI interface
s.gui(locals())
