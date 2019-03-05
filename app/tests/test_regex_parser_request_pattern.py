import unittest

from app.parsers.regex_parser import (
    PRICE_REQUEST_PATTERN,
    PRICE_REQUEST_LEFT_AMOUNT,
    PRICE_REQUEST_LEFT_CURRENCY,
    PRICE_REQUEST_RIGHT_CURRENCY,
    PRICE_REQUEST_RIGHT_AMOUNT,
)


class PriceRequestPatternTest(unittest.TestCase):
    def test_good(self):
        cases = [
            ('usd', None, 'usd', None, None),
            ('usdrubthb', None, 'usdrubthb', None, None),
            ('12usd', '12', 'usd', None, None),
            ('12 usd', '12', 'usd', None, None),
            ('usd12', None, None, 'usd', '12'),
            ('usd 12', None, None, 'usd', '12'),
            ('usdrub', None, 'usdrub', None, None),
            ('usd rub', None, 'usd rub', None, None),
            ('12usdrub', '12', 'usdrub', None, None),
            ('12 usd rub', '12', 'usd rub', None, None),
            ('usdrub12', None, None, 'usdrub', '12'),
            ('usd rub 12', None, None, 'usd rub', '12'),
            ('1,000usdrub', '1,000', 'usdrub', None, None),
            ('1,000 usd rub', '1,000', 'usd rub', None, None),
            ('usdrub1,000', None, None, 'usdrub', '1,000'),
            ('usd rub 1,000', None, None, 'usd rub', '1,000'),
            ('1.000usdrub', '1.000', 'usdrub', None, None),
            ('1.000 usd rub', '1.000', 'usd rub', None, None),
            ('usdrub1.000', None, None, 'usdrub', '1.000'),
            ('usd rub 1.000', None, None, 'usd rub', '1.000'),
            ('usd = rub', None, 'usd = rub', None, None),
            ('12 usd = rub', '12', 'usd = rub', None, None),
            ('usd = rub 12', None, None, 'usd = rub', '12'),
            ('usd=rub', None, 'usd=rub', None, None),
            ('12usd=rub', '12', 'usd=rub', None, None),
            ('usd=rub12', None, None, 'usd=rub', '12'),
            ('usd in rub', None, 'usd in rub', None, None),
            ('12 usd in rub', '12', 'usd in rub', None, None),
            ('usd in rub 12', None, None, 'usd in rub', '12'),
            ('usd to rub', None, 'usd to rub', None, None),
            ('12 usd to rub', '12', 'usd to rub', None, None),
            ('usd to rub 12', None, None, 'usd to rub', '12'),
            ('abcde', None, 'abcde', None, None),
            ('abcdeabcde', None, 'abcdeabcde', None, None),
            (f'{"1" * 12}.{"1" * 8}abcdeabcde', '111111111111.11111111', 'abcdeabcde', None, None),
            (f'abcdeabcde{"1" * 12}.{"1" * 8}', None, None, 'abcdeabcde', '111111111111.11111111'),
            (f'1{",000" * 3}.{"1" * 8}abcdeabcde', '1,000,000,000.11111111', 'abcdeabcde', None, None),
            (f'abcdeabcde1{",000" * 3}.{"1" * 8}', None, None, 'abcdeabcde', '1,000,000,000.11111111'),
            (f'{"1" * 12},{"1" * 8}abcdeabcde', '111111111111,11111111', 'abcdeabcde', None, None),
            (f'abcdeabcde{"1" * 12},{"1" * 8}', None, None, 'abcdeabcde', '111111111111,11111111'),
            (f'1{".000" * 3},{"1" * 8}abcdeabcde', '1.000.000.000,11111111', 'abcdeabcde', None, None),
            (f'abcdeabcde1{".000" * 3},{"1" * 8}', None, None, 'abcdeabcde', '1.000.000.000,11111111'),
            (f'111{",000" * 3}.{"1" * 8}abcdeabcde', '111,000,000,000.11111111', 'abcdeabcde', None, None),
            (f'abcdeabcde111{",000" * 3}.{"1" * 8}', None, None, 'abcdeabcde', '111,000,000,000.11111111'),
        ]
        for case, la, lc, rc, ra in cases:
            obj = PRICE_REQUEST_PATTERN.match(case)
            self.assertIsNotNone(obj, case)

            g = obj.groups()

            self.assertEqual(g[PRICE_REQUEST_LEFT_AMOUNT], la)
            self.assertEqual(g[PRICE_REQUEST_LEFT_CURRENCY], lc)
            self.assertEqual(g[PRICE_REQUEST_RIGHT_CURRENCY], rc)
            self.assertEqual(g[PRICE_REQUEST_RIGHT_AMOUNT], ra)

    def test_bad(self):
        cases = [
            'abcdeabcdea',
            'abcde abcdea',
            'abcde abcde a',
            'usd rub thb',
            'usd 12 rub',
            '12 usd rub 12',
            'usd ? rub',
            'usd > rub',
            f'{"1" * 13}.{"1" * 8}abcdeabcde'
            f'{"1" * 12}.{"1" * 9}abcdeabcde'
            f'{"1" * 13}.{"1" * 9}abcdeabcde'
            f'abcdeabcde{"1" * 13}.{"1" * 8}'
            f'abcdeabcde{"1" * 12}.{"1" * 9}'
            f'abcdeabcde{"1" * 13}.{"1" * 9}'
            f'1{",000" * 4}.{"1" * 8}abcdeabcde'
            f'1{",000" * 3}.{"1" * 9}abcdeabcde'
            f'1{",000" * 4}.{"1" * 9}abcdeabcde'
            f'1{".000" * 4},{"1" * 8}abcdeabcde'
            f'1{".000" * 3},{"1" * 9}abcdeabcde'
            f'1{".000" * 4},{"1" * 9}abcdeabcde'
            f'abcdeabcde1{",000" * 4}.{"1" * 8}'
            f'abcdeabcde1{",000" * 3}.{"1" * 9}'
            f'abcdeabcde1{",000" * 4}.{"1" * 9}'
            f'abcdeabcde1{".000" * 4},{"1" * 8}'
            f'abcdeabcde1{".000" * 3},{"1" * 9}'
            f'abcdeabcde1{".000" * 4},{"1" * 9}'
            f'1111{",000" * 3}.{"1" * 8}abcdeabcde'
            'abcdeabcde1111{",000" * 3}.{"1" * 8}'
            f'{"1" * 13},{"1" * 8}abcdeabcde'
            f'abcdeabcde{"1" * 13},{"1" * 8}'
            f'{"1" * 13}.{"1" * 8}abcdeabcde'
            f'abcdeabcde{"1" * 13}.{"1" * 8}'
        ]
        for case in cases:
            obj = PRICE_REQUEST_PATTERN.match(case)
            self.assertIsNone(obj, case)
