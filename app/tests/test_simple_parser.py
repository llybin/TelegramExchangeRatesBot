from decimal import Decimal
import unittest


from app.parsers.base import PriceRequest, DirectionWriting
from app.parsers.exceptions import ValidationException
from app.parsers.number_format import NumberFormat
from app.parsers.simple_parser import SimpleParser


class SimpleParserTest(unittest.TestCase):
    def test_good(self):
        cases = [
            ('usd rub', PriceRequest(
                amount=None,
                first_currency='USD',
                second_currency='RUB',
                direction_writing=DirectionWriting.UNKNOWN,
                number_format=NumberFormat.UNKNOWN,
            )),
            ('USD EUR', PriceRequest(
                amount=None,
                first_currency='USD',
                second_currency='EUR',
                direction_writing=DirectionWriting.UNKNOWN,
                number_format=NumberFormat.UNKNOWN,
            )),
            ('100 usd rub', PriceRequest(
                amount=Decimal('100'),
                first_currency='USD',
                second_currency='RUB',
                direction_writing=DirectionWriting.LEFT2RIGHT,
                number_format=NumberFormat.UNKNOWN,
            )),
            ('100.20 usd rub', PriceRequest(
                amount=Decimal('100.20'),
                first_currency='USD',
                second_currency='RUB',
                direction_writing=DirectionWriting.LEFT2RIGHT,
                number_format=NumberFormat.US,
            )),
        ]

        for text, result, in cases:
            self.assertEqual(
                SimpleParser(text).parse(),
                result
            )

    def test_bad(self):
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
        ]

        for text in cases:
            with self.assertRaises(ValidationException, msg=text):
                SimpleParser(text).parse()
