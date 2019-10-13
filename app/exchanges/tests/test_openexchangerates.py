import datetime
from decimal import Decimal

import vcr
from suite.test.testcases import SimpleTestCase
from suite.test.utils import override_settings

from ..base import ECurrency, Pair, PairData
from ..exceptions import PairNotExistsException
from ..openexchangerates import OpenExchangeRatesExchange

my_vcr = vcr.VCR(
    cassette_library_dir="app/exchanges/tests/fixtures/vcr/openexchangerates",
    record_mode="once",
    decode_compressed_response=True,
    filter_query_parameters=["app_id"],
)


@override_settings(OPENEXCHANGERATES_TOKEN="FAKE-TOKEN")
class OpenExchangeRatesTest(SimpleTestCase):
    def test_name(self):
        self.assertEqual(OpenExchangeRatesExchange.name, "OpenExchangeRates")

    @my_vcr.use_cassette("query_200")
    def test_list_currencies(self):
        currencies = OpenExchangeRatesExchange().list_currencies
        self.assertEqual(len(currencies), 172)
        self.assertTrue(ECurrency(code="EUR") in currencies)
        self.assertTrue(ECurrency(code="USD") in currencies)

    @my_vcr.use_cassette("query_200")
    def test_list_pairs(self):
        pairs = OpenExchangeRatesExchange().list_pairs
        self.assertEqual(len(pairs), 171)
        self.assertTrue(Pair(ECurrency("USD"), ECurrency("EUR")) in pairs)

    @my_vcr.use_cassette("query_200")
    def test_is_pair_exists(self):
        exchange = OpenExchangeRatesExchange()
        self.assertTrue(
            exchange.is_pair_exists(Pair(ECurrency("USD"), ECurrency("EUR")))
        )

        self.assertFalse(
            exchange.is_pair_exists(Pair(ECurrency("usd"), ECurrency("EUR")))
        )
        self.assertFalse(
            exchange.is_pair_exists(Pair(ECurrency("USD"), ECurrency("MONEY")))
        )

    @my_vcr.use_cassette("query_200")
    def test_is_currency_exists(self):
        exchange = OpenExchangeRatesExchange()
        self.assertTrue(exchange.is_currency_exists(ECurrency(code="EUR")))
        self.assertTrue(exchange.is_currency_exists(ECurrency(code="USD")))

        self.assertFalse(exchange.is_currency_exists(ECurrency(code="usd")))
        self.assertFalse(exchange.is_currency_exists(ECurrency(code="MONEY")))

    @my_vcr.use_cassette("query_200")
    def test_get_pair_info(self):
        pair = Pair(ECurrency("USD"), ECurrency("EUR"))
        self.assertEqual(
            OpenExchangeRatesExchange().get_pair_info(pair),
            PairData(
                pair=pair,
                rate=Decimal("0.8792"),
                rate_open=None,
                last_trade_at=datetime.datetime(2019, 3, 21, 21, 0),
            ),
        )

    @my_vcr.use_cassette("query_200")
    def test_get_pair_info_no_pair(self):
        pair = Pair(ECurrency("MONEY"), ECurrency("USD"))
        with self.assertRaises(PairNotExistsException):
            OpenExchangeRatesExchange().get_pair_info(pair)
