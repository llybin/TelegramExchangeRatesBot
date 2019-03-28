from datetime import datetime
from decimal import Decimal

from suite.test.testcases import SimpleTestCase
from ..base import Pair, ECurrency, reverse_pair, reverse_pair_data, reverse_amount, PairData


class ReverseFunctionsTest(SimpleTestCase):

    def test_reverse_pair(self):
        pair = Pair(ECurrency('BTC'), ECurrency('USD'))
        reversed_pair = Pair(ECurrency('USD'), ECurrency('BTC'))

        self.assertEqual(reverse_pair(pair), reversed_pair)

    def test_reverse_amount(self):
        self.assertEqual(reverse_amount(Decimal('1') / Decimal('3')), Decimal('3'))

    def test_reverse_pair_data(self):
        pair_data = PairData(
            pair=Pair(ECurrency('BTC'), ECurrency('USD')),
            rate=Decimal('1') / Decimal('3'),
            last_trade_at=datetime(2019, 3, 9, 12),
            rate_open=Decimal('1') / Decimal('2'),
            low24h=Decimal('1') / Decimal('4'),
            high24h=Decimal('1') / Decimal('8'),
        )

        pair_data_reversed = PairData(
            pair=Pair(ECurrency('USD'), ECurrency('BTC')),
            rate=Decimal('3'),
            last_trade_at=datetime(2019, 3, 9, 12),
            rate_open=Decimal('2'),
            low24h=Decimal('4'),
            high24h=Decimal('8'),
        )

        self.assertEqual(reverse_pair_data(pair_data), pair_data_reversed)
