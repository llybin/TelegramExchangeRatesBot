from datetime import datetime
from decimal import Decimal

from sqlalchemy import inspect
from suite.test.testcases import SimpleTestCase

from ..exchanges.base import Pair, Currency, PairData
from ..helpers import rate_from_pair_data


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
        self.assertEqual(rate_obj.from_currency.code, 'BTC')
        self.assertEqual(rate_obj.to_currency.code, 'USD')
        self.assertEqual(rate_obj.rate, Decimal('1') / Decimal('3'))
        self.assertEqual(rate_obj.rate_open, Decimal('1') / Decimal('2'))
        self.assertEqual(rate_obj.low24h, Decimal('1') / Decimal('4'))
        self.assertEqual(rate_obj.high24h, Decimal('1') / Decimal('8'))
        self.assertEqual(rate_obj.last_trade_at, datetime(2019, 3, 9, 12))
