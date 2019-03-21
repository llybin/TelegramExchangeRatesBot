import datetime
from decimal import Decimal

import vcr

from suite.test.testcases import SimpleTestCase
from ..fixer import FixerExchange
from ..base import PairData, Pair, Currency
from ..exceptions import PairNotExistsException


my_vcr = vcr.VCR(
    cassette_library_dir='app/exchanges/tests/fixtures/vcr/fixer',
    record_mode='once',
    decode_compressed_response=True,
    filter_query_parameters=['access_key'],
)


class FixerTest(SimpleTestCase):

    def test_name(self):
        self.assertEqual(FixerExchange.name, 'Fixer')

    @my_vcr.use_cassette('query_200')
    def test_list_currencies(self):
        currencies = FixerExchange().list_currencies
        self.assertEqual(len(currencies), 169)
        self.assertTrue(Currency(code='EUR') in currencies)
        self.assertTrue(Currency(code='USD') in currencies)

    @my_vcr.use_cassette('query_200')
    def test_list_pairs(self):
        pairs = FixerExchange().list_pairs
        self.assertEqual(len(pairs), 168)
        self.assertTrue(Pair(Currency('EUR'), Currency('USD')) in pairs)

    @my_vcr.use_cassette('query_200')
    def test_is_pair_exists(self):
        exchange = FixerExchange()
        self.assertTrue(exchange.is_pair_exists(Pair(Currency('EUR'), Currency('USD'))))

        self.assertFalse(exchange.is_pair_exists(Pair(Currency('eur'), Currency('USD'))))
        self.assertFalse(exchange.is_pair_exists(Pair(Currency('eur'), Currency('MONEY'))))

    @my_vcr.use_cassette('query_200')
    def test_is_currency_exists(self):
        exchange = FixerExchange()
        self.assertTrue(exchange.is_currency_exists(Currency(code='EUR')))
        self.assertTrue(exchange.is_currency_exists(Currency(code='USD')))

        self.assertFalse(exchange.is_currency_exists(Currency(code='usd')))
        self.assertFalse(exchange.is_currency_exists(Currency(code='MONEY')))

    @my_vcr.use_cassette('query_200')
    def test_get_pair_info(self):
        pair = Pair(Currency('EUR'), Currency('USD'))
        self.assertEqual(
            FixerExchange().get_pair_info(pair),
            PairData(
                pair=pair,
                rate=Decimal('1.137314'),
                rate_open=None,
                last_trade_at=datetime.datetime(2019, 3, 21, 20, 47, 5),
            )
        )

    @my_vcr.use_cassette('query_200')
    def test_get_pair_info_no_pair(self):
        pair = Pair(Currency('MONEY'), Currency('EUR'))
        with self.assertRaises(PairNotExistsException):
            FixerExchange().get_pair_info(pair)
