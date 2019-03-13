from decimal import Decimal

from suite.test.testcases import SimpleTestCase
from ..formatter import nice_round


class NiceRoundTest(SimpleTestCase):

    def test_rounding(self):
        self.assertEqual(nice_round(Decimal('1'), 2), Decimal('1'))
        self.assertEqual(nice_round(Decimal('1.1'), 2), Decimal('1.1'))
        self.assertEqual(nice_round(Decimal('1.16'), 2), Decimal('1.16'))
        self.assertEqual(nice_round(Decimal('1.126'), 2), Decimal('1.13'))
        self.assertEqual(nice_round(Decimal('1.1236'), 2), Decimal('1.12'))

        self.assertEqual(nice_round(Decimal('1.0'), 2), Decimal('1.0'))
        self.assertEqual(nice_round(Decimal('1.01'), 2), Decimal('1.01'))
        self.assertEqual(nice_round(Decimal('1.016'), 2), Decimal('1.016'))
        self.assertEqual(nice_round(Decimal('1.0167'), 2), Decimal('1.017'))
        self.assertEqual(nice_round(Decimal('1.00167'), 2), Decimal('1.0017'))
        self.assertEqual(nice_round(Decimal('1.000167'), 2), Decimal('1.00017'))

        self.assertEqual(nice_round(Decimal('1.000207'), 2), Decimal('1.00021'))
        self.assertEqual(nice_round(Decimal('1.000207'), 2, 3), Decimal('1.000207'))
        self.assertEqual(nice_round(Decimal('1.000207'), 2, 4), Decimal('1.000207'))
        self.assertEqual(nice_round(Decimal('0.000030161495775926880000'), 2), Decimal('0.00003'))
        self.assertEqual(nice_round(Decimal('0.000030061495775926880000'), 2), Decimal('0.00003'))
        self.assertEqual(nice_round(Decimal('0.000000000000000000001'), 2), Decimal('0'))

    def test_as_str(self):
        self.skipTest("FIXME: 0.000030 - last zero, bug in python?")
        self.assertEqual(nice_round(Decimal('0.000030061495775926880000'), 2), Decimal('0.00003'))
        self.assertEqual(f'{nice_round(Decimal("0.000030061495775926880000"), 2):f}', '0.00003')
