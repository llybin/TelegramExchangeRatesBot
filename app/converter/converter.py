from datetime import datetime
from decimal import Decimal

from pyramid_sqlalchemy import Session
from sqlalchemy.orm.exc import NoResultFound

from ..models import Currency, Rate
from ..parsers.base import PriceRequest


# TODO: in work
def convert(price_request: PriceRequest) -> str:
    db_session = Session()
    from_currency = db_session.query(Currency).filter_by(is_active=True, code=price_request.currency).one()
    to_currency = db_session.query(Currency).filter_by(is_active=True, code=price_request.to_currency).one()

    rates = db_session.query(Rate).filter_by(from_currency=from_currency, to_currency=to_currency).all()

    amount = price_request.amount or Decimal('1')
    res = amount * rates[0].rate

    mess = '{} *{}* = {} *{}*'.format(
        money_format(amount),
        price_request.currency,
        money_format(res),
        price_request.to_currency,
    )

    mess += "\n_{:%B %d, %H:%M} UTC_".format(rates[0].last_trade_at)

    return mess


# old code

def rate_difference(rate0: Decimal, rate1: Decimal):
    diff = round(rate1 - rate0, 4)
    percent = round(diff / rate0 * 100, 2)

    return percent, diff


def show_exchange_rate(cur0: str, cur1: str, exrate0: Decimal, exrate1: Decimal,
                       last_trade_at0=None, last_trade_at1=None,
                       up='\U00002B06', down='\U0001F53B') -> str:
    mess = "*{} {} {}*".format(
        cur0,
        cur1,
        money_format(exrate1),
    )

    percent, diff = rate_difference(exrate0, exrate1)

    sign = '+' if percent > 0 else ''
    if percent > 0:
        updown = up
    elif percent < 0:
        updown = down
    else:
        updown = ''

    mess += " {}\n{}{:,.4f} ({}{:,.2f}%)".format(
        updown,
        sign,
        diff,
        sign,
        percent,
    )

    # if last_trade_at0 and last_trade_at1:
    #     mess += last_trade_exrate(cur0, cur1, last_trade_at0, last_trade_at1)
    return mess


def money_format(money):
    return "{:,.4f}".format(money)
