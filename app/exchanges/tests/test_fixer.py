import datetime
from decimal import Decimal

import vcr

from suite.test.testcases import SimpleTestCase
from ..fixer import FixerExchange
from ..base import PairData, Pair, ECurrency
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
        self.assertTrue(ECurrency(code='EUR') in currencies)
        self.assertTrue(ECurrency(code='USD') in currencies)

    @my_vcr.use_cassette('query_200')
    def test_list_pairs(self):
        pairs = FixerExchange().list_pairs
        self.assertEqual(len(pairs), 168)
        self.assertTrue(Pair(ECurrency('EUR'), ECurrency('USD')) in pairs)

    @my_vcr.use_cassette('query_200')
    def test_is_pair_exists(self):
        exchange = FixerExchange()
        self.assertTrue(exchange.is_pair_exists(Pair(ECurrency('EUR'), ECurrency('USD'))))

        self.assertFalse(exchange.is_pair_exists(Pair(ECurrency('eur'), ECurrency('USD'))))
        self.assertFalse(exchange.is_pair_exists(Pair(ECurrency('eur'), ECurrency('MONEY'))))

    @my_vcr.use_cassette('query_200')
    def test_is_currency_exists(self):
        exchange = FixerExchange()
        self.assertTrue(exchange.is_currency_exists(ECurrency(code='EUR')))
        self.assertTrue(exchange.is_currency_exists(ECurrency(code='USD')))

        self.assertFalse(exchange.is_currency_exists(ECurrency(code='usd')))
        self.assertFalse(exchange.is_currency_exists(ECurrency(code='MONEY')))

    @my_vcr.use_cassette('query_200')
    def test_get_pair_info(self):
        pair = Pair(ECurrency('EUR'), ECurrency('USD'))
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
        pair = Pair(ECurrency('MONEY'), ECurrency('EUR'))
        with self.assertRaises(PairNotExistsException):
            FixerExchange().get_pair_info(pair)
