"""
Simple parser for understanding how it work.

ONLY FORMAT: "USD EUR" or "1000.00 USD EUR", required spaces
"""

import re
from decimal import Decimal

from suite.conf import settings

from .base import (
    DirectionWriting,
    PriceRequest,
    Parser,
)
from .number_format import NUMBER_PATTERN_DOT_SIMPLE, NumberFormat
from .exceptions import WrongFormatException, UnknownCurrencyException


REQUEST_PATTERN = r'^(%s\s)?([a-zA-Z]{3,5}\s[a-zA-Z]{3,5})$' % NUMBER_PATTERN_DOT_SIMPLE
REQUEST_PATTERN_COMPILED = re.compile(REQUEST_PATTERN, re.IGNORECASE)

#                                  # usd eur | 100 usd eur | 100.22 usd eur
PRICE_REQUEST_AMOUNT = 0           # None    | 100         | 100.22
PRICE_REQUEST_AMOUNT_FRACTION = 2  # None    | None        | .22
PRICE_REQUEST_CURRENCIES = 3       # usd eur | usd eur     | usd eur


class SimpleParser(Parser):
    def parse(self) -> PriceRequest:
        text = self.text

        obj = REQUEST_PATTERN_COMPILED.match(text)
        if not obj:
            raise WrongFormatException

        groups = obj.groups()

        amount = groups[PRICE_REQUEST_AMOUNT]
        text = groups[PRICE_REQUEST_CURRENCIES]

        number_format = NumberFormat.UNKNOWN
        direction_writing = DirectionWriting.UNKNOWN

        if amount:
            amount = Decimal(amount)
            direction_writing = DirectionWriting.LEFT2RIGHT

            # dot in fraction, to be sure need to look at the numerator also, contains spaces or commas and etc.
            if groups[PRICE_REQUEST_AMOUNT_FRACTION] and '.' in groups[PRICE_REQUEST_AMOUNT_FRACTION]:
                number_format = NumberFormat.US

        text = text.upper()
        first_currency, second_currency = text.split()

        if first_currency not in settings.CURRENCIES or second_currency not in settings.CURRENCIES:
            raise UnknownCurrencyException

        return PriceRequest(
            amount=amount,
            first_currency=first_currency,
            second_currency=second_currency,
            direction_writing=direction_writing,
            number_format=number_format,
        )
