from math import ceil


class KeyboardArrows(object):
    def __init__(self, data, height=4, width=5, offset=0):
        self.data = data
        self.offset = max(offset, 0)
        self.height = height
        self.width = width
        self.page_max = height * width
        self.be = " "
        self.bl = "◀"
        self.br = "▶"

    def prev(self):
        self.offset -= self.page_max
        self.offset += self.__left_button_available() + self.__right_button_available()
        self.offset = max(self.offset, 0)

    def next(self):
        self.offset -= self.__left_button_available() + self.__right_button_available()
        self.offset += self.page_max

    def __left_button_available(self):
        return 1 if self.offset > 0 else 0

    def __right_button_available(self):
        return 1 if len(self.data) > self.offset + self.page_max - 1 else 0

    def show(self):
        right_button = self.__right_button_available()
        left_button = self.__left_button_available()

        limit_data = self.page_max - (right_button + left_button)
        data_page = self.data[self.offset : self.offset + limit_data]

        data_page += [self.be] * (limit_data - len(data_page))

        if right_button:
            data_page.append(self.br)

        if left_button:
            data_page.insert(len(data_page) - 4, self.bl)

        keyboard = []
        for i in range(0, len(data_page), self.width):
            keyboard.append(data_page[i : i + self.width])

        return keyboard


class KeyboardSimpleClever(object):
    def __init__(self, data, width=3, height=None):
        self.data = data
        self.width = width
        self.height = height
        self.be = " "

    def show(self):
        if not self.height:
            self.height = int(ceil(len(self.data) / self.width))

        data_page = self.data
        data_page += [self.be] * (self.height * self.width - len(self.data))

        keyboard = []
        for i in range(0, len(self.data), self.width):
            keyboard.append(self.data[i : i + self.width])

        return keyboard
