from decimal import Decimal
import re
import unittest

from app.parsers.number_format import (
    NUMBER_PATTERN_EU,
    NUMBER_PATTERN_US,
    NUMBER_PATTERN_ALL,
)


US_GOOD_CASES = {
    '1',
    '1,000.0001',
    '1,000.01',
    '1,000,000.01',
    '1,000',
    '100,000',
    '100',
    '1000',
    '1000000',
    '1000000.01',
    '1.1',
    '0.1',
    '1.01',
    '10.0',
    '10.0001',
    '00.1',
    '000.1',
    f'{"0" * 12}.{"0" * 12}',
    f'{"0" * 12}.1',
    f'{"0" * 12}',
    f'{"1" * 12}.{"1" * 12}',
    f'111{",000" * 3}',
    f'1{",000" * 3}',
    f'1{",000" * 3}.{"1" * 12}',
}

EU_GOOD_CASES = {
    '1',
    '1.000,0001',
    '1.000,01',
    '1.000.000,01',
    '1.000',
    '100.000',
    '100',
    '1000',
    '1000000',
    '1000000,01',
    '1,1',
    '0,1',
    '1,01',
    '10,0',
    '10,0001',
    '00,1',
    '000,1',
    f'{"0" * 12},{"0" * 12}',
    f'{"0" * 12},1',
    f'{"0" * 12}',
    f'{"1" * 12},{"1" * 12}',
    f'111{".000" * 3}',
    f'1{".000" * 3}',
    f'1{".000" * 3},{"1" * 12}',
}

BOTH_BAD_CASES = {
    '+1',
    '-1',
    '+1,000',
    '+1,000.00',
    '+1.000',
    '+1.000,00',
    '-1,000',
    '-1,000.00',
    '-1.000',
    '-1.000,00',
    '1.00.',
    '1.00.00',
    '1,00.00',
    '1.00,00',
    '1,00,00',
    '100,00,,',
    '100,00..',
    '10.0,00..',
    '.1',
    ',1',
    ' ',
    ',',
    ',',
    '',
    f'{"0"*13}.{"0"*12}',
    f'{"0"*13},{"0"*12}',
    f'{"0"*12}.{"0"*13}',
    f'{"0"*12},{"0"*13}',
    f'1111{",000" * 3}',
    f'1111{".000" * 3}',
    f'1{",000" * 4}',
    f'1{",000" * 4}.{"1" * 12}',
    f'1{".000" * 4}',
    f'1{".000" * 4},{"1" * 12}',
}

US_BAD_CASES = BOTH_BAD_CASES | {
    # EU
    '1.000,0001',
    '1.000,01',
    '1.000.000,01',
    '1000000,01',
    '1,1',
    '0,1',
    '1,01',
    '10,0',
    '10,0001',
    '00,1',
    '000,1',
    f'{"0" * 12},{"0" * 12}',
    f'{"0" * 12},1',
    f'{"1" * 12},{"1" * 12}',
    f'1{".000" * 3}',
    f'1{".000" * 3},{"1" * 12}',
}

EU_BAD_CASES = BOTH_BAD_CASES | {
    # US
    '1,000.0001',
    '1,000.01',
    '1,000,000.01',
    '1000000.01',
    '1.1',
    '0.1',
    '1.01',
    '10.0',
    '10.0001',
    '00.1',
    '000.1',
    f'{"0" * 12}.{"0" * 12}',
    f'{"0" * 12}.1',
    f'{"1" * 12}.{"1" * 12}',
    f'1{",000" * 3}',
    f'1{",000" * 3}.{"1" * 12}',
}


class NumberPatternUSTest(unittest.TestCase):
    mpt = f'^{NUMBER_PATTERN_US}$'

    def test_good(self):
        for case in US_GOOD_CASES:
            r = re.match(self.mpt, case)
            self.assertIsNotNone(r, case)
            self.assertEqual(r.group(0), case)

    def test_bad(self):
        for case in US_BAD_CASES:
            self.assertFalse(re.match(self.mpt, case))


class NumberPatternEUTest(unittest.TestCase):
    mpt = f'^{NUMBER_PATTERN_EU}$'

    def test_good(self):
        for case in EU_GOOD_CASES:
            r = re.match(self.mpt, case)
            self.assertIsNotNone(r, case)
            self.assertEqual(r.group(0), case)

    def test_bad(self):
        for case in EU_BAD_CASES:
            self.assertFalse(re.match(self.mpt, case))


class NumberPatternTest(unittest.TestCase):
    mpt = f'^{NUMBER_PATTERN_ALL}$'

    def test_good(self):
        for case in US_GOOD_CASES | EU_GOOD_CASES:
            r = re.match(self.mpt, case)
            self.assertIsNotNone(r, case)
            self.assertEqual(r.group(1), case)

    def test_bad(self):
        for case in BOTH_BAD_CASES:
            self.assertFalse(re.match(self.mpt, case))


class DecimalPrecTest(unittest.TestCase):
    def test_ok(self):
        num = Decimal('123456789012.123456789012345678901234567890') / Decimal(1)
        integer_part, fractional_part = str(num).split('.')
        self.assertEqual(len(integer_part), 12)
        self.assertEqual(len(fractional_part), 12)

        num = Decimal('12345678901.123456789012345678901234567890') / Decimal(1)
        integer_part, fractional_part = str(num).split('.')
        self.assertEqual(len(integer_part), 11)
        self.assertEqual(len(fractional_part), 13)
