class CircularList:
    """This class was made for easier access to moving historical values"""

    def __init__(self, size: int, init_value=None):
        """
        Initializes a circular array
        """
        self.list = [None] * size
        self._index = 0
        self.set_all_values(init_value)

    def get_curr_value(self):
        return self.list[self._index]

    def get_index(self):
        return self._index

    def get_size(self):
        return len(self.list)

    def to_list(self):
        return self.list[self._index :].copy() + self.list[: self._index].copy()

    def advance(self, steps=1):
        self._index = (self._index + steps) % len(self.list)

    def set_all_values(self, value):
        for indx in range(len(self.list)):
            self.list[indx] = value

    def set_curr_value(self, value):
        self.list[self._index] = value

    def __len__(self):
        return len(self.list)
