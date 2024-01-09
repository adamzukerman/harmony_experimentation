import pynput.keyboard as kb
import pynput.mouse as ms
from scipy.optimize import Bounds, minimize
import numpy as np
import matplotlib.pyplot as plt
import notes
from tone import Tone
from circular_list import CircularList

MOUSE_PRESSED = False
PIANO_MODE = False


def on_press(key, tone_collection, tone_trails, tone_dots, freq_histories, globals):
    # TODO: change body to use slctd_tone_id
    # TODO: search for and remove all keybindings that conflict with matplotlib
    # TODO: still using slctd_tone for everything that's not just shifting not pitches
    slctd_tone = tone_collection.get_selected_tone()
    global PIANO_MODE

    def enter_piano_mode():
        print("entering piano mode")
        global PIANO_MODE
        PIANO_MODE = True

    def stop_program():
        server = globals.get("server")
        if server:
            server.stop()
        print("Terminating")
        plt.close("all")
        return False

    def adjust_note_frequency(note, exponent):
        note.set_fund_freq(note.get_fund_freq() * pow(2, exponent))

    def reset_overtones():
        print("Resetting overtones randomly")
        for tone_id, tone in tone_collection:
            tone.set_random_overtones(15)

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

    def tune_selected_tone(tone_collection):
        temp_collection = tone_collection.copy()
        slctd_tone = temp_collection.get_selected_tone()
        solution = minimize(
            fun=lambda x: (
                slctd_tone.set_fund_freq(x),
                temp_collection.calc_dissonance(),
            )[1],
            x0=slctd_tone.get_fund_freq(),
            bounds=Bounds(
                slctd_tone.get_fund_freq() * pow(2, -1 / 12),
                slctd_tone.get_fund_freq() * pow(2, 1 / 12),
            ),
        )
        tone_collection.get_selected_tone().set_fund_freq(solution.x.item())

    def resolve_tone():
        pass

    def resolve_above_bass(tone_collection):
        lowest_tone = tone_collection.get_lowest_tone()
        lowest_tone_id = tone_collection.get_id_from_tone(lowest_tone)
        slctd_tone_id_backup = tone_collection.slctd_tone_id
        for tone_id, tone in tone_collection:
            if lowest_tone == tone:
                continue
            tone_collection.set_selected_tone(tone_id)
            tune_selected_tone(tone_collection)
        tone_collection.set_selected_tone(slctd_tone_id_backup)

    def select_next_tone() -> None:
        print("running select_next_tone")
        if tone_collection.slctd_tone_id == None:
            print("cannot select next tone when no tone is selected")
            return None
        tone_ids = tone_collection.get_tone_ids()
        if tone_collection.slctd_tone_id not in tone_ids:
            raise ValueError("Selected tone not in tone collection")
        slctd_tone_indx = tone_ids.index(tone_collection.slctd_tone_id)
        new_sltd_tone_indx = (slctd_tone_indx + 1) % len(tone_ids)
        tone_collection.set_selected_tone(tone_ids[new_sltd_tone_indx])
        print("changing selected tone to " + str(tone_collection.slctd_tone_id))

    def add_new_tone() -> None:
        print("adding a new tone")
        init_freq = notes.A4
        new_tone = Tone(fund_freq=init_freq, mul=0.4, time=globals["TONE_MOVE_TIME"])
        new_tone.set_random_overtones(15)
        new_tone_id = tone_collection.add_tone(tone=new_tone)
        tone_collection.play_tone(new_tone_id)
        print(f"adding new tone_id {new_tone_id} to tone_dots and tone_trails")
        freq_histories[new_tone_id] = CircularList(
            size=globals["FRAME_RATE"] * globals["TRAIL_TIME"], init_value=init_freq
        )
        tone_trails[new_tone_id] = globals["note_ax"].plot(
            freq_histories[new_tone_id].to_list(), globals["trail_ys"]
        )[0]
        tone_dots[new_tone_id] = globals["note_ax"].scatter(
            x=[init_freq], y=[globals["note_y"]]
        )

    normal_mode_key_actions = {
        kb.KeyCode.from_char("1"): enter_piano_mode if not PIANO_MODE else None,
        kb.KeyCode.from_char("q"): stop_program,
        kb.KeyCode.from_char("u"): lambda: adjust_note_frequency(
            tone_collection.get_selected_tone(), 1 / 12
        ),
        kb.KeyCode.from_char("U"): lambda: adjust_note_frequency(
            tone_collection.get_selected_tone(), -1 / 12
        ),
        kb.KeyCode.from_char("o"): reset_overtones,
        kb.KeyCode.from_char("a"): hide_yticklabels,
        kb.KeyCode.from_char("d"): lambda: tone_collection.remove_tone(tone_id=tone_collection.slctd_tone_id),
        kb.Key.shift: lambda: None,
        kb.Key.shift_r: lambda: None,
        kb.KeyCode.from_char("a"): add_new_tone,
        kb.Key.left: select_next_tone,
        kb.KeyCode.from_char("R"): lambda: tune_selected_tone(tone_collection),
        kb.KeyCode.from_char("r"): lambda: resolve_above_bass(tone_collection),
        kb.KeyCode.from_char(
            "i"
        ): lambda: tone_collection.get_selected_tone().snap_to_nearest_note if tone_collection.get_selected_tone() != None else None,
        kb.KeyCode.from_char("m"): tone_collection.reduce_dissonance,
        kb.KeyCode.from_char("n"): tone_collection.increase_dissonance,
    }
    piano_mode_key_actions = {
        kb.KeyCode.from_char("1"): turn_off_piano_mode,
        kb.Key.space: lambda: set_note_frequency(slctd_tone, "C4"),
        kb.KeyCode.from_char("u"): lambda: set_note_frequency(slctd_tone, "C#/Db4"),
        kb.KeyCode.from_char("j"): lambda: set_note_frequency(slctd_tone, "D4"),
        kb.KeyCode.from_char("i"): lambda: set_note_frequency(slctd_tone, "D#/Eb4"),
        kb.KeyCode.from_char("k"): lambda: set_note_frequency(slctd_tone, "E4"),
        kb.KeyCode.from_char("l"): lambda: set_note_frequency(slctd_tone, "F4"),
        kb.KeyCode.from_char("p"): lambda: set_note_frequency(slctd_tone, "F#/Gb4"),
        kb.KeyCode.from_char("f"): lambda: set_note_frequency(slctd_tone, "B4"),
        kb.KeyCode.from_char("r"): lambda: set_note_frequency(slctd_tone, "A#/Bb4"),
        kb.KeyCode.from_char("d"): lambda: set_note_frequency(slctd_tone, "A3"),
        kb.KeyCode.from_char("e"): lambda: set_note_frequency(slctd_tone, "G#/Ab3"),
        kb.KeyCode.from_char("s"): lambda: set_note_frequency(slctd_tone, "G3"),
    }

    if PIANO_MODE:
        action = piano_mode_key_actions.get(key)
    else:
        action = normal_mode_key_actions.get(key)

    if action:
        action()
    else:
        print("key behavior undefined")


def on_mouse_press(event, tone_collection, note_ax):
    # Currently broken becuase of access to axes
    slctd_tone = tone_collection.get_selected_tone()
    if not event.xdata or not note_ax == event.inaxes:
        return None
    x_pos = float(event.xdata)  # pyo can't handle numpy dtypes
    slctd_tone.set_fund_freq(float(x_pos))
    global MOUSE_PRESSED
    MOUSE_PRESSED = True


def on_mouse_release(event):
    # Currently broken becuase of access to axes
    global MOUSE_PRESSED
    MOUSE_PRESSED = False


def on_mouse_move(event, tone_collection, note_ax):
    # Currently broken becuase of access to axes
    slctd_tone = tone_collection.get_selected_tone()
    global MOUSE_PRESSED
    if (not MOUSE_PRESSED) or (not event.ydata):
        return None
    slctd_tone.set_fund_freq(float(event.xdata))
