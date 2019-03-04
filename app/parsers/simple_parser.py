"""
ONLY FORMAT: "USD EUR" or "1000.00 USD EUR"
"""

import re
from decimal import Decimal

from suite.conf import settings

from .base import (
    DirectionWriting,
    PriceRequest,
    Parser,
)
from .number_format import NUMBER_PATTERN_DOT_SIMPLE
from .exceptions import WrongFormatException, UnknownCurrencyException


def price_request_pattern() -> str:
    return r'((%s)\s)?([a-zA-Z]{3,5}\s[a-zA-Z]{3,5})' % NUMBER_PATTERN_DOT_SIMPLE


PRICE_REQUEST_PATTERN = re.compile(price_request_pattern(), re.IGNORECASE)

PRICE_REQUEST_AMOUNT = 0
PRICE_REQUEST_CURRENCY = 3


class SimpleParser(Parser):
    def parse(self) -> PriceRequest:
        text = self.text

        obj = PRICE_REQUEST_PATTERN.match(''.join(text))
        if not obj:
            raise WrongFormatException

        groups = obj.groups()

        amount = groups[PRICE_REQUEST_AMOUNT] or None
        text = groups[PRICE_REQUEST_CURRENCY]

        if amount:
            amount = Decimal(amount)
            direction_writing = DirectionWriting.LEFT2RIGHT
        else:
            direction_writing = DirectionWriting.UNKNOWN

        text = text.upper()
        first_currency, second_currency = text.split()

        if first_currency not in settings.CURRENCIES or second_currency not in settings.CURRENCIES:
            raise UnknownCurrencyException

        return PriceRequest(
            amount=amount,
            first_currency=first_currency,
            second_currency=second_currency,
            direction_writing=direction_writing,
        )
