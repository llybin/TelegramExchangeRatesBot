import datetime
from decimal import Decimal

import vcr
from freezegun import freeze_time

from suite.test.testcases import SimpleTestCase
from ..sp_today import SpTodayExchange
from ..base import PairData, Pair, ECurrency
from ..exceptions import PairNotExistsException


my_vcr = vcr.VCR(
    cassette_library_dir='app/exchanges/tests/fixtures/vcr/sp_today',
    record_mode='once',
    decode_compressed_response=True,
)


class SpTodayExchangeTest(SimpleTestCase):

    def test_name(self):
        self.assertEqual(SpTodayExchange.name, 'sp-today')

    @my_vcr.use_cassette('query_200')
    def test_list_currencies(self):
        currencies = SpTodayExchange().list_currencies
        self.assertEqual(len(currencies), 18)
        self.assertTrue(ECurrency(code='SYP') in currencies)
        self.assertTrue(ECurrency(code='USD') in currencies)

    @my_vcr.use_cassette('query_200')
    def test_list_pairs(self):
        pairs = SpTodayExchange().list_pairs
        self.assertEqual(len(pairs), 17)
        self.assertTrue(Pair(ECurrency('USD'), ECurrency('SYP')) in pairs)
        self.assertTrue(Pair(ECurrency('EUR'), ECurrency('SYP')) in pairs)
        self.assertFalse(Pair(ECurrency('EUR'), ECurrency('USD')) in pairs)

    @my_vcr.use_cassette('query_200')
    def test_is_pair_exists(self):
        exchange = SpTodayExchange()
        self.assertTrue(exchange.is_pair_exists(Pair(ECurrency('USD'), ECurrency('SYP'))))

        self.assertFalse(exchange.is_pair_exists(Pair(ECurrency('SYP'), ECurrency('EUR'))))
        self.assertFalse(exchange.is_pair_exists(Pair(ECurrency('usd'), ECurrency('syp'))))
        self.assertFalse(exchange.is_pair_exists(Pair(ECurrency('syp'), ECurrency('MONEY'))))

    @my_vcr.use_cassette('query_200')
    def test_is_currency_exists(self):
        exchange = SpTodayExchange()
        self.assertTrue(exchange.is_currency_exists(ECurrency(code='SYP')))
        self.assertTrue(exchange.is_currency_exists(ECurrency(code='USD')))
        self.assertTrue(exchange.is_currency_exists(ECurrency(code='EUR')))

        self.assertFalse(exchange.is_currency_exists(ECurrency(code='thb')))
        self.assertFalse(exchange.is_currency_exists(ECurrency(code='MONEY')))

    @my_vcr.use_cassette('query_200')
    @freeze_time("2019-03-17 22:14:15", tz_offset=0)
    def test_get_pair_info(self):
        pair = Pair(ECurrency('USD'), ECurrency('SYP'))
        self.assertEqual(
            SpTodayExchange().get_pair_info(pair),
            PairData(
                pair=pair,
                rate=Decimal('550'),
                rate_open=None,
                last_trade_at=datetime.datetime(2019, 3, 17, 22, 14, 15, 0),
            )
        )

    @my_vcr.use_cassette('query_200')
    def test_get_pair_info_no_pair(self):
        pair = Pair(ECurrency('SYP'), ECurrency('BTC'))
        with self.assertRaises(PairNotExistsException):
            SpTodayExchange().get_pair_info(pair)
