from datetime import datetime
from decimal import Decimal

from sqlalchemy import inspect
from suite.test.testcases import SimpleTestCase

from ..models import Rate, Currency
from ..exchanges.base import Pair, Currency, PairData
from ..helpers import rate_from_pair_data, fill_rate_open


class RateFromPairDataTest(SimpleTestCase):
    def test_ok(self):
        pair_data = PairData(
            pair=Pair(Currency('BTC'), Currency('USD')),
            rate=Decimal('1') / Decimal('3'),
            last_trade_at=datetime(2019, 3, 9, 12),
            rate_open=Decimal('1') / Decimal('2'),
            low24h=Decimal('1') / Decimal('4'),
            high24h=Decimal('1') / Decimal('8'),
        )

        rate_obj = rate_from_pair_data(pair_data, exchange_id=1)

        inst = inspect(rate_obj)
        self.assertSetEqual(
            {c_attr.key for c_attr in inst.mapper.column_attrs},
            {
                'id',
                'exchange_id',
                'from_currency_id',
                'to_currency_id',
                'rate',
                'rate_open',
                'low24h',
                'high24h',
                'last_trade_at',
                'created_at',
                'modified_at',
            }
        )

        self.assertEqual(rate_obj.exchange_id, 1)
        self.assertEqual(rate_obj.from_currency.code, pair_data.pair.from_currency.code)
        self.assertEqual(rate_obj.to_currency.code, pair_data.pair.to_currency.code)
        self.assertEqual(rate_obj.rate, pair_data.rate)
        self.assertEqual(rate_obj.rate_open, pair_data.rate_open)
        self.assertEqual(rate_obj.low24h, pair_data.low24h)
        self.assertEqual(rate_obj.high24h, pair_data.high24h)
        self.assertEqual(rate_obj.last_trade_at, pair_data.last_trade_at)


# class FillRateOpenTest(SimpleTestCase):
#     def setUp(self):
#         self.current_rate = Rate(
#             from_currency=Currency(code='BTC'),
#             to_currency=Currency(code='USD'),
#             rate=Decimal('2'),
#             rate_open=Decimal('11'),
#             last_trade_at=datetime(2019, 3, 8, 11, 10, 0),
#         )
#
#         self.new_rate = Rate(
#             from_currency=Currency(code='BTC'),
#             to_currency=Currency(code='USD'),
#             rate=Decimal('1'),
#             last_trade_at=datetime(2019, 3, 9, 12, 11, 0),
#         )
#
#     def test_first_create_midnight_no_open_rate(self):
#         self.assertEqual(self.new_rate.rate_open, None)
#
#         self.new_rate.last_trade_at = datetime(2019, 3, 9, 0, 0, 0)
#
#         self.new_rate = fill_rate_open(new_rate=self.new_rate, current_rate=None)
#
#         self.assertEqual(self.new_rate.rate_open, self.new_rate.rate)
#
#     def test_first_create_not_midnight_no_open_rate(self):
#         self.assertEqual(self.new_rate.rate_open, None)
#
#         self.new_rate.last_trade_at = datetime(2019, 3, 9, 1, 0, 0)
#
#         self.new_rate = fill_rate_open(new_rate=self.new_rate, current_rate=None)
#
#         self.assertEqual(self.new_rate.rate_open, None)
#
#     def test_first_create_midnight_open_rate_exists(self):
#         self.new_rate.rate_open = Decimal('10')
#         self.new_rate.last_trade_at = datetime(2019, 3, 9, 0, 0, 0)
#
#         self.new_rate = fill_rate_open(new_rate=self.new_rate, current_rate=None)
#
#         self.assertEqual(self.new_rate.rate_open, Decimal('10'))
#
#     def test_first_create_not_midnight_open_rate_exists(self):
#         self.new_rate.rate_open = Decimal('10')
#         self.new_rate.last_trade_at = datetime(2019, 3, 9, 1, 0, 0)
#
#         self.new_rate = fill_rate_open(new_rate=self.new_rate, current_rate=None)
#
#         self.assertEqual(self.new_rate.rate_open, Decimal('10'))
#
#     def test_not_first_create_midnight_open_rate_exists(self):
#         self.new_rate.rate_open = Decimal('10')
#         self.new_rate.last_trade_at = datetime(2019, 3, 9, 0, 0, 0)
#
#         self.new_rate = fill_rate_open(new_rate=self.new_rate, current_rate=self.current_rate)
#
#         self.assertEqual(self.new_rate.rate_open, Decimal('10'))
#
#     def test_not_first_create_midnight_no_open_rate_first_set(self):
#         self.new_rate.last_trade_at = datetime(2019, 3, 10, 0, 0, 0)
#
#         self.new_rate = fill_rate_open(new_rate=self.new_rate, current_rate=self.current_rate)
#
#         self.assertEqual(self.new_rate.rate_open, Decimal('1'))
#
#     def test_not_first_create_not_midnight_no_open_rate_first_set(self):
#         self.new_rate.last_trade_at = datetime(2019, 3, 10, 1, 0, 0)
#
#         self.new_rate = fill_rate_open(new_rate=self.new_rate, current_rate=self.current_rate)
#
#         self.assertEqual(self.new_rate.rate_open, None)
#
#     def test_not_first_create_midnight_no_open_rate_not_first_set(self):
#         self.current_rate.last_trade_at = datetime(2019, 3, 10, 0, 5, 0)
#         self.new_rate.last_trade_at = datetime(2019, 3, 10, 0, 10, 0)
#
#         self.new_rate = fill_rate_open(new_rate=self.new_rate, current_rate=self.current_rate)
#
#         self.assertEqual(self.new_rate.rate_open, None)
