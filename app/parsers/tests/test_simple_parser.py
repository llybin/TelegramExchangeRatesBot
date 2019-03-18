import unittest
from decimal import Decimal
from unittest.mock import patch

from ..base import PriceRequest, DirectionWriting
from ..exceptions import ValidationException
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
            )),
            ('rub', PriceRequest(
                amount=None,
                currency='RUB',
                to_currency='USD',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )),
            ('sc burst', PriceRequest(
                amount=None,
                currency='SC',
                to_currency='BURST',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )),
            ('burst sc', PriceRequest(
                amount=None,
                currency='BURST',
                to_currency='SC',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )),
            ('USD EUR', PriceRequest(
                amount=None,
                currency='USD',
                to_currency='EUR',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.UNKNOWN,
            )),
            ('100 usd rub', PriceRequest(
                amount=Decimal('100'),
                currency='USD',
                to_currency='RUB',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
            )),
            ('100 rub', PriceRequest(
                amount=Decimal('100'),
                currency='RUB',
                to_currency='USD',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
            )),
            ('100rub', PriceRequest(
                amount=Decimal('100'),
                currency='RUB',
                to_currency='USD',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
            )),
            ('100.20 usd rub', PriceRequest(
                amount=Decimal('100.20'),
                currency='USD',
                to_currency='RUB',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
            )),
            ('100.20usd rub', PriceRequest(
                amount=Decimal('100.20'),
                currency='USD',
                to_currency='RUB',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
            )),
            ('usd rub 100', PriceRequest(
                amount=Decimal('100'),
                currency='RUB',
                to_currency='USD',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.RIGHT2LEFT,
            )),
            ('rub 100', PriceRequest(
                amount=Decimal('100'),
                currency='RUB',
                to_currency='USD',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.RIGHT2LEFT,
            )),
            ('rub100', PriceRequest(
                amount=Decimal('100'),
                currency='RUB',
                to_currency='USD',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.RIGHT2LEFT,
            )),
            ('usd rub 100.20', PriceRequest(
                amount=Decimal('100.20'),
                currency='RUB',
                to_currency='USD',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.RIGHT2LEFT,
            )),
            ('usd rub100.20', PriceRequest(
                amount=Decimal('100.20'),
                currency='RUB',
                to_currency='USD',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.RIGHT2LEFT,
            )),
        ]

        for text, result, in cases:
            self.assertEqual(
                SimpleParser(text, 'USD', True).parse(),
                result,
            )

        self.assertEqual(
            SimpleParser('100rub', 'USD', False).parse(),
            PriceRequest(
                amount=Decimal('100'),
                currency='USD',
                to_currency='RUB',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.LEFT2RIGHT,
            ),
        )

        self.assertEqual(
            SimpleParser('rub100', 'USD', False).parse(),
            PriceRequest(
                amount=Decimal('100'),
                currency='USD',
                to_currency='RUB',
                parser_name='SimpleParser',
                direction_writing=DirectionWriting.RIGHT2LEFT,
            ),
        )

    @patch('app.parsers.simple_parser.get_all_currencies', return_value=['USD', 'RUB', 'EUR', 'BURST', 'SC'])
    def test_bad(self, m):
        cases = [
            '',
            ' ',
            '100',
            '100.22',
            'usdrub',
            '100usdrub',
            'usdrub100',
            '100usd rub100',
            '1,000 usd rub',
            '0,1 usd rub',
            '-100 usd rub',
            '+100 usd rub',
            'BTC USD',
        ]

        for text in cases:
            with self.assertRaises(ValidationException, msg=text):
                SimpleParser(text, 'USD', True).parse()
