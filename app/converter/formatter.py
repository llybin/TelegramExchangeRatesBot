from decimal import Decimal

from .. import constants
from .converter import PriceRequestResult


def format_price_request_result(prr: PriceRequestResult) -> str:
    # convert mode - if amount is not None
    if prr.price_request.amount is not None:
        amount = prr.price_request.amount
        res = amount * prr.rate

        mess = f'{nice_amount(amount)} *{prr.price_request.currency}* = {nice_amount(res)} *{prr.price_request.to_currency}*'

    else:
        mess = '*{} {} {}*'.format(
            prr.price_request.currency,
            prr.price_request.to_currency,
            nice_round(prr.rate, 4)
        )

        if prr.rate and prr.rate_open:
            diff = rate_difference(prr.rate, prr.rate_open)
            percent = rate_percent(prr.rate, prr.rate_open)
            sign = get_sign(percent)
            arrow = get_arrow(percent)

            mess += f' {arrow}'
            mess += f'\n{sign}{nice_amount(diff)} ({sign}{nice_percent(percent)}%)'

        if prr.low24h and prr.high24h:
            mess += f'\n*Low*: {nice_amount(prr.low24h)} *High*: {nice_amount(prr.high24h)}'

    mess += f'\n_[{" + ".join(prr.exchanges)}]_'

    # Baba Vanga
    if prr.last_trade_at.year == 1996:
        mess += f'\n_{prr.last_trade_at:%d %B %Y}_'
    else:
        mess += f'\n_{prr.last_trade_at:%d %B, %H:%M} UTC_'

    return mess


def get_sign(percent: Decimal) -> str:
    # return nothing because if minus then amount already contain minus
    return '+' if percent > 0 else ''


def get_arrow(percent: Decimal) -> str:
    if percent > 0:
        return constants.arrows_different_color['up']
    elif percent < 0:
        return constants.arrows_different_color['down']
    else:
        return ''


def rate_difference(rate0: Decimal, rate1: Decimal) -> Decimal:
    return rate1 - rate0


def rate_percent(rate0: Decimal, rate1: Decimal) -> Decimal:
    diff = rate_difference(rate0, rate1)
    return diff / rate0 * 100


def nice_amount(number):
    return f'{nice_round(number, 4):f}'


def nice_percent(number):
    return f'{nice_round(number, 2):f}'


def nice_round(number: Decimal, ndigits: int, ndigits2: int = 2) -> Decimal:
    """
    Round a number to a given ndigits precision in decimal digits
    If a number is too small, to round a number with dynamic precision with a last ndigits2 non-zero digits
    """
    number_parts = f'{number:.{constants.decimal_scale}f}'.split('.')

    if len(number_parts) == 1:
        return number
    else:
        str_fract = number_parts[1]

    k = ndigits
    if str_fract[0] == '0':
        for i in range(1, len(str_fract)):
            if str_fract[i - 1] == '0' and str_fract[i] != '0':
                k = i + ndigits2
                break

    return round(number, k)
