"""
Regex parser

FORMATS:
    "USD EUR"
    "USDEUR"
    "EUR"
    "1000.00 USD EUR"
    "1000.00USDEUR"
    "1000USD"
    "1000.00 EUR"
    "EUR USD 1000.00"
    "EURUSD1000.00"
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

CURRENCY_SEPARATORS_LIST = (r'\s', ' to ', ' in ', '=', ' = ')
CURRENCY_SEPARATORS_STR = '|'.join(CURRENCY_SEPARATORS_LIST)

# TODO: digits with grouping
REQUEST_PATTERN = r'^' \
                  r'(\d{1,12}(\.\d{1,12})?)?' \
                  r'\s?' \
                  r'(' \
                  r'[a-zA-Z]{2,6}' \
                  r'((%(sep)s)?' \
                  r'[a-zA-Z]{2,6})' \
                  r'?)' \
                  r'\s?' \
                  r'(\d{1,12}(\.\d{1,12})?)?' \
                  r'$' % {'sep': CURRENCY_SEPARATORS_STR}

REQUEST_PATTERN_COMPILED = re.compile(REQUEST_PATTERN, re.IGNORECASE)

#                                        # usd eur | 100 usd eur | 100.22 usd eur | eur usd 100.33
PRICE_REQUEST_LEFT_AMOUNT = 0            # None    | 100         | 100.22         | None
PRICE_REQUEST_CURRENCIES = 2             # usd eur | usd eur     | usd eur        | eur usd
PRICE_REQUEST_RIGHT_AMOUNT = 5           # None    | None        | None           | 100.33


class RegexParser(Parser):
    name = 'RegexParser'

    def __init__(self, text: str, default_currency: str, default_currency_position: bool):
        super().__init__(text, default_currency, default_currency_position)
        self.all_currencies = get_all_currencies()

    def is_currency_recognized(self, currency: str) -> bool:
        return currency in self.all_currencies

    @staticmethod
    def split_currencies(text: str) -> list:
        default_sep = ' '

        for s in CURRENCY_SEPARATORS_LIST[1:]:
            text = text.replace(s.upper(), default_sep)

        return text.split()

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

        currencies = self.split_currencies(text)

        if len(currencies) == 2:
            currency, to_currency = currencies[0], currencies[1]
            if not self.is_currency_recognized(currency) or not self.is_currency_recognized(to_currency):
                raise UnknownCurrencyException

        elif len(currencies) == 1 and self.is_currency_recognized(currencies[0]):
            if self.default_currency_position:
                currency, to_currency = currencies[0], self.default_currency
            else:
                currency, to_currency = self.default_currency, currencies[0]

            if direction_writing == DirectionWriting.RIGHT2LEFT:
                currency, to_currency = to_currency, currency

        else:
            currencies = currencies[0]
            for x in range(2, len(currencies) - 1):
                currency, to_currency = currencies[:x], currencies[x:]
                if self.is_currency_recognized(currency) and self.is_currency_recognized(to_currency):
                    break
            else:
                raise WrongFormatException

        if direction_writing == DirectionWriting.RIGHT2LEFT:
            currency, to_currency = to_currency, currency

        return PriceRequest(
            amount=amount,
            currency=currency,
            to_currency=to_currency,
            parser_name=self.name,
            direction_writing=direction_writing,
        )
