import re
from decimal import Decimal

from suite.conf import settings

from .base import (
    DirectionWriting,
    PriceRequest,
    Parser,
)
from .number_format import NUMBER_PATTERN_ALL, NumberFormat
from .exceptions import WrongFormatException, UnknownCurrencyException


CURRENCY_SEPARATORS_LIST = (' to ', ' in ', '=', ' = ', r'\s')
CURRENCY_SEPARATORS_STR = '|'.join(CURRENCY_SEPARATORS_LIST)
CURRENCY_SEPARATORS_PATTERN = re.compile(f'({CURRENCY_SEPARATORS_STR})')


def price_request_pattern() -> str:
    # left to right, 12USDEUR, 12USD, USDEUR, EUR, ...
    #       (12)?  ?(          USD((  )?          EUR)?)
    l2r = r'(%s)?\s?([a-zA-Z]{3,5}((%s)?[a-zA-Z]{3,5})?)' % (NUMBER_PATTERN_ALL, CURRENCY_SEPARATORS_STR)

    # right to left, EURUSD12, USD12, EURUSD, EUR, ...
    #       ((          EUR(  )?)?          USD)  ?(12)?
    r2l = r'(([a-zA-Z]{3,5}(%s)?)?[a-zA-Z]{3,5})\s?(%s)?' % (CURRENCY_SEPARATORS_STR, NUMBER_PATTERN_ALL)

    return f'({l2r}|{r2l})$'


PRICE_REQUEST_PATTERN = re.compile(price_request_pattern(), re.IGNORECASE)

PRICE_REQUEST_LEFT_AMOUNT = 1
PRICE_REQUEST_LEFT_AMOUNT_FRACTION = 5
PRICE_REQUEST_LEFT_CURRENCY = 10
PRICE_REQUEST_RIGHT_CURRENCY = 13
PRICE_REQUEST_RIGHT_AMOUNT = 16
PRICE_REQUEST_RIGHT_AMOUNT_FRACTION = 20


class RegexParser(Parser):
    def parse(self) -> PriceRequest:
        text = self.text

        obj = PRICE_REQUEST_PATTERN.match(''.join(text))
        if not obj:
            raise WrongFormatException

        groups = obj.groups()
        # print(groups)

        amount = groups[PRICE_REQUEST_LEFT_AMOUNT] or groups[PRICE_REQUEST_RIGHT_AMOUNT] or None
        text = groups[PRICE_REQUEST_LEFT_CURRENCY] or groups[PRICE_REQUEST_RIGHT_CURRENCY]

        direction_writing = DirectionWriting.UNKNOWN
        number_format = NumberFormat.UNKNOWN

        if amount:
            # 1,000.111 -> 1000.111
            amount = amount.replace(',', '')
            amount = Decimal(amount)

            # TODO:
            # if bool(groups[PRICE_REQUEST_LEFT_AMOUNT]):
            #     direction_writing = WritingTextFormat.LEFT
            # else:
            #     direction_writing = WritingTextFormat.RIGHT
            #
            # if direction_writing == WritingTextFormat.LEFT:
            #     amount_fraction_pos = PRICE_REQUEST_LEFT_AMOUNT_FRACTION
            # else:
            #     amount_fraction_pos = PRICE_REQUEST_RIGHT_AMOUNT_FRACTION
            #
            # if groups[amount_fraction_pos]:
            #     if '.' in groups[amount_fraction_pos]:
            #         number_format = MoneyFormat.US
            #     else:
            #         number_format = MoneyFormat.EU
            #
            # if number_format == MoneyFormat.US:
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
            direction_writing=direction_writing,
            number_format=number_format,
        )
