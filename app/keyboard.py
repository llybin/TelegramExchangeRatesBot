import math


class KeyboardArrows(object):
    def __init__(self, data, height=4, width=5, offset=0):
        self.data = data
        self.offset = max(offset, 0)
        self.height = height
        self.width = width
        self.max = height * width
        self.be = ' '
        self.bl = '◀'
        self.br = '▶'

    def prev(self):
        self.offset -= self.max
        self.offset += (self.__left_button_avaiable() + self.__right_button_avaiable())
        self.offset = max(self.offset, 0)

    def next(self):
        self.offset -= (self.__left_button_avaiable() + self.__right_button_avaiable())
        self.offset += self.max

    def __left_button_avaiable(self):
        r = 1 if self.offset > 0 else 0
        return r

    def __right_button_avaiable(self):
        r = 1 if len(self.data) > self.offset + self.max - 1 else 0
        return r

    def show(self):
        b_right = self.__right_button_avaiable()
        b_left = self.__left_button_avaiable()

        _limit = self.max - (b_right + b_left)
        data_limited = self.data[self.offset:self.offset + _limit]

        for x in range(abs(len(data_limited) - _limit)):
            data_limited.append(self.be)

        if b_right:
            data_limited.append(self.br)

        if b_left:
            data_limited.insert(len(data_limited) - 4, self.bl)

        keyboard = []
        _i = 0
        for h in range(self.height):
            _t = []
            for w in range(self.width):
                _t.append(data_limited[_i])
                _i += 1
            keyboard.append(_t)

        return keyboard


class KeyboardSimpleClever(object):
    def __init__(self, data, width=3, height=None):
        self.data = data
        self.width = width
        self.height = height
        self.be = ' '

    def show(self):
        if not self.height:
            self.height = int(math.ceil(len(self.data) / self.width))
        for x in range(abs(len(self.data) - self.height * self.width)):
            self.data.append(self.be)

        keyboard = []
        _i = 0
        for h in range(self.height):
            _t = []
            for w in range(self.width):
                _t.append(self.data[_i])
                _i += 1
            keyboard.append(_t)

        return keyboard
