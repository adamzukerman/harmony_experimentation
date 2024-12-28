"""BUG: Need to check if pyo server is already started"""
import math
import logging
import numpy as np
import pyo
from notes import note_freq_dict

# setup logger
logger = logging.getLogger(__name__)

class Tone:
    # tone_server = pyo.Server().boot() # should this be here inside a class?
    def __init__(self, fund_freq: float, mul: float, overtones: dict = None, time=0):
        self.__fund_freq = pyo.SigTo(value=fund_freq, time=time, init=fund_freq)
        self.__mul = mul
        if overtones is None:
            self.__overtones = {1:mul}
        else:
            # Check that fundamental freq is defined
            if 1 not in overtones.keys():
                raise ValueError("No strength defined for fundamental frequency in overtones")
            # check that values for all overtones are valid
            for freq_mul, strength in overtones.items():
                if not isinstance(freq_mul, int):
                    raise ValueError("frequency multiplier in overtones is not an integer")
                if strength < 0:
                    raise ValueError("Negative frequency strength passed to overtones")
            self.__overtones = {freq_mul:strength * mul for freq_mul, strength in overtones.items()}
            self.__overtones = overtones
        self._sines = []
        self.__generate_sines(self.__fund_freq, self.__overtones.copy())

    def copy(self):
        """Returns a deep copy of this Tone that not being played"""
        return Tone(
            self.__fund_freq.value,
            self.__mul,
            self.__overtones.copy(),
            time=self.__fund_freq.time,
        )

    def __generate_sines(self, fund_freq, overtones):
        self._sines = {
            overtone: pyo.Sine(freq=self.__fund_freq * overtone, mul=self.__mul * amp)
            for (overtone, amp) in self.__overtones.items()
        }

    # def get_fund_freq(self):
    #     # how to make sure this can't be used to modify the object when copy is not allowed for int/float?
    #     return self.__fund_freq.get()

    def get_fund_freq(self):
        # how to make sure this can't be used to modify the object when copy is not allowed for int/float?
        return self.__fund_freq.value

    def get_fund_freq_curr(self):
        return self.__fund_freq.get()

    # Maybe this shouldn't be accessible?
    def _get_sines(self):
        """Returns the pyo Sines that make up this tone"""
        return self._sines

    def get_mul(self):
        return self.__mul

    def get_overtones(self):
        """Returns a copy of this Tone's overtones"""
        return self.__overtones.copy()

    def out(self):
        for overtone, sine in self._sines.items():
            sine.out()

    def stop(self):
        for overtone, sine in self._sines.items():
            sine.stop()

    def set_fund_freq(self, freq: float):
        # self._set_sines(freq, self.get_overtones())
        # self.__fund_freq = freq
        self.__fund_freq.setValue(float(freq))

    def _set_sines(self, fund_freq: pyo.SigTo | pyo.Dummy, overtones):
        for overtone, amp in overtones.items():
            if overtone not in self._sines.keys():
                self._sines[overtone] = pyo.Sine(
                    freq=fund_freq * overtone, mul=self.__mul * amp
                )
            else:
                sine = self._sines[overtone]
                sine.mul = self.__mul * amp
                # sine.mul = amp
                # hopefully frequency doesnt need intervention and will listen to the class's __fund_freq
                # sine.freq = float(fund_freq) * overtone

    def set_overtones(self, overtones: dict):
        for overtone, amp in overtones.items():
            if type(overtone) != int:
                raise ValueError("Non-integer overtone was received")
            elif overtone <= 0:
                raise ValueError("attempted to set a non-positive overtone")
            # elif overtone == 1:
            #     logger.info("WARNING: overwriting the fundamental when resetting overtones")
        self.__overtones = overtones
        self._set_sines(self.__fund_freq, overtones)

    def set_random_overtones(self, limit: int):
        rand_overtones = self.create_rand_overtones(limit)
        self.set_overtones(rand_overtones)

    def create_rand_overtones(self, limit: int):
        """
        Creates random set of overtone strengths
        With overtones up to the given limit
        Currently, higher overtones are made less prominent
        args:
            limit: Number of tones present
        """
        rand_overtones = {}
        for i in range(2, limit):
            rand_overtones[i] = np.random.rand() * 0.3 * 1 / pow(i, 1.5)
        return rand_overtones

    def snap_to_nearest_note(self):
        logger.info("snapping note")
        this_log_freq = math.log10(self.get_fund_freq())
        closest_note = list(note_freq_dict.keys())[0]
        closest_log_freq = math.log10(note_freq_dict[closest_note])
        for note_name, note_freq in note_freq_dict.items():
            log_temp_freq = math.log10(note_freq)
            if abs(log_temp_freq - this_log_freq) < abs(
                closest_log_freq - this_log_freq
            ):
                closest_note = note_name
                closest_log_freq = log_temp_freq
        self.set_fund_freq(note_freq_dict[closest_note])
        logger.info(f"Snapping Tone to [{closest_note}]")

    def calc_tone_dissonance(self, other_tone):
        dissonance = 0
        for overtone, amp in self.__overtones.items(): # __overtones = {1:mul1, 2:mul2, 3:mul3, ...}
            for other_overtone, other_amp in other_tone.__overtones.items():
                dissonance += self._calc_sine_dissonance(
                    sine1_freq=self.get_fund_freq() * overtone,
                    sine1_amp=amp,
                    sine2_freq=other_tone.get_fund_freq() * other_overtone,
                    sine2_amp=other_amp,
                )
        return dissonance

    def _calc_sine_dissonance(self, sine1_freq, sine1_amp, sine2_freq, sine2_amp):
        # Optimization idea: stop calculating constants on every call
        # Used naming of variables in the paper the formula came from
        X = sine1_amp * sine2_amp
        Y = 2 * min(sine1_amp, sine2_amp) / (sine1_amp + sine2_amp)
        b1 = 3.5
        b2 = 5.75
        s1 = 0.0207
        s2 = 18.96
        s = 0.24 / (s1 * min(sine1_freq, sine2_freq) + s2)
        dist = abs(sine1_freq - sine2_freq)
        Z = pow(math.e, -1 * b1 * s * dist) - pow(math.e, -1 * b2 * s * dist)
        R = pow(X, 0.1) * 0.5 * pow(Y, 3.11) * Z
        return R

    def __eq__(self, other):
        if not isinstance(other, Tone):
            return False
        if self.get_fund_freq() != other.get_fund_freq():
            return False
        if self.get_mul() != other.get_mul():
            return False
        if self.get_overtones() != other.get_overtones():
            return False
        return True

    def __eq__(self, other):
        if not isinstance(other, Tone):
            return False
        if self.get_fund_freq() != other.get_fund_freq():
            return False
        if self.get_mul() != other.get_mul():
            return False
        if self.get_overtones() != other.get_overtones():
            return False
        return True

    def __repr__(self) -> str:

        repr_string = f"""
        Tone Status:
        Freq: {self.get_fund_freq()}
        """
        return repr_string