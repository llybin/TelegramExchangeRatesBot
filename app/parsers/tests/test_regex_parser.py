import unittest
from decimal import Decimal
from unittest.mock import patch

from app.models import get_all_currencies
from ..base import PriceRequest, DirectionWriting
from ..exceptions import ValidationException
from ..regex_parser import RegexParser, parse_amount


class RegexParserTest(unittest.TestCase):
    @patch('app.parsers.regex_parser.get_all_currencies', return_value=['USD', 'RUB', 'EUR', 'BURST', 'SC'])
    def test_ok_pair_no_digits(self, m):
        # pair low case, no digits, space separator
        self.assertEqual(
            RegexParser('usd rub', 1, 'en', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )
        # pair upper case, no digits, space separator
        self.assertEqual(
            RegexParser('USD EUR', 1, 'en', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='USD',
                to_currency='EUR',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )

        # pair min and max len, no digits, space separator
        self.assertEqual(
            RegexParser('sc burst', 1, 'en', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='SC',
                to_currency='BURST',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )

        # pair min and max len, no digits, space separator
        self.assertEqual(
            RegexParser('burst sc', 1, 'en', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='BURST',
                to_currency='SC',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )

    @patch('app.parsers.regex_parser.get_all_currencies', return_value=['USD', 'RUB', 'EUR', 'BURST', 'SC'])
    def test_ok_single_no_digits(self, m):
        # single to, no digits
        self.assertEqual(
            RegexParser('rub', 1, 'en', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )

        # single from, no digits
        self.assertEqual(
            RegexParser('rub', 1, 'en', 'USD', True).parse(),
            PriceRequest(
                amount=None,
                currency='RUB',
                to_currency='USD',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )

    @patch('app.parsers.regex_parser.get_all_currencies', return_value=['USD', 'RUB', 'EUR', 'BURST', 'SC'])
    def test_ok_digits_l2r(self, m):
        # pair, space separator
        self.assertEqual(
            RegexParser('100.20 usd rub', 1, 'en', 'USD', True).parse(),
            PriceRequest(
                amount=Decimal('100.20'),
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
            )
        )

        # single from, space separator
        self.assertEqual(
            RegexParser('100.20 rub', 1, 'en', 'USD', True).parse(),
            PriceRequest(
                amount=Decimal('100.20'),
                currency='RUB',
                to_currency='USD',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
            )
        )

        # single from, no space separator
        self.assertEqual(
            RegexParser('100.20rub', 1, 'en', 'USD', True).parse(),
            PriceRequest(
                amount=Decimal('100.20'),
                currency='RUB',
                to_currency='USD',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
            )
        )

        # single to, no space separator
        self.assertEqual(
            RegexParser('100.20rub', 1, 'en', 'USD', False).parse(),
            PriceRequest(
                amount=Decimal('100.20'),
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
            )
        )

    @patch('app.parsers.regex_parser.get_all_currencies', return_value=['USD', 'RUB', 'EUR', 'BURST', 'SC'])
    def test_ok_digits_r2l(self, m):
        # pair, space separator
        self.assertEqual(
            RegexParser('rub usd 100.20', 1, 'en', 'USD', True).parse(),
            PriceRequest(
                amount=Decimal('100.20'),
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.RIGHT2LEFT,
            )
        )

        # single from, space separator
        self.assertEqual(
            RegexParser('rub 100.20', 1, 'en', 'USD', True).parse(),
            PriceRequest(
                amount=Decimal('100.20'),
                currency='RUB',
                to_currency='USD',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.RIGHT2LEFT,
            )
        )

        # single from, no space separator
        self.assertEqual(
            RegexParser('rub100.20', 1, 'en', 'USD', True).parse(),
            PriceRequest(
                amount=Decimal('100.20'),
                currency='RUB',
                to_currency='USD',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.RIGHT2LEFT,
            )
        )

        # single to, no space separator
        self.assertEqual(
            RegexParser('rub100.20', 1, 'en', 'USD', False).parse(),
            PriceRequest(
                amount=Decimal('100.20'),
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.RIGHT2LEFT,
            )
        )

    @patch('app.parsers.regex_parser.get_all_currencies', return_value=['USD', 'RUB', 'EUR', 'BURST', 'SC'])
    def test_ok_separators(self, m):
        self.assertEqual(
            RegexParser('usd to rub', 1, 'en', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )

        self.assertEqual(
            RegexParser('usd=rub', 1, 'en', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )

        self.assertEqual(
            RegexParser('100.20 usd in rub', 1, 'en', 'USD', True).parse(),
            PriceRequest(
                amount=Decimal('100.20'),
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
            )
        )

        self.assertEqual(
            RegexParser('rub = usd 100.20', 1, 'en', 'USD', True).parse(),
            PriceRequest(
                amount=Decimal('100.20'),
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.RIGHT2LEFT,
            )
        )

    @patch('app.parsers.regex_parser.get_all_currencies', return_value=['USD', 'RUB', 'EUR', 'BURST', 'SC'])
    def test_no_separators(self, m):
        self.assertEqual(
            RegexParser('usdrub', 1, 'en', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )

        self.assertEqual(
            RegexParser('scburst', 1, 'en', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='SC',
                to_currency='BURST',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )

        self.assertEqual(
            RegexParser('burstsc', 1, 'en', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='BURST',
                to_currency='SC',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )

        self.assertEqual(
            RegexParser('scsc', 1, 'en', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='SC',
                to_currency='SC',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )

        self.assertEqual(
            RegexParser('burstburst', 1, 'en', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='BURST',
                to_currency='BURST',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )

    @patch('app.parsers.regex_parser.get_all_currencies', return_value=['USD', 'RUB', 'EUR', 'BURST', 'SC'])
    def test_money_formats(self, m):
        self.assertEqual(
            RegexParser('100.20 usd rub', 1, 'en', 'USD', True).parse(),
            PriceRequest(
                amount=Decimal('100.20'),
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
            )
        )

        self.assertEqual(
            RegexParser('100.20 usd rub', 1, 'de', 'USD', True).parse(),
            PriceRequest(
                amount=Decimal('10020'),
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
            )
        )

        self.assertEqual(
            RegexParser('100,20 usd rub', 1, 'en', 'USD', True).parse(),
            PriceRequest(
                amount=Decimal('10020'),
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
            )
        )

        self.assertEqual(
            RegexParser('100,20 usd rub', 1, 'de', 'USD', True).parse(),
            PriceRequest(
                amount=Decimal('100.20'),
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
            )
        )

        self.assertEqual(
            RegexParser('100 20 usd rub', 1, 'de', 'USD', True).parse(),
            PriceRequest(
                amount=Decimal('10020'),
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
            )
        )

        self.assertEqual(
            RegexParser('100 20,12 usd rub', 1, 'de', 'USD', True).parse(),
            PriceRequest(
                amount=Decimal('10020.12'),
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
            )
        )

    @patch('app.parsers.regex_parser.get_all_currencies', return_value=['USD', 'RUB', 'EUR', 'BURST', 'SC'])
    def test_bad(self, m):
        cases = [
            '',
            ' ',
            '100',
            '100.22',
            'usdrubeur',
            '100usd rub100',
            '-100 usd rub',
            '+100 usd rub',
            'BTC USD',
            'BTC',
            'BTC > USD',
            '1234567890123 USD'
            '100000000000 USD'
        ]

        for text in cases:
            with self.assertRaises(ValidationException, msg=text):
                RegexParser(text, 1, 'en', 'USD', True).parse()

    def test_cross_all_currency(self):
        for cur0 in get_all_currencies():
            for cur1 in get_all_currencies():
                pr = RegexParser(f'{cur0}{cur1}', 1, 'en', 'USD', False).parse()
                self.assertEqual(pr.currency, cur0, f'{cur0}{cur1}')
                self.assertEqual(pr.to_currency, cur1, f'{cur0}{cur1}')


class ParseAmountTest(unittest.TestCase):
    @patch('app.parsers.regex_parser.get_all_currencies', return_value=['USD', 'RUB', 'EUR', 'BURST', 'SC'])
    def test_ok(self, m):
        self.assertEqual(
            parse_amount('99999999999.1234567890123', 'en'),
            Decimal('99999999999.1234567890123')
        )

        self.assertEqual(
            parse_amount('9', 'en'),
            Decimal('9')
        )

        self.assertEqual(
            parse_amount('9 123', 'en'),
            Decimal('9123')
        )

        self.assertEqual(
            parse_amount('9,123', 'en'),
            Decimal('9123')
        )

        self.assertEqual(
            parse_amount('9,123', 'de'),
            Decimal('9.123')
        )

        self.assertEqual(
            parse_amount('9,123', 'ru'),
            Decimal('9.123')
        )

        self.assertEqual(
            parse_amount('9.123', 'pt_BR'),
            Decimal('9123')
        )

        self.assertEqual(
            parse_amount('9.123', 'zh_Hans_SG'),
            Decimal('9.123')
        )

    @patch('app.parsers.regex_parser.get_all_currencies', return_value=['USD', 'RUB', 'EUR', 'BURST', 'SC'])
    def test_bad(self, m):
        with self.assertRaises(ValidationException):
            parse_amount('99999999999.1234567890123', 'de')

        with self.assertRaises(ValidationException):
            parse_amount('1234567890123', 'de')

        with self.assertRaises(ValidationException):
            parse_amount('1000000000000', 'de')
