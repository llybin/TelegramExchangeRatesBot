from decimal import Decimal
import math

from babel.numbers import format_decimal

from .. import constants
from ..models import Chat
from ..parsers.base import DirectionWriting
from .converter import PriceRequestResult


# TODO: refact
def format_price_request_result(prr: PriceRequestResult, chat: Chat) -> str:
    cf = ChatFormat(chat.is_colored_arrows, chat.money_format.value)

    # convert mode - if amount is not None
    if prr.price_request.amount is not None:
        amount = prr.price_request.amount
        res = amount * prr.rate

        if prr.price_request.direction_writing == DirectionWriting.RIGHT2LEFT:
            mess = f'{cf.amount(res)} *{prr.price_request.to_currency}* = {cf.amount(amount)} *{prr.price_request.currency}*'
        else:
            mess = f'{cf.amount(amount)} *{prr.price_request.currency}* = {cf.amount(res)} *{prr.price_request.to_currency}*'

    else:
        mess = f'*{prr.price_request.currency} {prr.price_request.to_currency} {cf.amount(prr.rate)}*'

        if prr.rate and prr.rate_open:
            diff = rate_difference(prr.rate, prr.rate_open)
            percent = rate_percent(prr.rate, prr.rate_open)
            sign = cf.get_sign(percent)
            arrow = cf.get_arrow(percent)

            mess += f' {arrow}'
            mess += f'\n{sign}{cf.amount(diff)} ({sign}{cf.percent(percent)}%)'

        if prr.low24h and prr.high24h:
            mess += f'\n*Low*: {cf.amount(prr.low24h)} *High*: {cf.amount(prr.high24h)}'

    mess += f'\n_[{" + ".join(prr.exchanges)}]_'

    # Baba Vanga
    if prr.last_trade_at.year == 1996:
        mess += f'\n_{prr.last_trade_at:%d %B %Y}_'
    else:
        mess += f'\n_{prr.last_trade_at:%d %B, %H:%M} UTC_'

    return mess


def rate_difference(rate0: Decimal, rate1: Decimal) -> Decimal:
    return rate1 - rate0


def rate_percent(rate0: Decimal, rate1: Decimal) -> Decimal:
    diff = rate_difference(rate0, rate1)
    return diff / rate0 * 100


def nice_round(number: Decimal, ndigits: int) -> Decimal:
    """
    Round a number with dynamic precision with a last ndigits non-zero digits for small number
    """
    if number > 1:
        return round(number, ndigits)

    # split on integer and fraction parts
    str_number_parts = f'{number:f}'.split('.')

    # if no fraction
    if len(str_number_parts) == 1:
        return round(number, ndigits)

    str_fraction = str_number_parts[1]

    k = round(math.log10(abs(Decimal(f'0.{int(str_fraction)}') / (number - int(number)))))

    # if fraction is too small
    if k >= constants.decimal_scale:
        return number.quantize(1)

    if k < ndigits - 1:
        k = ndigits
    else:
        k += ndigits

    return round(number, k)


class ChatFormat(object):
    is_colored_arrows: bool
    money_format: str

    def __init__(self, is_colored_arrows, money_format):
        self.is_colored_arrows = is_colored_arrows
        self.money_format = money_format

    @staticmethod
    def get_sign(number: Decimal) -> str:
        # return nothing because if minus then amount already contain minus
        return '+' if number > 0 else ''

    def get_arrow(self, percent: Decimal) -> str:
        if percent > 0:
            return constants.arrows[self.is_colored_arrows]['up']
        elif percent < 0:
            return constants.arrows[self.is_colored_arrows]['down']
        else:
            return ''

    def amount(self, number):
        return format_decimal(nice_round(number, 4), locale=self.money_format, decimal_quantization=False)

    def percent(self, number):
        return format_decimal(nice_round(number, 2), locale=self.money_format, decimal_quantization=False)
