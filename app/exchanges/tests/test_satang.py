from datetime import datetime
from decimal import Decimal

from freezegun import freeze_time
from vcr import VCR

from app.exchanges.base import ECurrency, Pair, PairData
from app.exchanges.exceptions import PairNotExistsException
from app.exchanges.satang import SatangExchange
from suite.test.testcases import SimpleTestCase

my_vcr = VCR(
    cassette_library_dir="app/exchanges/tests/fixtures/vcr/satang",
    record_mode="once",
    decode_compressed_response=True,
)


class SatangExchangeTest(SimpleTestCase):
    def test_name(self):
        self.assertEqual(
            SatangExchange.name,
            "[satang.pro](https://satang.pro/signup?referral=STZ3EEU2)",
        )

    @my_vcr.use_cassette("query_200.yaml")
    def test_list_currencies(self):
        currencies = SatangExchange().list_currencies
        self.assertEqual(len(currencies), 12)
        self.assertTrue(ECurrency(code="BTC") in currencies)
        self.assertTrue(ECurrency(code="THB") in currencies)

    @my_vcr.use_cassette("query_200.yaml")
    def test_list_pairs(self):
        pairs = SatangExchange().list_pairs
        self.assertEqual(len(pairs), 11)
        self.assertTrue(Pair(ECurrency("BTC"), ECurrency("THB")) in pairs)
        self.assertFalse(Pair(ECurrency("THB"), ECurrency("BTC")) in pairs)

    @my_vcr.use_cassette("query_200.yaml")
    def test_is_pair_exists(self):
        exchange = SatangExchange()
        self.assertTrue(
            exchange.is_pair_exists(Pair(ECurrency("BTC"), ECurrency("THB")))
        )

        self.assertFalse(
            exchange.is_pair_exists(Pair(ECurrency("THB"), ECurrency("BTC")))
        )
        self.assertFalse(
            exchange.is_pair_exists(Pair(ECurrency("thb"), ECurrency("BTC")))
        )
        self.assertFalse(
            exchange.is_pair_exists(Pair(ECurrency("btc"), ECurrency("MONEY")))
        )

    @my_vcr.use_cassette("query_200.yaml")
    def test_is_currency_exists(self):
        exchange = SatangExchange()
        self.assertTrue(exchange.is_currency_exists(ECurrency(code="BTC")))
        self.assertTrue(exchange.is_currency_exists(ECurrency(code="THB")))

        self.assertFalse(exchange.is_currency_exists(ECurrency(code="thb")))
        self.assertFalse(exchange.is_currency_exists(ECurrency(code="MONEY")))

    @my_vcr.use_cassette("query_200.yaml")
    @freeze_time("2020-02-17 22:14:15", tz_offset=0)
    def test_get_pair_info(self):
        pair = Pair(ECurrency("BTC"), ECurrency("THB"))
        self.assertEqual(
            SatangExchange().get_pair_info(pair),
            PairData(
                pair=pair,
                rate=Decimal("304799.5"),
                last_trade_at=datetime(2020, 2, 17, 22, 14, 15),
                rate_open=None,
                low24h=None,
                high24h=None,
            ),
        )

    @my_vcr.use_cassette("query_200.yaml")
    def test_get_pair_info_no_pair(self):
        pair = Pair(ECurrency("USD"), ECurrency("BTC"))
        with self.assertRaises(PairNotExistsException):
            SatangExchange().get_pair_info(pair)
