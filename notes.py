"""This module generates the notes names and associated frequencies for the
piano keyboard. Notes are constructed outwards starting from the A4.
"""
A4 = 440
NOTES_RANGE = 40
NOTE_NAMES = [
    "A",
    "A#/Bb",
    "B",
    "C",
    "C#/Db",
    "D",
    "D#/Eb",
    "E",
    "F",
    "F#/Gb",
    "G",
    "G#/Ab",
]

note_freqs = [A4 * pow(2, i * 1 / 12) for i in range(NOTES_RANGE)]
note_freqs = [A4 * pow(2, i * -1 / 12) for i in range(1, NOTES_RANGE)][
    ::-1
] + note_freqs
note_labels = [NOTE_NAMES[indx % 12] for indx in range(NOTES_RANGE)]
note_labels = [NOTE_NAMES[(-1 * indx) % 12] for indx in range(1, NOTES_RANGE)][
    ::-1
] + note_labels
a4_indx = note_freqs.index(A4)

note_freq_dict = {}
octave = 4
# notes going up from A4
for i, (note_name, note_freq) in enumerate(
    zip(note_labels[a4_indx:], note_freqs[a4_indx:])
):
    key = note_name + str(octave)
    if note_freq_dict.get(key):
        octave += 1
        key = note_name + str(octave)
    note_freq_dict[key] = note_freq
octave = 4
# notes going down from A4
for i, (note_name, note_freq) in enumerate(
    zip(note_labels[: a4_indx + 1][::-1], note_freqs[: a4_indx + 1][::-1])
):
    key = note_name + str(octave)
    if note_freq_dict.get(key):
        octave -= 1
        key = note_name + str(octave)
    note_freq_dict[key] = note_freq
