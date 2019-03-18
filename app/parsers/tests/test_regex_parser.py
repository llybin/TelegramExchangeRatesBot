import unittest
from decimal import Decimal
from unittest.mock import patch

from app.models import get_all_currencies
from ..base import PriceRequest, DirectionWriting
from ..exceptions import ValidationException
from ..regex_parser import RegexParser


class RegexParserTest(unittest.TestCase):
    @patch('app.parsers.regex_parser.get_all_currencies', return_value=['USD', 'RUB', 'EUR', 'BURST', 'SC'])
    def test_ok_pair_no_digits(self, m):
        # pair low case, no digits, space separator
        self.assertEqual(
            RegexParser('usd rub', 'USD', False).parse(),
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
            RegexParser('USD EUR', 'USD', False).parse(),
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
            RegexParser('sc burst', 'USD', False).parse(),
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
            RegexParser('burst sc', 'USD', False).parse(),
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
            RegexParser('rub', 'USD', False).parse(),
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
            RegexParser('rub', 'USD', True).parse(),
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
            RegexParser('100.20 usd rub', 'USD', True).parse(),
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
            RegexParser('100.20 rub', 'USD', True).parse(),
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
            RegexParser('100.20rub', 'USD', True).parse(),
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
            RegexParser('100.20rub', 'USD', False).parse(),
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
            RegexParser('rub usd 100.20', 'USD', True).parse(),
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
            RegexParser('rub 100.20', 'USD', True).parse(),
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
            RegexParser('rub100.20', 'USD', True).parse(),
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
            RegexParser('rub100.20', 'USD', False).parse(),
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
            RegexParser('usd to rub', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )

        self.assertEqual(
            RegexParser('usd=rub', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )

        self.assertEqual(
            RegexParser('100.20 usd in rub', 'USD', True).parse(),
            PriceRequest(
                amount=Decimal('100.20'),
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
            )
        )

        self.assertEqual(
            RegexParser('rub = usd 100.20', 'USD', True).parse(),
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
            RegexParser('usdrub', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='USD',
                to_currency='RUB',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )

        self.assertEqual(
            RegexParser('scburst', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='SC',
                to_currency='BURST',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )

        self.assertEqual(
            RegexParser('burstsc', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='BURST',
                to_currency='SC',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )

        self.assertEqual(
            RegexParser('scsc', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='SC',
                to_currency='SC',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )
        )

        self.assertEqual(
            RegexParser('burstburst', 'USD', False).parse(),
            PriceRequest(
                amount=None,
                currency='BURST',
                to_currency='BURST',
                parser_name='RegexParser',
                direction_writing=DirectionWriting.UNKNOWN,
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
            '1,000 usd rub',
            '0,1 usd rub',
            '-100 usd rub',
            '+100 usd rub',
            'BTC USD',
            'BTC > USD',
        ]

        for text in cases:
            with self.assertRaises(ValidationException, msg=text):
                RegexParser(text, 'USD', True).parse()

    def test_cross_all_currency(self):
        for cur0 in get_all_currencies():
            for cur1 in get_all_currencies():
                pr = RegexParser(f'{cur0}{cur1}', 'USD', False).parse()
                self.assertEqual(pr.currency, cur0, f'{cur0}{cur1}')
                self.assertEqual(pr.to_currency, cur1, f'{cur0}{cur1}')

