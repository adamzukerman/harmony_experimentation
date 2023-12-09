"""BUG: Need to check if pyo server is already started"""
import pyo
import math
import numpy as np


class Tone:
    # tone_server = pyo.Server().boot() # should this be here inside a class?
    def __init__(self, fund_freq: float, mul: float, overtones: list = {}):
        self.__fund_freq = fund_freq
        self.__mul = mul
        self.__overtones = overtones
        self.__overtones[1] = mul
        self._sines = []
        self.__generate_sines(self.__fund_freq, self.__overtones)

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
        # WARNING does not work if __fund_freq is 0
        # I should just recalculate all the sines
        self._set_sines(freq, self.get_overtones())
        self.__fund_freq = freq
        ####### FIX ##########

    def _set_sines(self, fund_freq, overtones):
        for overtone, amp in overtones.items():
            if overtone not in self._sines.keys():
                self._sines[overtone] = pyo.Sine(
                    freq=fund_freq * overtone, mul=self.__mul * amp
                )
            else:
                sine = self._sines[overtone]
                sine.mul = amp
                sine.freq = fund_freq * overtone

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
        # if R != 0:
        #     print("R:", R)
        # if R == 0 and note1.freq != note2.freq:
        #     print("Dissonance should not be 0!")
        # elif R == 0:
        #     # print("R should be 0o??")
        #     pass
        return R
