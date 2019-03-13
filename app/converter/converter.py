from decimal import Decimal

from pyramid_sqlalchemy import Session
import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy import orm
from sqlalchemy.orm.exc import NoResultFound

from .. import constants
from ..models import Currency, Rate, Exchange
from ..parsers.base import PriceRequest


# TODO: in work
def convert(price_request: PriceRequest) -> str:
    db_session = Session()
    from_currency = db_session.query(Currency).filter_by(code=price_request.currency).one()
    to_currency = db_session.query(Currency).filter_by(code=price_request.to_currency).one()

    # if from_currency == to_currency return 1
    # check amount zero overflow
    # bitfinex is slow, may be sort by last_trade? not updated old data exclude or delete?
    # enabled exchanges only

    rate_obj = db_session.query(Rate).filter_by(
        from_currency=from_currency,
        to_currency=to_currency
    ).join(
        Exchange
    ).order_by(sa.desc(Exchange.weight)).first()

    if rate_obj:
        exchanges = rate_obj.exchange.name
        rate = rate_obj.rate
        rate_open = rate_obj.rate_open
        last_trade_at = rate_obj.last_trade_at

    else:
        Rate0 = orm.aliased(Rate)
        Rate1 = orm.aliased(Rate)
        Exchange0 = orm.aliased(Exchange)
        Exchange1 = orm.aliased(Exchange)

        rate_obj = db_session.query(Rate0, Rate1, (Exchange0.weight + Exchange1.weight).label('w')).filter_by(
            from_currency=from_currency
        ).join(
            Rate1, sa.and_(Rate1.from_currency_id == Rate0.to_currency_id, Rate1.to_currency == to_currency)
        ).join(
            Exchange0, Exchange0.id == Rate0.exchange_id
        ).join(
            Exchange1, Exchange1.id == Rate1.exchange_id
        ).order_by(sa.desc('w')).first()

        if rate_obj:
            rate = rate_obj[0].rate * rate_obj[1].rate
            if rate_obj[0].rate_open and rate_obj[1].rate_open:
                rate_open = rate_obj[0].rate_open * rate_obj[1].rate_open
            else:
                rate_open = None
            last_trade_at = min(rate_obj[0].last_trade_at, rate_obj[1].last_trade_at)

            exchanges = f'{rate_obj[0].exchange.name} + {rate_obj[1].exchange.name}'

        else:
            return 'No rates'

    if price_request.amount:
        # convert mode

        amount = price_request.amount
        res = amount * rate

        mess = f'{money_format(amount)} *{price_request.currency}* = {money_format(res)} *{price_request.to_currency}*'
    else:
        mess = '*{} {} {}*'.format(
            price_request.currency,
            price_request.to_currency,
            money_format(rate),
        )

        if rate_open:
            percent, diff = rate_difference(rate, rate_open)

            sign = '+' if percent > 0 else ''
            if percent > 0:
                updown = constants.arrows_different_color['up']
            elif percent < 0:
                updown = constants.arrows_different_color['down']
            else:
                updown = ''

            mess += f' {updown}\n{sign}{diff:,.4f} ({sign}{percent:,.2f}%)'

    mess += f'\n_{last_trade_at:%B %d, %H:%M} UTC_'
    mess += f'\n_{exchanges}_'

    return mess


def rate_difference(rate0: Decimal, rate1: Decimal) -> (float, float):
    diff = round(rate1 - rate0, 4)
    percent = round(diff / rate0 * 100, 2)

    return percent, diff


def money_format(money: Decimal) -> str:
    return '{:,.4f}'.format(money)
