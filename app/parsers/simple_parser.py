"""
Simple parser

FORMATS: space separator between currencies are required
    "USD EUR"
    "EUR"
    "1000.00 USD EUR"
    "1000USD"
    "1000.00 EUR"
    "EUR USD 1000.00"
    "EUR 1000.00"
    "EUR100"
"""

import re
from decimal import Decimal

from .base import (
    DirectionWriting,
    PriceRequest,
    Parser,
)
from .exceptions import WrongFormatException, UnknownCurrencyException
from app.models import get_all_currencies

REQUEST_PATTERN = r'^(\d{1,12}(\.\d{1,12})?)?\s?([a-zA-Z]{2,6}(\s[a-zA-Z]{2,6})?)\s?(\d{1,12}(\.\d{1,12})?)?$'
REQUEST_PATTERN_COMPILED = re.compile(REQUEST_PATTERN, re.IGNORECASE)

#                                        # usd eur | 100 usd eur | 100.22 usd eur | eur usd 100.33
PRICE_REQUEST_LEFT_AMOUNT = 0            # None    | 100         | 100.22         | None
PRICE_REQUEST_LEFT_AMOUNT_FRACTION = 1   # None    | None        | .22            | None
PRICE_REQUEST_CURRENCIES = 2             # usd eur | usd eur     | usd eur        | eur usd
PRICE_REQUEST_RIGHT_AMOUNT = 4           # None    | None        | None           | 100.33
PRICE_REQUEST_RIGHT_AMOUNT_FRACTION = 5  # None    | None        | None           | .33


class SimpleParser(Parser):
    name = 'SimpleParser'

    def parse(self) -> PriceRequest:
        text = self.text

        obj = REQUEST_PATTERN_COMPILED.match(text)
        if not obj:
            raise WrongFormatException

        groups = obj.groups()
        # print(groups)

        if groups[PRICE_REQUEST_LEFT_AMOUNT] and groups[PRICE_REQUEST_RIGHT_AMOUNT]:
            raise WrongFormatException

        if groups[PRICE_REQUEST_LEFT_AMOUNT]:
            direction_writing = DirectionWriting.LEFT2RIGHT

        elif groups[PRICE_REQUEST_RIGHT_AMOUNT]:
            direction_writing = DirectionWriting.RIGHT2LEFT

        else:
            direction_writing = DirectionWriting.UNKNOWN

        amount = groups[PRICE_REQUEST_LEFT_AMOUNT] or groups[PRICE_REQUEST_RIGHT_AMOUNT]

        if amount:
            amount = Decimal(amount)

        text = groups[PRICE_REQUEST_CURRENCIES]
        text = text.upper()

        currencies = text.split()

        if len(currencies) == 2:
            currency, to_currency = currencies
        else:
            if self.default_currency_position:
                currency, to_currency = currencies[0], self.default_currency
            else:
                currency, to_currency = self.default_currency, currencies[0]

            if direction_writing == DirectionWriting.RIGHT2LEFT:
                currency, to_currency = to_currency, currency

        if direction_writing == DirectionWriting.RIGHT2LEFT:
            currency, to_currency = to_currency, currency

        all_currencies = get_all_currencies()
        if currency not in all_currencies or to_currency not in all_currencies:
            raise UnknownCurrencyException

        return PriceRequest(
            amount=amount,
            currency=currency,
            to_currency=to_currency,
            parser_name=self.name,
            direction_writing=direction_writing,
        )
