import datetime
from decimal import Decimal

import vcr
from freezegun import freeze_time

from suite.test.testcases import SimpleTestCase
from ..bx_in_th import BxInThExchange
from ..base import PairData, Pair, Currency
from ..exceptions import PairNotExistsException


my_vcr = vcr.VCR(
    cassette_library_dir='app/exchanges/tests/fixtures/vcr/bx_in_th',
    record_mode='once',
    decode_compressed_response=True,
)


class BxInThTest(SimpleTestCase):

    def test_name(self):
        self.assertEqual(BxInThExchange.name, '[bx.in.th](https://bx.in.th/ref/s9c3HU/)')

    @my_vcr.use_cassette('query_200')
    def test_list_currencies(self):
        currencies = BxInThExchange().list_currencies
        self.assertEqual(len(currencies), 27)
        self.assertTrue(Currency(code='BTC') in currencies)
        self.assertTrue(Currency(code='THB') in currencies)

    @my_vcr.use_cassette('query_200')
    def test_list_pairs(self):
        pairs = BxInThExchange().list_pairs
        self.assertEqual(len(pairs), 28)
        self.assertTrue(Pair(Currency('BTC'), Currency('THB')) in pairs)
        self.assertFalse(Pair(Currency('THB'), Currency('BTC')) in pairs)

    @my_vcr.use_cassette('query_200')
    def test_is_pair_exists(self):
        exchange = BxInThExchange()
        self.assertTrue(exchange.is_pair_exists(Pair(Currency('BTC'), Currency('THB'))))

        self.assertFalse(exchange.is_pair_exists(Pair(Currency('THB'), Currency('BTC'))))
        self.assertFalse(exchange.is_pair_exists(Pair(Currency('thb'), Currency('BTC'))))
        self.assertFalse(exchange.is_pair_exists(Pair(Currency('btc'), Currency('MONEY'))))

    @my_vcr.use_cassette('query_200')
    def test_is_currency_exists(self):
        exchange = BxInThExchange()
        self.assertTrue(exchange.is_currency_exists(Currency(code='BTC')))
        self.assertTrue(exchange.is_currency_exists(Currency(code='THB')))

        self.assertFalse(exchange.is_currency_exists(Currency(code='thb')))
        self.assertFalse(exchange.is_currency_exists(Currency(code='MONEY')))

    @my_vcr.use_cassette('query_200')
    @freeze_time("2019-03-17 22:14:15", tz_offset=0)
    def test_get_pair_info(self):
        pair = Pair(Currency('BTC'), Currency('THB'))
        self.assertEqual(
            BxInThExchange().get_pair_info(pair),
            PairData(
                pair=pair,
                rate=Decimal('124510.8'),
                rate_open=None,
                last_trade_at=datetime.datetime(2019, 3, 17, 22, 14, 15, 0),
            )
        )

    @my_vcr.use_cassette('query_200')
    def test_get_pair_info_no_pair(self):
        pair = Pair(Currency('USD'), Currency('BTC'))
        with self.assertRaises(PairNotExistsException):
            BxInThExchange().get_pair_info(pair)
