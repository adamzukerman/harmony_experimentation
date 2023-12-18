import pynput.keyboard as kb
import pynput.mouse as ms
import matplotlib.pyplot as plt
import notes

MOUSE_PRESSED = False
PIANO_MODE = False


def on_press(key, active_notes, slctd_note_indx):
    # TODO: change body to use slctd_note_indx
    # More conflicting keybindings with matplotlib
    note1 = active_notes[0]
    note2 = active_notes[1]
    global PIANO_MODE

    def enter_piano_mode():
        print("entering piano mode")
        global PIANO_MODE
        PIANO_MODE = True

    def stop_program():
        global s
        s.stop()
        print("Terminating")
        plt.close("all")
        return False

    def adjust_note_frequency(note, exponent):
        note.set_fund_freq(note.get_fund_freq() * pow(2, exponent))

    def reset_overtones():
        print("Resetting overtones randomly")
        note1.set_random_overtones(15)
        note2.set_random_overtones(15)

    def hide_yticklabels():
        note_ax.set_yticklabels([])
    
    def turn_off_piano_mode():
        global PIANO_MODE
        print("turning off piano mode")
        PIANO_MODE = False

    def set_note_frequency(note, note_name):
        print("setting note frequency to " + note_name)
        note_freq = notes.note_freq_dict.get(note_name)
        if note_freq:
            note.set_fund_freq(note_freq)
        else:
            print("WARNONG: note frequency not found")

    normal_mode_key_actions = {
        kb.KeyCode.from_char("1"): enter_piano_mode if not PIANO_MODE else None,
        kb.KeyCode.from_char("q"): stop_program,
        kb.KeyCode.from_char("u"): lambda: adjust_note_frequency(note1, 1 / 12),
        kb.KeyCode.from_char("U"): lambda: adjust_note_frequency(note1, -1 / 12),
        kb.KeyCode.from_char("i"): lambda: adjust_note_frequency(note2, 1 / 12),
        kb.KeyCode.from_char("I"): lambda: adjust_note_frequency(note2, -1 / 12),
        kb.KeyCode.from_char("o"): reset_overtones,
        kb.KeyCode.from_char("a"): hide_yticklabels,
        kb.Key.shift: lambda: None,
        kb.KeyCode.from_char("r"): lambda: note1.set_fund_freq(STARTING_FREQ_1) and note2.set_fund_freq(STARTING_FREQ_2),
        kb.KeyCode.from_char("R"): lambda: None,  # Ignoring this section until bug is fixed. Reprioritizing
    }
    piano_mode_key_actions = {
        kb.KeyCode.from_char("1"): turn_off_piano_mode,
        kb.Key.space: lambda: set_note_frequency(note1, "C4"),
        kb.KeyCode.from_char("u"): lambda: set_note_frequency(note1, "C#/Db4"),
        kb.KeyCode.from_char("j"): lambda: set_note_frequency(note1, "D4"),
        kb.KeyCode.from_char("i"): lambda: set_note_frequency(note1, "D#/Eb4"),
        kb.KeyCode.from_char("k"): lambda: set_note_frequency(note1, "E4"),
        kb.KeyCode.from_char("l"): lambda: set_note_frequency(note1, "F4"),
        kb.KeyCode.from_char("p"): lambda: set_note_frequency(note1, "F#/Gb4"),
        kb.KeyCode.from_char("f"): lambda: set_note_frequency(note1, "B4"),
        kb.KeyCode.from_char("r"): lambda: set_note_frequency(note1, "A#/Bb4"),
        kb.KeyCode.from_char("d"): lambda: set_note_frequency(note1, "A3"),
        kb.KeyCode.from_char("e"): lambda: set_note_frequency(note1, "G#/Ab3"),
        kb.KeyCode.from_char("s"): lambda: set_note_frequency(note1, "G3"), 
    }
    
    if PIANO_MODE:
        action = piano_mode_key_actions.get(key)
    else: 
        action = normal_mode_key_actions.get(key)

    if action:
        action()
    else:
        print("key behavior undefined")


def on_mouse_press(event, notes, slctd_note_indx):
    note1 = notes[0]
    note2 = notes[1]
    if not event.ydata or not note_ax == event.inaxes:
        return None
    y_pos = float(event.ydata)  # pyo can't handle numpy dtypes
    note1.set_fund_freq(float(y_pos))
    global MOUSE_PRESSED
    MOUSE_PRESSED = True


def on_mouse_release(event, notes, slctd_note_indx):
    note1 = notes[0]
    note2 = notes[1]
    global MOUSE_PRESSED
    MOUSE_PRESSED = False


def on_mouse_move(event, notes, slctd_note_indx):
    note1 = notes[0]
    note2 = notes[1]
    global MOUSE_PRESSED
    if (not MOUSE_PRESSED) or (not event.ydata):
        return None
    note1.set_fund_freq(float(event.ydata))