from decimal import Decimal

from .. import constants
from .converter import PriceRequestResult


def format_price_request_result(prr: PriceRequestResult) -> str:
    # convert mode - if amount is not None
    if prr.price_request.amount is not None:
        amount = prr.price_request.amount
        res = amount * prr.rate

        mess = f'{money_format(amount)} *{prr.price_request.currency}* = {money_format(res)} *{prr.price_request.to_currency}*'

    else:
        mess = '*{} {} {}*'.format(
            prr.price_request.currency,
            prr.price_request.to_currency,
            money_format(prr.rate),
        )

        if prr.rate and prr.rate_open:
            diff = rate_difference(prr.rate, prr.rate_open)
            percent = rate_percent(prr.rate, prr.rate_open)
            sign = get_sign(percent)
            arrow = get_arrow(percent)

            mess += f' {arrow}'
            mess += f'\n{sign}{diff:,.4f} ({sign}{percent:,.2f}%)'

        if prr.low24h and prr.high24h:
            mess += f'\n*Low*: {prr.low24h:,.2f} *High*: {prr.high24h:,.2f}'

    mess += f'\n_[{" + ".join(prr.exchanges)}]_'
    mess += f'\n_{prr.last_trade_at:%B %d, %H:%M} UTC_'

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


def money_format(money: Decimal) -> str:
    return '{:,.4f}'.format(money)
