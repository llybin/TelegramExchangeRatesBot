import datetime
from decimal import Decimal

import vcr
from freezegun import freeze_time

from suite.test.testcases import SimpleTestCase
from suite.test.utils import override_settings
from ..vipchanger import VipChangerExchange
from ..base import PairData, Pair, ECurrency
from ..exceptions import PairNotExistsException


my_vcr = vcr.VCR(
    cassette_library_dir='app/exchanges/tests/fixtures/vcr/vipchanger',
    record_mode='once',
    decode_compressed_response=True,
)


@override_settings(PROXIES_TH=None)
class VipChangerExchangeTest(SimpleTestCase):

    def test_name(self):
        self.assertEqual(VipChangerExchange.name, '[vipchanger.com](https://vipchanger.com/?pid=4503)')

    @my_vcr.use_cassette('query_200')
    def test_list_currencies(self):
        currencies = VipChangerExchange().list_currencies
        self.assertEqual(len(currencies), 4)
        self.assertTrue(ECurrency(code='RUB') in currencies)
        self.assertTrue(ECurrency(code='THB') in currencies)

    @my_vcr.use_cassette('query_200')
    def test_list_pairs(self):
        pairs = VipChangerExchange().list_pairs
        self.assertEqual(len(pairs), 8)
        self.assertTrue(Pair(ECurrency('RUB'), ECurrency('THB')) in pairs)
        self.assertTrue(Pair(ECurrency('THB'), ECurrency('RUB')) in pairs)
        self.assertFalse(Pair(ECurrency('EUR'), ECurrency('USD')) in pairs)

    @my_vcr.use_cassette('query_200')
    def test_is_pair_exists(self):
        exchange = VipChangerExchange()
        self.assertTrue(exchange.is_pair_exists(Pair(ECurrency('RUB'), ECurrency('THB'))))

        self.assertFalse(exchange.is_pair_exists(Pair(ECurrency('SYP'), ECurrency('EUR'))))
        self.assertFalse(exchange.is_pair_exists(Pair(ECurrency('usd'), ECurrency('syp'))))
        self.assertFalse(exchange.is_pair_exists(Pair(ECurrency('syp'), ECurrency('MONEY'))))

    @my_vcr.use_cassette('query_200')
    def test_is_currency_exists(self):
        exchange = VipChangerExchange()
        self.assertTrue(exchange.is_currency_exists(ECurrency(code='RUB')))
        self.assertTrue(exchange.is_currency_exists(ECurrency(code='THB')))
        self.assertTrue(exchange.is_currency_exists(ECurrency(code='KZT')))

        self.assertFalse(exchange.is_currency_exists(ECurrency(code='thb')))
        self.assertFalse(exchange.is_currency_exists(ECurrency(code='MONEY')))

    @my_vcr.use_cassette('query_200')
    @freeze_time("2019-03-17 22:14:15", tz_offset=0)
    def test_get_pair_info(self):
        pair = Pair(ECurrency('RUB'), ECurrency('THB'))
        self.assertEqual(
            VipChangerExchange().get_pair_info(pair),
            PairData(
                pair=pair,
                rate=Decimal('0.4624'),
                rate_open=None,
                last_trade_at=datetime.datetime(2019, 3, 17, 22, 14, 15, 0),
            )
        )

    @my_vcr.use_cassette('query_200')
    def test_get_pair_info_no_pair(self):
        pair = Pair(ECurrency('SYP'), ECurrency('BTC'))
        with self.assertRaises(PairNotExistsException):
            VipChangerExchange().get_pair_info(pair)
