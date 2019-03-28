import datetime
from decimal import Decimal

import vcr

from suite.test.testcases import SimpleTestCase
from ..bittrex import BittrexExchange
from ..base import PairData, Pair, ECurrency
from ..exceptions import PairNotExistsException


my_vcr = vcr.VCR(
    cassette_library_dir='app/exchanges/tests/fixtures/vcr/bittrex',
    record_mode='once',
    decode_compressed_response=True,
)


class BittrexTest(SimpleTestCase):

    def test_name(self):
        self.assertEqual(BittrexExchange.name, 'Bittrex')

    @my_vcr.use_cassette('query_200')
    def test_list_currencies(self):
        currencies = BittrexExchange().list_currencies
        self.assertEqual(len(currencies), 239)
        self.assertTrue(ECurrency(code='BTC') in currencies)
        self.assertTrue(ECurrency(code='USD') in currencies)

    @my_vcr.use_cassette('query_200')
    def test_list_pairs(self):
        pairs = BittrexExchange().list_pairs
        self.assertEqual(len(pairs), 331)
        self.assertTrue(Pair(ECurrency('BTC'), ECurrency('USD')) in pairs)
        self.assertFalse(Pair(ECurrency('USD'), ECurrency('BTC')) in pairs)

    @my_vcr.use_cassette('query_200')
    def test_is_pair_exists(self):
        exchange = BittrexExchange()
        self.assertTrue(exchange.is_pair_exists(Pair(ECurrency('BTC'), ECurrency('USD'))))

        self.assertFalse(exchange.is_pair_exists(Pair(ECurrency('USD'), ECurrency('BTC'))))
        self.assertFalse(exchange.is_pair_exists(Pair(ECurrency('usd'), ECurrency('BTC'))))
        self.assertFalse(exchange.is_pair_exists(Pair(ECurrency('usd'), ECurrency('MONEY'))))

    @my_vcr.use_cassette('query_200')
    def test_is_currency_exists(self):
        exchange = BittrexExchange()
        self.assertTrue(exchange.is_currency_exists(ECurrency(code='BTC')))
        self.assertTrue(exchange.is_currency_exists(ECurrency(code='USD')))

        self.assertFalse(exchange.is_currency_exists(ECurrency(code='usd')))
        self.assertFalse(exchange.is_currency_exists(ECurrency(code='MONEY')))

    @my_vcr.use_cassette('query_200')
    def test_get_pair_info(self):
        pair = Pair(ECurrency('BTC'), ECurrency('USD'))
        self.assertEqual(
            BittrexExchange().get_pair_info(pair),
            PairData(
                pair=pair,
                rate=Decimal('3909.439'),
                rate_open=Decimal('3879.0'),
                low24h=Decimal('3773.806'),
                high24h=Decimal('3923.994'),
                last_trade_at=datetime.datetime(2019, 3, 9, 13, 47, 19, 0),
            )
        )

    @my_vcr.use_cassette('query_200')
    def test_get_pair_info_no_pair(self):
        pair = Pair(ECurrency('USD'), ECurrency('BTC'))
        with self.assertRaises(PairNotExistsException):
            BittrexExchange().get_pair_info(pair)
