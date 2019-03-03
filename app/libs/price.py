import re
from decimal import Decimal
from typing import NamedTuple

from suite.conf import settings


# TODO: not so good e.g. 00.1 or 00000.1, many first zeros
MONEY_PATTERN_EU = r'((\d{1,3}(\.\d{3}){1,3}|\d{1,12})(,\d{1,8})?)'
MONEY_PATTERN_US = r'((\d{1,3}(,\d{3}){1,3}|\d{1,12})(\.\d{1,8})?)'

MONEY_PATTERN = f'{MONEY_PATTERN_EU}|{MONEY_PATTERN_US}'

CURRENCY_SEPARATORS_LIST = (' to ', ' in ', '=', ' = ', r'\s')
CURRENCY_SEPARATORS_STR = '|'.join(CURRENCY_SEPARATORS_LIST)
CURRENCY_SEPARATORS_PATTERN = re.compile(f'({CURRENCY_SEPARATORS_STR})')


def price_request_pattern() -> str:
    # left to right, 12USDEUR, 12USD, USDEUR, EUR, ...
    #       (12)?  ?(          USD((  )?          EUR)?)
    l2r = r'(%s)?\s?([a-zA-Z]{3,5}((%s)?[a-zA-Z]{3,5})?)' % (MONEY_PATTERN, CURRENCY_SEPARATORS_STR)

    # right to left, EURUSD12, USD12, EURUSD, EUR, ...
    #       ((          EUR(  )?)?          USD)  ?(12)?
    r2l = r'(([a-zA-Z]{3,5}(%s)?)?[a-zA-Z]{3,5})\s?(%s)?' % (CURRENCY_SEPARATORS_STR, MONEY_PATTERN)

    return f'({l2r}|{r2l})$'


PRICE_REQUEST_PATTERN = re.compile(price_request_pattern(), re.IGNORECASE)

PRICE_REQUEST_LEFT_AMOUNT = 1
PRICE_REQUEST_LEFT_AMOUNT_FRACTION = 5
PRICE_REQUEST_LEFT_CURRENCY = 10
PRICE_REQUEST_RIGHT_CURRENCY = 13
PRICE_REQUEST_RIGHT_AMOUNT = 16
PRICE_REQUEST_RIGHT_AMOUNT_FRACTION = 20


class MoneyFormat(object):
    UNKNOWN = None
    US = 'US'
    EU = 'EU'


class WritingTextFormat(object):
    UNKNOWN = None
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'


class PriceRequest(NamedTuple):
    amount: Decimal or None
    first_currency: str
    second_currency: str or None
    writing_text: WritingTextFormat
    money_format: MoneyFormat


class ValidationException(Exception):
    pass


class WrongFormatException(ValidationException):
    pass


class UnknownCurrencyException(ValidationException):
    pass


def parse_price_text(text: str) -> PriceRequest:
    obj = PRICE_REQUEST_PATTERN.match(''.join(text))
    if not obj:
        raise WrongFormatException

    groups = obj.groups()
    # print(groups)

    amount = groups[PRICE_REQUEST_LEFT_AMOUNT] or groups[PRICE_REQUEST_RIGHT_AMOUNT] or None
    text = groups[PRICE_REQUEST_LEFT_CURRENCY] or groups[PRICE_REQUEST_RIGHT_CURRENCY]

    writing_text = WritingTextFormat.UNKNOWN
    money_format = MoneyFormat.UNKNOWN

    if amount:
        # 1,000.111 -> 1000.111
        amount = amount.replace(',', '')
        amount = Decimal(amount)

        # TODO:
        # if bool(groups[PRICE_REQUEST_LEFT_AMOUNT]):
        #     writing_text = WritingTextFormat.LEFT
        # else:
        #     writing_text = WritingTextFormat.RIGHT
        #
        # if writing_text == WritingTextFormat.LEFT:
        #     amount_fraction_pos = PRICE_REQUEST_LEFT_AMOUNT_FRACTION
        # else:
        #     amount_fraction_pos = PRICE_REQUEST_RIGHT_AMOUNT_FRACTION
        #
        # if groups[amount_fraction_pos]:
        #     if '.' in groups[amount_fraction_pos]:
        #         money_format = MoneyFormat.US
        #     else:
        #         money_format = MoneyFormat.EU
        #
        # if money_format == MoneyFormat.US:
        #     # 1,000.111 -> 1000.111
        #     amount = amount.replace(',', '')
        #     amount = Decimal(amount)
        #
        # else:
        #     # 1.000,111 -> 1000.111
        #     amount = amount.replace('.', '')
        #     amount = amount.replace(',', '.')
        #     amount = Decimal(amount)

    # clear separators
    text = CURRENCY_SEPARATORS_PATTERN.sub('', text)

    text = text.upper()
    first_currency = second_currency = None

    if len(text) < 6:
        first_currency = text
        if first_currency not in settings.CURRENCIES:
            raise UnknownCurrencyException

    elif len(text) == 6:
        first_currency = text[0:3]
        second_currency = text[3:]

        if first_currency not in settings.CURRENCIES or second_currency not in settings.CURRENCIES:
            raise UnknownCurrencyException

    else:
        # TODO: USD EUR BTC first
        for x in settings.CURRENCIES:
            if text.startswith(x):
                if text[len(x):] in settings.CURRENCIES:
                    first_currency = x
                    second_currency = text[len(x):]
                else:
                    continue

        if not first_currency and not second_currency:
            raise UnknownCurrencyException

    return PriceRequest(
        amount=amount,
        first_currency=first_currency,
        second_currency=second_currency,
        writing_text=writing_text,
        money_format=money_format,
    )
