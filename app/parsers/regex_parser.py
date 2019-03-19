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
    "1,000.00 USD"
    "1.000,00 USD"
    "1 000,00 USD"
"""

import re
from decimal import Decimal, InvalidOperation

from babel.core import Locale
from babel.numbers import get_decimal_symbol, get_group_symbol

from ..constants import BIGGEST_VALUE
from .base import (
    DirectionWriting,
    PriceRequest,
    Parser,
)
from .exceptions import WrongFormatException, UnknownCurrencyException
from app.models import get_all_currencies

CURRENCY_SEPARATORS_LIST = (r'\s', ' to ', ' in ', '=', ' = ')
CURRENCY_SEPARATORS_STR = '|'.join(CURRENCY_SEPARATORS_LIST)

# len("123,456,789,012.123456789012") == 28
REQUEST_PATTERN = r'^' \
                  r'([\d\.,\'\s]{1,28})?' \
                  r'\s?' \
                  r'(' \
                  r'[a-zA-Z]{2,6}' \
                  r'((%(sep)s)?' \
                  r'[a-zA-Z]{2,6})' \
                  r'?)' \
                  r'\s?' \
                  r'([\d.,\'\s]{1,28})?' \
                  r'$' % {'sep': CURRENCY_SEPARATORS_STR}

REQUEST_PATTERN_COMPILED = re.compile(REQUEST_PATTERN, re.IGNORECASE)

#                               # usd eur | 100 usd eur | 100.22 usd eur | eur usd 100.33
PRICE_REQUEST_LEFT_AMOUNT = 0   # None    | 100         | 100.22         | None
PRICE_REQUEST_CURRENCIES = 1    # usd eur | usd eur     | usd eur        | eur usd
PRICE_REQUEST_RIGHT_AMOUNT = 4  # None    | None        | None           | 100.33


# https://github.com/python-babel/babel/issues/637
def parse_decimal(string, locale):
    locale = Locale.parse(locale)
    decimal_symbol = get_decimal_symbol(locale)
    group_symbol = get_group_symbol(locale)
    group_symbol = ' ' if group_symbol == '\xa0' else group_symbol
    return Decimal(string.replace(group_symbol, '').replace(decimal_symbol, '.'))


class RegexParser(Parser):
    name = 'RegexParser'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.all_currencies = get_all_currencies()

    def is_currency_recognized(self, currency: str) -> bool:
        return currency in self.all_currencies

    def parse_amount(self, text: str) -> Decimal:
        locales = [self.locale, 'en', 'ru', 'de']
        for l in locales:
            try:
                number = parse_decimal(text, locale=l)
                if number >= BIGGEST_VALUE:
                    raise WrongFormatException
                else:
                    return number
            except InvalidOperation:
                continue

        raise WrongFormatException

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
            amount = self.parse_amount(amount)

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
