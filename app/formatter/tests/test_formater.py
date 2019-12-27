from datetime import datetime
from decimal import Decimal

from freezegun import freeze_time

from app.constants import decimal_scale
from app.converter.base import PriceRequestResult
from app.formatter.formatter import (
    FormatPriceRequestResult,
    InlineFormatPriceRequestResult,
    NotifyFormatPriceRequestResult,
    clever_round,
)
from app.parsers.base import DirectionWriting, PriceRequest
from suite.test.testcases import SimpleTestCase


class CleverRoundTest(SimpleTestCase):
    def test_more_1(self):
        self.assertEqual(clever_round(Decimal("1.00001"), 4), Decimal("1"))

    def test_no_fraction(self):
        self.assertEqual(clever_round(Decimal("10"), 4), Decimal("10"))

    def test_very_small(self):
        self.assertEqual(
            clever_round(Decimal(f'0.{"0" * decimal_scale}1'), 4), Decimal("0")
        )

    def test_all_ndigits(self):
        self.assertEqual(
            clever_round(Decimal(f'0.{"0" * (decimal_scale - 4)}11111'), 4),
            Decimal(f'0.{"0" * (decimal_scale - 4)}1111'),
        )

    def test_part_ndigits(self):
        self.assertEqual(
            clever_round(Decimal(f'0.{"0" * (decimal_scale - 3)}1111'), 4),
            Decimal(f'0.{"0" * (decimal_scale - 3)}111'),
        )

        self.assertEqual(
            clever_round(Decimal(f'0.{"0" * (decimal_scale - 1)}11111'), 4),
            Decimal(f'0.{"0" * (decimal_scale - 1)}1'),
        )

    def test_rounding(self):
        self.assertEqual(
            clever_round(Decimal(f'0.{"0" * (decimal_scale - 4)}12345'), 4),
            Decimal(f'0.{"0" * (decimal_scale - 4)}1235'),
        )


class FormatPriceRequestResultTest(SimpleTestCase):
    @freeze_time("2019-03-17 22:14:15", tz_offset=0)
    def test_convert_mode(self):
        prr = PriceRequestResult(
            price_request=PriceRequest(
                amount=Decimal("0.5"),
                currency="USD",
                to_currency="EUR",
                parser_name="test-parser",
                direction_writing=DirectionWriting.UNKNOWN,
            ),
            exchanges=["test-exchanger"],
            rate=Decimal("3"),
            rate_open=Decimal("1"),
            low24h=Decimal("1"),
            high24h=Decimal("1"),
            last_trade_at=datetime.now(),
        )

        fpr = FormatPriceRequestResult(prr, "en")

        self.assertTrue(fpr.is_rate_diff_available())
        self.assertTrue(fpr.is_convert_mode())
        self.assertEqual(
            fpr.get(), "0.5 *USD* = 1.5 *EUR*\n_17 March, 22:14 UTC_\ntest-exchanger 📡"
        )

    @freeze_time("1996-03-17 22:14:15", tz_offset=0)
    def test_convert_mode_1996(self):
        prr = PriceRequestResult(
            price_request=PriceRequest(
                amount=Decimal("0.5"),
                currency="USD",
                to_currency="USD",
                parser_name="test-parser",
                direction_writing=DirectionWriting.UNKNOWN,
            ),
            exchanges=["test-exchanger"],
            rate=Decimal("3"),
            rate_open=Decimal("1"),
            low24h=Decimal("1"),
            high24h=Decimal("1"),
            last_trade_at=datetime.now(),
        )

        fpr = FormatPriceRequestResult(prr, "en")

        self.assertTrue(fpr.is_rate_diff_available())
        self.assertTrue(fpr.is_convert_mode())
        self.assertEqual(
            fpr.get(), "0.5 *USD* = 1.5 *USD*\n_17 March 1996_\ntest-exchanger 📡"
        )

    @freeze_time("2019-03-17 22:14:15", tz_offset=0)
    def test_convert_mode_r2l(self):
        prr = PriceRequestResult(
            price_request=PriceRequest(
                amount=Decimal("0.5"),
                currency="USD",
                to_currency="EUR",
                parser_name="test-parser",
                direction_writing=DirectionWriting.RIGHT2LEFT,
            ),
            exchanges=["test-exchanger"],
            rate=Decimal("3"),
            rate_open=Decimal("1"),
            low24h=Decimal("1"),
            high24h=Decimal("1"),
            last_trade_at=datetime.now(),
        )

        fpr = FormatPriceRequestResult(prr, "en")

        self.assertTrue(fpr.is_rate_diff_available())
        self.assertTrue(fpr.is_convert_mode())
        self.assertEqual(
            fpr.get(), "1.5 *EUR* = 0.5 *USD*\n_17 March, 22:14 UTC_\ntest-exchanger 📡"
        )

    @freeze_time("2019-03-17 22:14:15", tz_offset=0)
    def test_price_mode(self):
        prr = PriceRequestResult(
            price_request=PriceRequest(
                amount=None,
                currency="USD",
                to_currency="EUR",
                parser_name="test-parser",
                direction_writing=DirectionWriting.UNKNOWN,
            ),
            exchanges=["test-exchanger"],
            rate=Decimal("1.5"),
            rate_open=Decimal("1.3"),
            low24h=Decimal("1.2"),
            high24h=Decimal("1.6"),
            last_trade_at=datetime.now(),
        )
        fpr = FormatPriceRequestResult(prr, "en")

        self.assertTrue(fpr.is_rate_diff_available())
        self.assertFalse(fpr.is_convert_mode())
        self.assertEqual(
            fpr.get(),
            "*USD EUR* 1.5 ⬆️\n+0.2 (+15.38%)\n*Low*: 1.2 *High*: 1.6\n_17 March, 22:14 UTC_\ntest-exchanger 📡",
        )

    @freeze_time("2019-03-17 22:14:15", tz_offset=0)
    def test_price_mode_no_diff(self):
        prr = PriceRequestResult(
            price_request=PriceRequest(
                amount=None,
                currency="USD",
                to_currency="EUR",
                parser_name="test-parser",
                direction_writing=DirectionWriting.UNKNOWN,
            ),
            exchanges=["test-exchanger"],
            rate=Decimal("1.5"),
            rate_open=None,
            low24h=Decimal("1.2"),
            high24h=Decimal("1.6"),
            last_trade_at=datetime.now(),
        )
        fpr = FormatPriceRequestResult(prr, "en")

        self.assertFalse(fpr.is_rate_diff_available())
        self.assertFalse(fpr.is_convert_mode())
        self.assertEqual(
            fpr.get(),
            "*USD EUR* 1.5\n*Low*: 1.2 *High*: 1.6\n_17 March, 22:14 UTC_\ntest-exchanger 📡",
        )

    @freeze_time("2019-03-17 22:14:15", tz_offset=0)
    def test_price_mode_no_low(self):
        prr = PriceRequestResult(
            price_request=PriceRequest(
                amount=None,
                currency="USD",
                to_currency="EUR",
                parser_name="test-parser",
                direction_writing=DirectionWriting.UNKNOWN,
            ),
            exchanges=["test-exchanger", "test-2"],
            rate=Decimal("1.5"),
            rate_open=None,
            low24h=None,
            high24h=None,
            last_trade_at=datetime.now(),
        )
        fpr = FormatPriceRequestResult(prr, "en")

        self.assertFalse(fpr.is_rate_diff_available())
        self.assertFalse(fpr.is_convert_mode())
        self.assertEqual(
            fpr.get(), "*USD EUR* 1.5\n_17 March, 22:14 UTC_\ntest-exchanger 📡 test-2 📡"
        )

    @freeze_time("2019-03-17 22:14:15", tz_offset=0)
    def test_price_mode_same_rate_open(self):
        prr = PriceRequestResult(
            price_request=PriceRequest(
                amount=None,
                currency="USD",
                to_currency="EUR",
                parser_name="test-parser",
                direction_writing=DirectionWriting.UNKNOWN,
            ),
            exchanges=["test-exchanger"],
            rate=Decimal("1.5"),
            rate_open=Decimal("1.5"),
            low24h=Decimal("1.2"),
            high24h=Decimal("1.6"),
            last_trade_at=datetime.now(),
        )
        fpr = FormatPriceRequestResult(prr, "en")

        self.assertTrue(fpr.is_rate_diff_available())
        self.assertFalse(fpr.is_convert_mode())
        self.assertEqual(
            fpr.get(),
            "*USD EUR* 1.5\n0.0 (0.0%)\n*Low*: 1.2 *High*: 1.6\n_17 March, 22:14 UTC_\ntest-exchanger 📡",
        )

    @freeze_time("2019-03-17 22:14:15", tz_offset=0)
    def test_rounding(self):
        prr = PriceRequestResult(
            price_request=PriceRequest(
                amount=None,
                currency="USD",
                to_currency="EUR",
                parser_name="test-parser",
                direction_writing=DirectionWriting.UNKNOWN,
            ),
            exchanges=["test-exchanger"],
            rate=Decimal("0.5"),
            rate_open=Decimal("1"),
            low24h=Decimal("0.05"),
            high24h=Decimal("0.005"),
            last_trade_at=datetime.now(),
        )
        fpr = FormatPriceRequestResult(prr, "en")

        self.assertTrue(fpr.is_rate_diff_available())
        self.assertFalse(fpr.is_convert_mode())
        self.assertEqual(
            fpr.get(),
            "*USD EUR* 0.5 🔻\n-0.5 (-50.0%)\n*Low*: 0.05 *High*: 0.0050\n_17 March, 22:14 UTC_\ntest-exchanger 📡",
        )

        prr = PriceRequestResult(
            price_request=PriceRequest(
                amount=None,
                currency="USD",
                to_currency="EUR",
                parser_name="test-parser",
                direction_writing=DirectionWriting.UNKNOWN,
            ),
            exchanges=["test-exchanger"],
            rate=Decimal("123456789012.123456789012"),
            rate_open=Decimal("1"),
            low24h=Decimal("0.000000000012"),
            high24h=Decimal("1"),
            last_trade_at=datetime.now(),
        )
        fpr = FormatPriceRequestResult(prr, "en")

        self.assertTrue(fpr.is_rate_diff_available())
        self.assertFalse(fpr.is_convert_mode())
        self.assertEqual(
            fpr.get(),
            """*USD EUR* 123,456,789,012.1235 ⬆️
+123,456,789,011.1235 (+12,345,678,901,112.35%)
*Low*: 0.000000000012 *High*: 1.0
_17 March, 22:14 UTC_
test-exchanger 📡""",
        )

        prr = PriceRequestResult(
            price_request=PriceRequest(
                amount=None,
                currency="USD",
                to_currency="EUR",
                parser_name="test-parser",
                direction_writing=DirectionWriting.UNKNOWN,
            ),
            exchanges=["test-exchanger"],
            rate=Decimal("123456789012.123456789012"),
            rate_open=Decimal("123456789000.000012345"),
            low24h=Decimal("1234567890.000"),
            high24h=Decimal("198765432112.000000000012"),
            last_trade_at=datetime.now(),
        )
        fpr = FormatPriceRequestResult(prr, "en")

        self.assertTrue(fpr.is_rate_diff_available())
        self.assertFalse(fpr.is_convert_mode())
        self.assertEqual(
            fpr.get(),
            """*USD EUR* 123,456,789,012.1235 ⬆️
+12.1234 (+0.0000000098%)
*Low*: 1,234,567,890.0 *High*: 198,765,432,112.0
_17 March, 22:14 UTC_
test-exchanger 📡""",
        )

    @freeze_time("2019-03-17 22:14:15", tz_offset=0)
    def test_locale(self):
        prr = PriceRequestResult(
            price_request=PriceRequest(
                amount=None,
                currency="USD",
                to_currency="EUR",
                parser_name="test-parser",
                direction_writing=DirectionWriting.UNKNOWN,
            ),
            exchanges=["test-exchanger"],
            rate=Decimal("1.5"),
            rate_open=Decimal("1.3"),
            low24h=Decimal("1.2"),
            high24h=Decimal("1.6"),
            last_trade_at=datetime.now(),
        )

        fpr = FormatPriceRequestResult(prr, "en")

        self.assertTrue(fpr.is_rate_diff_available())
        self.assertFalse(fpr.is_convert_mode())
        self.assertEqual(
            fpr.get(),
            "*USD EUR* 1.5 ⬆️\n+0.2 (+15.38%)\n*Low*: 1.2 *High*: 1.6\n_17 March, 22:14 UTC_\ntest-exchanger 📡",
        )

        fpr = FormatPriceRequestResult(prr, "de")

        self.assertTrue(fpr.is_rate_diff_available())
        self.assertFalse(fpr.is_convert_mode())
        self.assertEqual(
            fpr.get(),
            "*USD EUR* 1,5 ⬆️\n+0,2 (+15,38%)\n*Low*: 1,2 *High*: 1,6\n_17 March, 22:14 UTC_\ntest-exchanger 📡",
        )

        fpr = FormatPriceRequestResult(prr, "zh-hans-sg")

        self.assertTrue(fpr.is_rate_diff_available())
        self.assertFalse(fpr.is_convert_mode())
        self.assertEqual(
            fpr.get(),
            "*USD EUR* 1.5 ⬆️\n+0.2 (+15.38%)\n*Low*: 1.2 *High*: 1.6\n_17 March, 22:14 UTC_\ntest-exchanger 📡",
        )


class InlineFormatPriceRequestResultTest(SimpleTestCase):
    @freeze_time("2019-03-17 22:14:15", tz_offset=0)
    def test_convert_mode(self):
        prr = PriceRequestResult(
            price_request=PriceRequest(
                amount=Decimal("0.5"),
                currency="USD",
                to_currency="EUR",
                parser_name="test-parser",
                direction_writing=DirectionWriting.UNKNOWN,
            ),
            exchanges=["test-exchanger"],
            rate=Decimal("3"),
            rate_open=Decimal("1"),
            low24h=Decimal("1"),
            high24h=Decimal("1"),
            last_trade_at=datetime.now(),
        )

        fpr = InlineFormatPriceRequestResult(prr, "en")

        self.assertTrue(fpr.is_rate_diff_available())
        self.assertTrue(fpr.is_convert_mode())
        self.assertEqual(fpr.get(), "0.5 USD = 1.5 EUR")

    @freeze_time("2019-03-17 22:14:15", tz_offset=0)
    def test_convert_r2l(self):
        prr = PriceRequestResult(
            price_request=PriceRequest(
                amount=Decimal("0.5"),
                currency="USD",
                to_currency="EUR",
                parser_name="test-parser",
                direction_writing=DirectionWriting.RIGHT2LEFT,
            ),
            exchanges=["test-exchanger"],
            rate=Decimal("3"),
            rate_open=Decimal("1"),
            low24h=Decimal("1"),
            high24h=Decimal("1"),
            last_trade_at=datetime.now(),
        )

        fpr = InlineFormatPriceRequestResult(prr, "en")

        self.assertTrue(fpr.is_rate_diff_available())
        self.assertTrue(fpr.is_convert_mode())
        self.assertEqual(fpr.get(), "1.5 EUR = 0.5 USD")

    @freeze_time("2019-03-17 22:14:15", tz_offset=0)
    def test_price_mode(self):
        prr = PriceRequestResult(
            price_request=PriceRequest(
                amount=None,
                currency="USD",
                to_currency="EUR",
                parser_name="test-parser",
                direction_writing=DirectionWriting.UNKNOWN,
            ),
            exchanges=["test-exchanger"],
            rate=Decimal("1.5"),
            rate_open=Decimal("1.3"),
            low24h=Decimal("1.2"),
            high24h=Decimal("1.6"),
            last_trade_at=datetime.now(),
        )
        fpr = InlineFormatPriceRequestResult(prr, "en")

        self.assertTrue(fpr.is_rate_diff_available())
        self.assertFalse(fpr.is_convert_mode())
        self.assertEqual(fpr.get(), "USD EUR 1.5 ⬆️")

    @freeze_time("2019-03-17 22:14:15", tz_offset=0)
    def test_price_mode_no_diff(self):
        prr = PriceRequestResult(
            price_request=PriceRequest(
                amount=None,
                currency="USD",
                to_currency="EUR",
                parser_name="test-parser",
                direction_writing=DirectionWriting.UNKNOWN,
            ),
            exchanges=["test-exchanger"],
            rate=Decimal("1.5"),
            rate_open=None,
            low24h=Decimal("1.2"),
            high24h=Decimal("1.6"),
            last_trade_at=datetime.now(),
        )
        fpr = InlineFormatPriceRequestResult(prr, "en")

        self.assertFalse(fpr.is_rate_diff_available())
        self.assertFalse(fpr.is_convert_mode())
        self.assertEqual(fpr.get(), "USD EUR 1.5")


class NotifyFormatPriceRequestResultTest(SimpleTestCase):
    @freeze_time("2019-03-17 22:14:15", tz_offset=0)
    def test_price_mode(self):
        prr = PriceRequestResult(
            price_request=PriceRequest(
                amount=None,
                currency="USD",
                to_currency="EUR",
                parser_name="test-parser",
                direction_writing=DirectionWriting.UNKNOWN,
            ),
            exchanges=["test-exchanger"],
            rate=Decimal("1.5"),
            rate_open=Decimal("1.3"),
            low24h=Decimal("1.2"),
            high24h=Decimal("1.6"),
            last_trade_at=datetime.now(),
        )
        fpr = NotifyFormatPriceRequestResult(prr, "en")

        self.assertTrue(fpr.is_rate_diff_available())
        self.assertFalse(fpr.is_convert_mode())
        self.assertEqual(
            fpr.get(),
            "*USD EUR* 1.5 ⬆️ 🔔\n+0.2 (+15.38%)\n*Low*: 1.2 *High*: 1.6\n_17 March, 22:14 UTC_\ntest-exchanger 📡",
        )

    @freeze_time("2019-03-17 22:14:15", tz_offset=0)
    def test_price_mode_no_diff(self):
        prr = PriceRequestResult(
            price_request=PriceRequest(
                amount=None,
                currency="USD",
                to_currency="EUR",
                parser_name="test-parser",
                direction_writing=DirectionWriting.UNKNOWN,
            ),
            exchanges=["test-exchanger"],
            rate=Decimal("1.5"),
            last_trade_at=datetime.now(),
        )
        fpr = NotifyFormatPriceRequestResult(prr, "en")

        self.assertFalse(fpr.is_rate_diff_available())
        self.assertFalse(fpr.is_convert_mode())
        self.assertEqual(
            fpr.get(), "*USD EUR* 1.5 🔔\n_17 March, 22:14 UTC_\ntest-exchanger 📡"
        )
