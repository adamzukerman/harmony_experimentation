"""BUG: Need to check if pyo server is already started"""
import pyo
import numpy as np


class Tone:
    # tone_server = pyo.Server().boot() # should this be here inside a class?
    def __init__(self, fund_freq: float, mul: float, overtones: list = {}):
        self.__fund_freq = fund_freq
        self.__mul = mul
        self.__overtones = overtones
        self.__overtones[1] = mul
        self.set_overtones(self.__overtones)
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
    # def get_sines(self):
    #     """Returns the pyo Sines that make up this tone"""
    #     return self._sines

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
        for sine in self._sines:
            for overtone, sine in self._sines.items():
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
        # TODO: GENERATE SINES

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
        for i in range(2, 21):
            rand_overtones[i] = np.random.rand() * 0.3 * 1 / pow(i, 1.5)
        return rand_overtones
