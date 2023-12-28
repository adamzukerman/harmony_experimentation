"""BUG: Need to check if pyo server is already started"""
import pyo
import math
import numpy as np
from notes import note_freq_dict


class Tone:
    # tone_server = pyo.Server().boot() # should this be here inside a class?
    def __init__(self, fund_freq: float, mul: float, overtones: dict = {}):
        self.__fund_freq = fund_freq
        self.__mul = mul
        self.__overtones = overtones
        self.__overtones[1] = mul
        self._sines = []
        self.__generate_sines(self.__fund_freq, self.__overtones.copy())

    def copy(self):
        """Returns a deep copy of this Tone that not being played"""
        return Tone(self.__fund_freq, self.__mul, self.__overtones)

    def __generate_sines(self, fund_freq, overtones):
        self._sines = {
            overtone: pyo.Sine(freq=self.__fund_freq * overtone, mul=self.__mul * amp)
            for (overtone, amp) in self.__overtones.items()
        }

    def get_fund_freq(self):
        # how to make sure this can't be used to modify the object when copy is not allowed for int/float?
        return self.__fund_freq

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
        self._set_sines(freq, self.get_overtones())
        self.__fund_freq = freq

    def _set_sines(self, fund_freq, overtones):
        for overtone, amp in overtones.items():
            if overtone not in self._sines.keys():
                self._sines[overtone] = pyo.Sine(
                    freq=fund_freq * overtone, mul=self.__mul * amp
                )
            else:
                sine = self._sines[overtone]
                sine.mul = amp
                sine.freq = float(fund_freq) * overtone

    def set_overtones(self, overtones: dict):
        for overtone, amp in overtones.items():
            if type(overtone) != int:
                raise ValueError("Non-integer overtone was received")
            elif overtone <= 0:
                raise ValueError("attempted to set a non-positive overtone")
            # elif overtone == 1:
            #     print("WARNING: overwriting the fundamental when resetting overtones")
        self.__overtones = overtones
        self._set_sines(self.get_fund_freq(), overtones)

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
        closest_note = list(note_freq_dict.keys())[0]
        closest_log_freq = math.log10(note_freq_dict[closest_note])
        this_log_freq = math.log10(self.get_fund_freq())
        for note_name, note_freq in note_freq_dict.items():
            log_temp_freq = math.log10(note_freq)
            if abs(log_temp_freq - this_log_freq) < abs(closest_log_freq - this_log_freq):
                closest_note = note_name
                closest_log_freq = log_temp_freq
        self.set_fund_freq(note_freq_dict[closest_note])


    def calc_tone_dissonance(self, other_tone):
        dissonance = 0
        for sine in self._sines.values():
            for other_sine in other_tone._get_sines().values():
                dissonance += self._calc_sine_dissonance(sine, other_sine)
        return dissonance

    def _calc_sine_dissonance(self, note1, note2):
        # Optimization note: calculating constants on every call
        # Used naming of variables in the paper the formula came from
        X = note1.mul * note2.mul
        Y = 2 * min(note1.mul, note2.mul) / (note1.mul + note2.mul)
        b1 = 3.5
        b2 = 5.75
        s1 = 0.0207
        s2 = 18.96
        s = 0.24 / (s1 * min(note1.freq, note2.freq) + s2)
        dist = abs(note1.freq - note2.freq)
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