import unittest
from decimal import Decimal
from unittest.mock import patch

from ..base import PriceRequest, DirectionWriting
from ..exceptions import ValidationException
from ..number_format import NumberFormat
from ..simple_parser import SimpleParser


class SimpleParserTest(unittest.TestCase):
    @patch('app.parsers.simple_parser.get_all_currencies', return_value=['USD', 'RUB', 'EUR', 'BURST', 'SC'])
    def test_good(self, m):
        cases = [
            ('usd rub', PriceRequest(
                amount=None,
                currency='USD',
                to_currency='RUB',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.UNKNOWN,
                number_format=NumberFormat.UNKNOWN,
            )),
            ('sc burst', PriceRequest(
                amount=None,
                currency='SC',
                to_currency='BURST',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.UNKNOWN,
                number_format=NumberFormat.UNKNOWN,
            )),
            ('burst sc', PriceRequest(
                amount=None,
                currency='BURST',
                to_currency='SC',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.UNKNOWN,
                number_format=NumberFormat.UNKNOWN,
            )),
            ('USD EUR', PriceRequest(
                amount=None,
                currency='USD',
                to_currency='EUR',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.UNKNOWN,
                number_format=NumberFormat.UNKNOWN,
            )),
            ('100 usd rub', PriceRequest(
                amount=Decimal('100'),
                currency='USD',
                to_currency='RUB',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
                number_format=NumberFormat.UNKNOWN,
            )),
            ('100.20 usd rub', PriceRequest(
                amount=Decimal('100.20'),
                currency='USD',
                to_currency='RUB',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
                number_format=NumberFormat.US,
            )),
        ]

        for text, result, in cases:
            self.assertEqual(
                SimpleParser(text).parse(),
                result,
            )

    @patch('app.parsers.simple_parser.get_all_currencies', return_value=['USD', 'RUB', 'EUR', 'BURST', 'SC'])
    def test_bad(self, m):
        cases = [
            '',
            ' ',
            'usd',
            'usdrub',
            'usd rub 100',
            '100usdrub',
            '1,000 usd rub',
            '0,1 usd rub',
            '-100 usd rub',
            '+100 usd rub',
            'BTC USD',
        ]

        for text in cases:
            with self.assertRaises(ValidationException, msg=text):
                SimpleParser(text).parse()
