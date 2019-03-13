import unittest

from ..keyboard import KeyboardArrows


class TestKeyboardArrows(unittest.TestCase):
    def setUp(self):
        self.data = list(range(1, 56))

    def test_no_page_ok(self):
        self.assertEqual(
            KeyboardArrows(self.data).show(),
            [
                [1, 2, 3, 4, 5],
                [6, 7, 8, 9, 10],
                [11, 12, 13, 14, 15],
                [16, 17, 18, 19, '▶']
            ])

    def test_ok(self):
        self.assertEqual(
            KeyboardArrows(self.data, offset=0).show(),
            [
                [1, 2, 3, 4, 5],
                [6, 7, 8, 9, 10],
                [11, 12, 13, 14, 15],
                [16, 17, 18, 19, '▶']
            ])

        self.assertEqual(
            KeyboardArrows(self.data, offset=19).show(),
            [
                [20, 21, 22, 23, 24],
                [25, 26, 27, 28, 29],
                [30, 31, 32, 33, 34],
                ['◀', 35, 36, 37, '▶']
            ])

        self.assertEqual(
            KeyboardArrows(self.data, offset=37).show(),
            [
                [38, 39, 40, 41, 42],
                [43, 44, 45, 46, 47],
                [48, 49, 50, 51, 52],
                ['◀', 53, 54, 55, ' ']
            ])

    # def test_empty_data_ok(self):
    #     self.assertEqual(
    #         KeyboardArrows([], offset=0).show(),
    #         [
    #             [' ', ' ', ' ', ' ', ' '],
    #             [' ', ' ', ' ', ' ', ' '],
    #             [' ', ' ', ' ', ' ', ' '],
    #             [' ', ' ', ' ', ' ', ' ']
    #         ])
    #
    #     self.assertEqual(
    #         KeyboardArrows([], offset=19).show(),
    #         [
    #             [' ', ' ', ' ', ' ', ' '],
    #             [' ', ' ', ' ', ' ', ' '],
    #             [' ', ' ', ' ', ' ', ' '],
    #             [' ', ' ', ' ', ' ', ' ']
    #         ])

    def test_scroll_page_ok(self):
        k = KeyboardArrows(self.data, offset=0)

        self.assertEqual(
            k.show(),
            [
                [1, 2, 3, 4, 5],
                [6, 7, 8, 9, 10],
                [11, 12, 13, 14, 15],
                [16, 17, 18, 19, '▶']
            ])

        k.next()

        self.assertEqual(
            k.show(),
            [
                [20, 21, 22, 23, 24],
                [25, 26, 27, 28, 29],
                [30, 31, 32, 33, 34],
                ['◀', 35, 36, 37, '▶']
            ])

        k.prev()

        self.assertEqual(
            k.show(),
            [
                [1, 2, 3, 4, 5],
                [6, 7, 8, 9, 10],
                [11, 12, 13, 14, 15],
                [16, 17, 18, 19, '▶']
            ])

        k.prev()

        self.assertEqual(
            k.show(),
            [
                [1, 2, 3, 4, 5],
                [6, 7, 8, 9, 10],
                [11, 12, 13, 14, 15],
                [16, 17, 18, 19, '▶']
            ])

        k.next()

        self.assertEqual(
            k.show(),
            [
                [20, 21, 22, 23, 24],
                [25, 26, 27, 28, 29],
                [30, 31, 32, 33, 34],
                ['◀', 35, 36, 37, '▶']
            ])

        k.next()

        self.assertEqual(
            k.show(),
            [
                [38, 39, 40, 41, 42],
                [43, 44, 45, 46, 47],
                [48, 49, 50, 51, 52],
                ['◀', 53, 54, 55, ' ']
            ])

        # ?
        # k.next()
        #
        # self.assertEqual(
        #     k.show(),
        #     [
        #         [' ', ' ', ' ', ' ', ' '],
        #         [' ', ' ', ' ', ' ', ' '],
        #         [' ', ' ', ' ', ' ', ' '],
        #         ['◀', ' ', ' ', ' ', ' ']
        #     ])
        #
        # k.prev()
        #
        # self.assertEqual(
        #     k.show(),
        #     [
        #         [38, 39, 40, 41, 42],
        #         [43, 44, 45, 46, 47],
        #         [48, 49, 50, 51, 52],
        #         ['◀', 53, 54, 55, ' ']
        #     ])

    def test_not_full_page_ok(self):
        data = list(range(1, 7))

        self.assertEqual(
            KeyboardArrows(data).show(),
            [
                [1, 2, 3, 4, 5],
                [6, ' ', ' ', ' ', ' '],
                [' ', ' ', ' ', ' ', ' '],
                [' ', ' ', ' ', ' ', ' ']
            ])

    def test_minus_page_ok(self):
        self.assertEqual(
            KeyboardArrows(self.data, offset=-10).show(),
            [
                [1, 2, 3, 4, 5],
                [6, 7, 8, 9, 10],
                [11, 12, 13, 14, 15],
                [16, 17, 18, 19, '▶']
            ])

    def test_over_page_ok(self):
        self.assertEqual(
            KeyboardArrows(self.data, offset=55).show(),
            [
                [' ', ' ', ' ', ' ', ' '],
                [' ', ' ', ' ', ' ', ' '],
                [' ', ' ', ' ', ' ', ' '],
                ['◀', ' ', ' ', ' ', ' ']
            ])
