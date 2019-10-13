import datetime
from decimal import Decimal

import vcr
from suite.test.testcases import SimpleTestCase

from ..base import ECurrency, Pair, PairData
from ..bitfinex import BitfinexExchange
from ..exceptions import PairNotExistsException

my_vcr = vcr.VCR(
    cassette_library_dir="app/exchanges/tests/fixtures/vcr/bitfinex",
    record_mode="once",
    decode_compressed_response=True,
)


class BitfinexTest(SimpleTestCase):
    def test_name(self):
        self.assertEqual(BitfinexExchange.name, "Bitfinex")

    @my_vcr.use_cassette("symbols_200")
    def test_list_currencies(self):
        currencies = BitfinexExchange().list_currencies
        self.assertEqual(len(currencies), 160)
        self.assertTrue(ECurrency(code="BTC") in currencies)
        self.assertTrue(ECurrency(code="USD") in currencies)

    @my_vcr.use_cassette("symbols_200")
    def test_list_pairs(self):
        pairs = BitfinexExchange().list_pairs
        self.assertEqual(len(pairs), 421)
        self.assertTrue(Pair(ECurrency("BTC"), ECurrency("USD")) in pairs)
        self.assertFalse(Pair(ECurrency("USD"), ECurrency("BTC")) in pairs)

    @my_vcr.use_cassette("symbols_200")
    def test_is_pair_exists(self):
        exchange = BitfinexExchange()
        self.assertTrue(
            exchange.is_pair_exists(Pair(ECurrency("BTC"), ECurrency("USD")))
        )

        self.assertFalse(
            exchange.is_pair_exists(Pair(ECurrency("USD"), ECurrency("BTC")))
        )
        self.assertFalse(
            exchange.is_pair_exists(Pair(ECurrency("usd"), ECurrency("BTC")))
        )
        self.assertFalse(
            exchange.is_pair_exists(Pair(ECurrency("usd"), ECurrency("MONEY")))
        )

    @my_vcr.use_cassette("symbols_200")
    def test_is_currency_exists(self):
        exchange = BitfinexExchange()
        self.assertTrue(exchange.is_currency_exists(ECurrency(code="BTC")))
        self.assertTrue(exchange.is_currency_exists(ECurrency(code="USD")))

        self.assertFalse(exchange.is_currency_exists(ECurrency(code="usd")))
        self.assertFalse(exchange.is_currency_exists(ECurrency(code="MONEY")))

    @my_vcr.use_cassette("get_pair_200")
    def test_get_pair_info(self):
        pair = Pair(ECurrency("BTC"), ECurrency("USD"))
        self.assertEqual(
            BitfinexExchange().get_pair_info(pair),
            PairData(
                pair=pair,
                rate=Decimal("3996.05"),
                rate_open=None,
                low24h=Decimal("3850.0"),
                high24h=Decimal("4021.0"),
                last_trade_at=datetime.datetime(2019, 3, 9, 11, 21, 12, 996645),
            ),
        )

    @my_vcr.use_cassette("get_pair_200")
    def test_get_pair_info_no_pair(self):
        pair = Pair(ECurrency("USD"), ECurrency("BTC"))
        with self.assertRaises(PairNotExistsException):
            BitfinexExchange().get_pair_info(pair)
