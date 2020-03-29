from datetime import datetime
from decimal import Decimal

from vcr import VCR

from app.exchanges.base import ECurrency, Pair, PairData
from app.exchanges.bittrex import BittrexExchange
from app.exchanges.exceptions import PairNotExistsException
from suite.test.testcases import SimpleTestCase

my_vcr = VCR(
    cassette_library_dir="app/exchanges/tests/fixtures/vcr/bittrex",
    record_mode="once",
    decode_compressed_response=True,
)


class BittrexTest(SimpleTestCase):
    def test_name(self):
        self.assertEqual(
            BittrexExchange.name,
            "[bittrex.com](https://bittrex.com/Account/Register?referralCode=YIV-CNI-13Q)",
        )

    @my_vcr.use_cassette("query_200.yaml")
    def test_list_currencies(self):
        currencies = BittrexExchange().list_currencies
        self.assertEqual(len(currencies), 239)
        self.assertTrue(ECurrency(code="BTC") in currencies)
        self.assertTrue(ECurrency(code="USD") in currencies)

    @my_vcr.use_cassette("query_200.yaml")
    def test_list_pairs(self):
        pairs = BittrexExchange().list_pairs
        self.assertEqual(len(pairs), 331)
        self.assertTrue(Pair(ECurrency("BTC"), ECurrency("USD")) in pairs)
        self.assertFalse(Pair(ECurrency("USD"), ECurrency("BTC")) in pairs)

    @my_vcr.use_cassette("query_200.yaml")
    def test_is_pair_exists(self):
        exchange = BittrexExchange()
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

    @my_vcr.use_cassette("query_200.yaml")
    def test_is_currency_exists(self):
        exchange = BittrexExchange()
        self.assertTrue(exchange.is_currency_exists(ECurrency(code="BTC")))
        self.assertTrue(exchange.is_currency_exists(ECurrency(code="USD")))

        self.assertFalse(exchange.is_currency_exists(ECurrency(code="usd")))
        self.assertFalse(exchange.is_currency_exists(ECurrency(code="MONEY")))

    @my_vcr.use_cassette("query_200.yaml")
    def test_get_pair_info(self):
        pair = Pair(ECurrency("BTC"), ECurrency("USD"))
        self.assertEqual(
            BittrexExchange().get_pair_info(pair),
            PairData(
                pair=pair,
                rate=Decimal("3909.439"),
                rate_open=Decimal("3879.0"),
                low24h=Decimal("3773.806"),
                high24h=Decimal("3923.994"),
                last_trade_at=datetime(2019, 3, 9, 13, 47, 19, 0),
            ),
        )

    @my_vcr.use_cassette("query_200.yaml")
    def test_get_pair_info_no_pair(self):
        pair = Pair(ECurrency("USD"), ECurrency("BTC"))
        with self.assertRaises(PairNotExistsException):
            BittrexExchange().get_pair_info(pair)

    @my_vcr.use_cassette("null_high_low.yaml")
    def test_null_high_low(self):
        pair = Pair(ECurrency("BTC"), ECurrency("USD"))
        self.assertEqual(
            BittrexExchange().get_pair_info(pair),
            PairData(
                pair=pair,
                rate=Decimal("5132.308"),
                rate_open=Decimal("5001.301"),
                low24h=None,
                high24h=None,
                last_trade_at=datetime(2019, 4, 7, 7, 54, 34),
            ),
        )

    @my_vcr.use_cassette("null_bid_ask.yaml")
    def test_null_bid_ask(self):
        pair = Pair(ECurrency("BTC"), ECurrency("USD"))
        with self.assertRaises(PairNotExistsException):
            BittrexExchange().get_pair_info(pair)

    @my_vcr.use_cassette("null_prevday.yaml")
    def test_null_prevday(self):
        pair = Pair(ECurrency("BTC"), ECurrency("USD"))
        self.assertEqual(
            BittrexExchange().get_pair_info(pair),
            PairData(
                pair=pair,
                rate=Decimal("5132.308"),
                rate_open=None,
                low24h=None,
                high24h=None,
                last_trade_at=datetime(2019, 4, 7, 7, 54, 34),
            ),
        )
