import math
import time
import pyo
from tone import Tone

class ToneCollection:
    def __init__(self):
        self.active_tones = {}
        self.removed_tones = {}
        self.slctd_tone_id = None
        self._next_id = 0
        self.__time_selected_tone_changed = time.time()

    def copy(self, preserve_ids=False):
        if preserve_ids:
            return self.__copy_with_ids()

        new_collection = ToneCollection()
        for tone_id, tone in self:
            new_id = new_collection.add_tone(tone.copy())
            if self.slctd_tone_id == tone_id:
                new_collection.set_selected_tone(new_id)
        return new_collection

    def __copy_with_ids(self):
        new_collection = ToneCollection()
        for tone_id, tone in self:
            new_collection.active_tones[tone_id] = tone.copy()
            if self.slctd_tone_id == tone_id:
                new_collection.set_selected_tone(tone_id)
        return new_collection

    def add_tone(self, tone: Tone):
        self.active_tones[self._next_id] = tone
        if self.slctd_tone_id is None:
            print("Adding tone to an empty collection")
            self.set_selected_tone(self._next_id)
        self._next_id += 1
        return self._next_id - 1

    def remove_tone(self,  tone_id: int = None, tone: Tone = None):
        """
        Deletes the tone from the collection
        Defaults to using tone_id. Uses tone instead if not given tone_id
        """
        if len(self) < 2:
            print("skipped deleting tone becuse only one remains")
            return
        if tone_id == None and tone == None:
            raise ValueError("must provide either and id or a tone")
        elif tone_id == None:
            tone_id = self.get_id_from_tone(tone)
            if tone_id == None: raise ValueError("Given tone does not exist in the collection")
        self.select_next_tone()
        removed_tone = self.active_tones.pop(tone_id)
        self.removed_tones[tone_id] = removed_tone

    def flush_removed_tones(self):
        self.removed_tones = {}

    def get_closest_tone(self, target_freq: float):
        if len(self.active_tones) == 0:
            return None
        closest_tone = self.active_tones.values()[0]
        closest_log_freq = math.log10(closest_tone.get_fund_freq)
        log_target_freq = math.log10(freq)
        for id, tone in self.active_tones.items():
            log_tone_freq = math.log10(tone.get_fund_freq)
            if abs(log_target_freq - log_tone_freq) < abs(
                log_target_freq - closest_log_freq
            ):
                closest_tone = tone
                closest_log_freq = log_tone_freq
        return id, closest_tone

    def get_selected_tone_update_time(self):
        #unsure if this is an immutable primitive
        return self.__time_selected_tone_changed

    def set_selected_tone(self, tone_id: int):
        if tone_id not in self.active_tones.keys():
            raise ValueError("Tone not in collection")
        self.slctd_tone_id = tone_id
        self.__time_selected_tone_changed = time.time()
    
    def select_next_tone(self):
        ids = self.get_tone_ids()
        slctd_tone_indx = ids.index(self.slctd_tone_id)
        new_slctd_tone_indx = (slctd_tone_indx + 1) % len(ids)
        self.set_selected_tone(ids[new_slctd_tone_indx])

    def get_selected_tone(self):
        if self.slctd_tone_id is None:
            return None
        return self.active_tones[self.slctd_tone_id]

    def get_selected_tone_id(self):
        return self.slctd_tone_id

    def get_tones(self) -> list:
        return list(self.active_tones.values())

    def get_tone(self, tone_id):
        result = self.active_tones.get(tone_id)
        if result == None:
            raise ValueError(f"Tone ID {tone_id} does not exist in the collection")
        return result

    def get_tone_ids(self) -> list:
        return list(self.active_tones.keys())

    def get_tone_by_index(self, index):
        if index >= len(self.active_tones):
            return None
        return list(self.active_tones.values())[index]

    def get_id_from_tone(self, tone):
        for id, comp_tone in self:
            if comp_tone == tone:
                return id
        return None

    def get_lowest_tone(self):
        lowest_freq = None
        lowest_tone = None
        for tone_id, tone in self:
            if lowest_freq == None or lowest_freq > tone.get_fund_freq():
                lowest_freq = tone.get_fund_freq()
                lowest_tone = tone
        return lowest_tone

    def play_all(self):
        for tone in self.active_tones.values():
            tone.out()

    def play_tone(self, tone_id):
        tone = self.active_tones.get(tone_id)
        if tone == None:
            raise ValueError(f"tone_id: {tone_id} not in collection")
        tone.out()

    def stop_all(self):
        for tone in self.active_tones:
            tone.stop()

    def calc_dissonance(self):
        diss = 0
        for note1 in self.active_tones.values():
            for note2 in self.active_tones.values():
                diss += note1.calc_tone_dissonance(note2)
        return diss

    def __len__(self):
        return len(self.active_tones)

    def __iter__(self):
        return self.active_tones.items().__iter__()

    def reduce_dissonance(self):
        """
        Goes through ids_to_resolve and for each tone in the collection
        it will find the least dissonant frequency within a whole-step of the current frequency
        """
        # Use a temporary collection so none of the played tones are adjusted during the algorithm
        temp_collection = self.copy(preserve_ids=True)
        ids_to_resolve = self.get_tone_ids()
        lowest_tone_id = self.get_id_from_tone(self.get_lowest_tone())
        resolved_tone_collection = self.__reduce_dissonance_helper(temp_collection, ids_to_resolve, lowest_tone_id)
        for tone_id, tone in self:
            tone.set_fund_freq(resolved_tone_collection.get_tone(tone_id).get_fund_freq())

    def __reduce_dissonance_helper(self, temp_collection, ids_to_resolve, lowest_tone_id):
        #base case
        if not ids_to_resolve:
            print("finished finding a resolution")
            return temp_collection

        freq_mul_options = [-2/12, -1/12, 0, 1/12, 2/12]

        next_tone_id = ids_to_resolve.pop()
        next_tone = temp_collection.get_tone(next_tone_id)
        # skip to the next one if we are looking at the lowest tone
        if next_tone_id == lowest_tone_id:
            print("skipping the lowest tone")
            return self.__reduce_dissonance_helper(temp_collection, ids_to_resolve, lowest_tone_id)

        orig_frequency = next_tone.get_fund_freq()
        min_dissonance = temp_collection.calc_dissonance()
        selected_adjustment = 0
        # Find the frequency adjustment factor that minimizes the dissonance and apply the adjustment factor
        for adjustment in freq_mul_options:
            next_tone.set_fund_freq(orig_frequency * pow(2, adjustment))
            new_dissonance = temp_collection.calc_dissonance()
            if temp_collection.calc_dissonance() < min_dissonance:
                selected_adjustment = adjustment
                min_dissonance = new_dissonance
        next_tone.set_fund_freq(orig_frequency * pow(2, selected_adjustment))
        return self.__reduce_dissonance_helper(temp_collection, ids_to_resolve, lowest_tone_id)

    def increase_dissonance(self):
        """
        Goes through ids_to_unresolve and for each tone in the collection
        it will find the most dissonant frequency within a whole-step of the current frequency
        """
        # Use a temporary collection so none of the played tones are adjusted during the algorithm
        temp_collection = self.copy(preserve_ids=True)
        ids_to_unresolve = self.get_tone_ids()
        lowest_tone_id = self.get_id_from_tone(self.get_lowest_tone())
        unresolved_tone_collection = self.__increase_dissonance_helper(temp_collection, ids_to_unresolve, lowest_tone_id)
        for tone_id, tone in self:
            tone.set_fund_freq(unresolved_tone_collection.get_tone(tone_id).get_fund_freq())


    def __increase_dissonance_helper(self, temp_collection, ids_to_unresolve, lowest_tone_id):
        #base case
        if not ids_to_unresolve:
            print("finished finding a non-resolution")
            return temp_collection

        freq_mul_options = [-2/12, -1/12, 0, 1/12, 2/12]

        next_tone_id = ids_to_unresolve.pop()
        next_tone = temp_collection.get_tone(next_tone_id)
        # skip to the next one if we are looking at the lowest tone
        if next_tone_id == lowest_tone_id:
            print("skipping the lowest tone")
            return self.__increase_dissonance_helper(temp_collection, ids_to_unresolve, lowest_tone_id)

        min_freq = temp_collection.get_tone(lowest_tone_id).get_fund_freq()
        orig_frequency = next_tone.get_fund_freq()
        max_dissonance = temp_collection.calc_dissonance()
        selected_adjustment = 0
        # Find the frequency adjustment factor that minimizes the dissonance and apply the adjustment factor without going below min freq
        for adjustment in freq_mul_options:
            next_tone.set_fund_freq(orig_frequency * pow(2, adjustment))
            new_dissonance = temp_collection.calc_dissonance()
            if next_tone.get_fund_freq() < min_freq:
                continue
            if new_dissonance > max_dissonance:
                selected_adjustment = adjustment
                max_dissonance = new_dissonance
        next_tone.set_fund_freq(orig_frequency * pow(2, selected_adjustment))
        return self.__increase_dissonance_helper(temp_collection, ids_to_unresolve, lowest_tone_id)


    def __repr__(self) -> str:
        num_tones = len(self.active_tones)
        tones = self.active_tones
        selected_tone_id = self.slctd_tone_id
        selected_tone = self.active_tones.get(selected_tone_id)
        repr_string = f"""
        Status of tone collection at time ({time.time()})-----------------------------------------
        Number of tones in collection: {num_tones}
        Selected tone id: {selected_tone_id}
        Selected tone: {selected_tone}
        Tones in collection: {tones}
        Time of last modification: {self.__time_selected_tone_changed}

        """
        return repr_string