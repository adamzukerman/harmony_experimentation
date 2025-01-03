import logging
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

# setup logger
logger = logging.getLogger(__name__)

def on_press(key, tone_collection, tone_trails, tone_dots, freq_histories, globals):
    # TODO: change body to use slctd_tone_id
    # TODO: search for and remove all keybindings that conflict with matplotlib
    # TODO: still using slctd_tone for everything that's not just shifting not pitches
    slctd_tone = tone_collection.get_selected_tone()
    global PIANO_MODE

    def enter_piano_mode():
        logger.info("entering piano mode")
        global PIANO_MODE
        PIANO_MODE = True

    def stop_program():
        server = globals.get("server")
        if server:
            server.stop()
        logger.info("Terminating")
        plt.close("all")
        return False

    def adjust_note_frequency(note, exponent):
        note.set_fund_freq(note.get_fund_freq() * pow(2, exponent))

    def reset_overtones():
        logger.info("Resetting overtones randomly")
        for tone_id, tone in tone_collection:
            tone.set_random_overtones(15)

    def hide_yticklabels():
        note_ax.set_yticklabels([])

    def turn_off_piano_mode():
        global PIANO_MODE
        logger.info("turning off piano mode")
        PIANO_MODE = False

    def set_note_frequency(note, note_name):
        logger.info("setting note frequency to " + note_name)
        note_freq = notes.note_freq_dict.get(note_name)
        if note_freq:
            note.set_fund_freq(note_freq)
        else:
            logger.warning("WARNONG: note frequency not found")

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
        temp_collection = tone_collection.copy()
        slctd_tone = temp_collection.get_selected_tone()
        solution = minimize(
            fun=lambda x: (
                slctd_tone.set_fund_freq(x),
                temp_collection.calc_dissonance(),
            )[1],
            x0=slctd_tone.get_fund_freq(),
            bounds=Bounds(
                slctd_tone.get_fund_freq() * pow(2, -3/12),
                slctd_tone.get_fund_freq() * pow(2, 3/12),
            ),
        )
        tone_collection.get_selected_tone().set_fund_freq(solution.x.item())
        pass

    def resolve_above_bass(tone_collection):
        lowest_id = tone_collection.get_id_lowest_tone()
        resolve_with_exclusions([lowest_id])
    
    def resolve_helper(freqs, temp_collection, excluded_ids=None):
        if excluded_ids is None:
            excluded_ids = []
        for (id, tone), new_freq in zip(temp_collection, freqs):
            if id in excluded_ids:
                continue
            tone.set_fund_freq(new_freq)
        return temp_collection.calc_dissonance()
    
    def resolve_all():
        temp_collection = tone_collection.copy()
        lowest_tone = tone_collection.get_lowest_tone()
        lowest_tone_id = tone_collection.get_id_from_tone(lowest_tone)
        lowest_freq = tone_collection.get_ids_and_freqs()[lowest_tone_id]
        slctd_tone_id_backup = tone_collection.slctd_tone_id
        
        # start with geiven frequencies and asjust them inside window of 3 half steps
        x0 = temp_collection.get_fund_freqs()
        bounds = [[max(lowest_freq, freq * pow(2, -1/12)), freq*pow(2, 1/12)] for freq in x0]

        solution = minimize(
            fun=lambda x: resolve_helper(x, temp_collection),
            x0=temp_collection.get_fund_freqs(),
            bounds=bounds,
            options={
                "disp":True, 
                "xrtol":0.001,
                "gtol":1e-5
            },
            # method='trust-constr',
            method='BFGS',
        )
        logger.info(f"Solution that minimizes dissonance: {solution}")

        for (id, tone), freq in zip(tone_collection, solution.x):
            tone_collection.set_tone_freq(id, freq)

    def resolve_with_exclusions(excluded_ids=None):
        id_freq_dict = tone_collection.get_ids_and_freqs()
        temp_collection = tone_collection.copy()
        # Can't just remove from temp_collection because it have to use exluded tones to calculate dossonance
        # for id in excluded_ids:
        #     temp_collection.remove_tone(id)
        
        # start with geiven frequencies and asjust them inside window of 3 half steps
        # x0 = temp_collection.get_fund_freqs()
        x0 = []
        x0_id_dict = {}
        for id, tone in temp_collection:
            if id in excluded_ids:
                continue 
            x0_id_dict[id] = len(x0)
            x0.append(tone.get_fund_freq())
        bounds = [[freq * pow(2, -1/12), freq*pow(2, 1/12)] for freq in x0]
        logger.info(f"optimization param lengths -- x0:{len(x0)}, bounds:{len(bounds)}")
        logger.info(f"optimizing with params x0={x0}, bounds={bounds}")

        solution = minimize(
            fun=lambda x: resolve_helper(x, temp_collection, excluded_ids),
            x0=x0,
            bounds=bounds,
            options={"disp":True},
            method='trust-constr',
        )
        logger.info(f"Solution that minimizes dissonance: {solution}")

        for tone_id, indx in x0_id_dict.items():
            tone_collection.set_tone_freq(tone_id, solution.x[indx])
        # for (id, tone), freq in zip(tone_collection, solution.x):
        #     tone_collection.set_tone_freq(id, freq)

    def select_next_tone() -> None:
        logger.info("running select_next_tone")
        if tone_collection.slctd_tone_id == None:
            logger.info("cannot select next tone when no tone is selected")
            return None
        tone_ids = tone_collection.get_tone_ids()
        if tone_collection.slctd_tone_id not in tone_ids:
            raise ValueError("Selected tone not in tone collection")
        slctd_tone_indx = tone_ids.index(tone_collection.slctd_tone_id)
        new_sltd_tone_indx = (slctd_tone_indx + 1) % len(tone_ids)
        tone_collection.set_selected_tone(tone_ids[new_sltd_tone_indx])
        logger.info("changing selected tone to " + str(tone_collection.slctd_tone_id))

    def add_new_tone() -> None:
        logger.info("adding a new tone")
        init_freq = notes.A4
        new_tone = Tone(fund_freq=init_freq, mul=0.4, time=globals["TONE_MOVE_TIME"])
        # new_tone.set_random_overtones(15)
        new_tone_id = tone_collection.add_tone(tone=new_tone)
        tone_collection.set_selected_tone(new_tone_id)
        tone_collection.play_tone(new_tone_id)
        logger.info(f"adding new tone_id {new_tone_id} to tone_dots and tone_trails")
        freq_histories[new_tone_id] = CircularList(
            size=globals["FRAME_RATE"] * globals["TRAIL_TIME"], init_value=init_freq
        )
        tone_trails[new_tone_id] = globals["note_ax"].plot(
            freq_histories[new_tone_id].to_list(), globals["trail_ys"]
        )[0]
        tone_dots[new_tone_id] = globals["note_ax"].plot(
            [init_freq], [globals["note_y"]], marker='o', linestyle='None' #should create param for marker
        )[0]

    def align_tone_with_piano():
        if tone_collection.get_selected_tone() is not None:
            logger.info("aligning tone with axis ticks")
            tone_collection.get_selected_tone().snap_to_nearest_note() 
        else:
            logger.warning("tone for alignment not found")
    
    def align_all_tones_with_piano():
        for _, tone in tone_collection:
            tone.snap_to_nearest_note()

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
        kb.KeyCode.from_char("t"): lambda: tune_selected_tone(tone_collection),
        kb.KeyCode.from_char("r"): resolve_tone,
        kb.KeyCode.from_char("R"): lambda: resolve_above_bass(tone_collection),
        kb.KeyCode.from_char("."): resolve_all,
        kb.KeyCode.from_char("i"): align_tone_with_piano,
        kb.KeyCode.from_char("I"): align_all_tones_with_piano,
        kb.KeyCode.from_char("m"): tone_collection.reduce_dissonance,
        kb.KeyCode.from_char("n"): tone_collection.increase_dissonance,
        kb.KeyCode.from_char("p"): lambda: logger.info(tone_collection),
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
        logger.info(f"Action for key '{key}' Executed")
    else:
        logger.info("key behavior undefined")


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
