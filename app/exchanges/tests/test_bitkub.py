import datetime
from decimal import Decimal

import vcr
from freezegun import freeze_time
from suite.test.testcases import SimpleTestCase

from ..base import ECurrency, Pair, PairData
from ..bitkub import BitkubExchange
from ..exceptions import PairNotExistsException

my_vcr = vcr.VCR(
    cassette_library_dir="app/exchanges/tests/fixtures/vcr/bitkub",
    record_mode="once",
    decode_compressed_response=True,
)


class BitkubExchangeTest(SimpleTestCase):
    def test_name(self):
        self.assertEqual(
            BitkubExchange.name, "[bitkub.com](https://www.bitkub.com/signup?ref=64572)"
        )

    @my_vcr.use_cassette("query_200")
    def test_list_currencies(self):
        currencies = BitkubExchange().list_currencies
        self.assertEqual(len(currencies), 26)
        self.assertTrue(ECurrency(code="BTC") in currencies)
        self.assertTrue(ECurrency(code="THB") in currencies)

    @my_vcr.use_cassette("query_200")
    def test_list_pairs(self):
        pairs = BitkubExchange().list_pairs
        self.assertEqual(len(pairs), 25)
        self.assertTrue(Pair(ECurrency("BTC"), ECurrency("THB")) in pairs)
        self.assertFalse(Pair(ECurrency("THB"), ECurrency("BTC")) in pairs)

    @my_vcr.use_cassette("query_200")
    def test_is_pair_exists(self):
        exchange = BitkubExchange()
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

    @my_vcr.use_cassette("query_200")
    def test_is_currency_exists(self):
        exchange = BitkubExchange()
        self.assertTrue(exchange.is_currency_exists(ECurrency(code="BTC")))
        self.assertTrue(exchange.is_currency_exists(ECurrency(code="THB")))

        self.assertFalse(exchange.is_currency_exists(ECurrency(code="thb")))
        self.assertFalse(exchange.is_currency_exists(ECurrency(code="MONEY")))

    @my_vcr.use_cassette("query_200")
    @freeze_time("2019-03-17 22:14:15", tz_offset=0)
    def test_get_pair_info(self):
        pair = Pair(ECurrency("BTC"), ECurrency("THB"))
        self.assertEqual(
            BitkubExchange().get_pair_info(pair),
            PairData(
                pair=pair,
                rate=Decimal("300353.515"),
                rate_open=None,
                low24h=Decimal("281470"),
                high24h=Decimal("304000"),
                last_trade_at=datetime.datetime(2019, 3, 17, 22, 14, 15, 0),
            ),
        )

    @my_vcr.use_cassette("query_200")
    def test_get_pair_info_no_pair(self):
        pair = Pair(ECurrency("USD"), ECurrency("BTC"))
        with self.assertRaises(PairNotExistsException):
            BitkubExchange().get_pair_info(pair)
