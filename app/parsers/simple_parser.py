"""
Simple parser for understanding how it work.

ONLY FORMAT: "USD EUR" or "1000.00 USD EUR", required spaces
"""

import re
from decimal import Decimal

from .base import (
    DirectionWriting,
    PriceRequest,
    Parser,
)
from .number_format import NUMBER_PATTERN_DOT_SIMPLE, NumberFormat
from .exceptions import WrongFormatException, UnknownCurrencyException
from app.models import get_all_currencies

REQUEST_PATTERN = r'^(%s\s)?([a-zA-Z]{2,6}\s[a-zA-Z]{2,6})$' % NUMBER_PATTERN_DOT_SIMPLE
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
        currency, to_currency = text.split()

        all_currencies = get_all_currencies()
        if currency not in all_currencies or to_currency not in all_currencies:
            raise UnknownCurrencyException

        return PriceRequest(
            amount=amount,
            currency=currency,
            to_currency=to_currency,
            direction_writing=direction_writing,
            number_format=number_format,
        )
