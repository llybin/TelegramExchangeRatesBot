import datetime
from decimal import Decimal

import vcr

from suite.test.testcases import SimpleTestCase
from ..openexchangerates import OpenExchangeRatesExchange
from ..base import PairData, Pair, Currency
from ..exceptions import PairNotExistsException


my_vcr = vcr.VCR(
    cassette_library_dir='app/exchanges/tests/fixtures/vcr/openexchangerates',
    record_mode='once',
    decode_compressed_response=True,
)


class OpenExchangeRatesTest(SimpleTestCase):

    @my_vcr.use_cassette('query_200')
    def test_list_currencies(self):
        currencies = OpenExchangeRatesExchange().list_currencies
        self.assertEqual(len(currencies), 172)
        self.assertTrue(Currency(code='EUR') in currencies)
        self.assertTrue(Currency(code='USD') in currencies)

    @my_vcr.use_cassette('query_200')
    def test_list_pairs(self):
        pairs = OpenExchangeRatesExchange().list_pairs
        self.assertEqual(len(pairs), 171)
        self.assertTrue(Pair(Currency('USD'), Currency('EUR')) in pairs)

    @my_vcr.use_cassette('query_200')
    def test_is_pair_exists(self):
        exchange = OpenExchangeRatesExchange()
        self.assertTrue(exchange.is_pair_exists(Pair(Currency('USD'), Currency('EUR'))))

        self.assertFalse(exchange.is_pair_exists(Pair(Currency('usd'), Currency('EUR'))))
        self.assertFalse(exchange.is_pair_exists(Pair(Currency('USD'), Currency('MONEY'))))

    @my_vcr.use_cassette('query_200')
    def test_is_currency_exists(self):
        exchange = OpenExchangeRatesExchange()
        self.assertTrue(exchange.is_currency_exists(Currency(code='EUR')))
        self.assertTrue(exchange.is_currency_exists(Currency(code='USD')))

        self.assertFalse(exchange.is_currency_exists(Currency(code='usd')))
        self.assertFalse(exchange.is_currency_exists(Currency(code='MONEY')))

    @my_vcr.use_cassette('query_200')
    def test_get_pair_info(self):
        pair = Pair(Currency('USD'), Currency('EUR'))
        self.assertEqual(
            OpenExchangeRatesExchange().get_pair_info(pair),
            PairData(
                pair=pair,
                rate=Decimal('0.8901'),
                rate_open=None,
                last_trade_at=datetime.datetime(2019, 3, 9, 11, 0, 8),
            )
        )

    @my_vcr.use_cassette('query_200')
    def test_get_pair_info_no_pair(self):
        pair = Pair(Currency('MONEY'), Currency('USD'))
        with self.assertRaises(PairNotExistsException):
            OpenExchangeRatesExchange().get_pair_info(pair)
