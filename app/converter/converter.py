from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import orm

from suite.database import Session

from app.constants import BIGGEST_VALUE
from app.models import Currency, Rate, Exchange
from app.parsers.base import PriceRequest
from .base import PriceRequestResult
from .exceptions import NoRatesException, OverflowException


def convert(price_request: PriceRequest) -> PriceRequestResult:
    if price_request.currency == price_request.to_currency:
        return PriceRequestResult(
            price_request=price_request,
            exchanges=['Baba Vanga'],
            rate=Decimal('1'),
            last_trade_at=datetime(1996, 8, 11),
        )

    if price_request.amount == 0:
        return PriceRequestResult(
            price_request=price_request,
            exchanges=['Baba Vanga'],
            rate=Decimal('0'),
            last_trade_at=datetime(1996, 8, 11),
        )

    from_currency = Session.query(Currency).filter_by(code=price_request.currency).one()
    to_currency = Session.query(Currency).filter_by(code=price_request.to_currency).one()

    rate_obj = Session.query(Rate).filter_by(
        from_currency=from_currency,
        to_currency=to_currency
    ).join(Exchange).filter(
        Exchange.is_active == sa.true()
    ).order_by(sa.desc(Exchange.weight)).first()

    if rate_obj:
        price_request_result = PriceRequestResult(
            price_request=price_request,
            exchanges=[rate_obj.exchange.name],
            rate=rate_obj.rate,
            rate_open=rate_obj.rate_open,
            last_trade_at=rate_obj.last_trade_at,
            low24h=rate_obj.low24h,
            high24h=rate_obj.high24h,
        )

    else:
        Rate0 = orm.aliased(Rate)
        Rate1 = orm.aliased(Rate)
        Exchange0 = orm.aliased(Exchange)
        Exchange1 = orm.aliased(Exchange)

        rate_obj = Session.query(Rate0, Rate1, (Exchange0.weight + Exchange1.weight).label('w')).filter_by(
            from_currency=from_currency
        ).join(
            Rate1, sa.and_(Rate1.from_currency_id == Rate0.to_currency_id, Rate1.to_currency == to_currency)
        ).join(
            Exchange0, sa.and_(Exchange0.id == Rate0.exchange_id, Exchange0.is_active == sa.true())
        ).join(
            Exchange1, sa.and_(Exchange1.id == Rate1.exchange_id, Exchange1.is_active == sa.true())
        ).order_by(sa.desc('w')).first()

        if rate_obj:
            rate = combine_values(rate_obj[0].rate, rate_obj[1].rate)
            rate_open = combine_values(rate_obj[0].rate_open, rate_obj[1].rate_open)
            low24h = high24h = None

            price_request_result = PriceRequestResult(
                price_request=price_request,
                exchanges=[rate_obj[0].exchange.name, rate_obj[1].exchange.name],
                rate=rate,
                rate_open=rate_open,
                last_trade_at=min(rate_obj[0].last_trade_at, rate_obj[1].last_trade_at),
                low24h=low24h,
                high24h=high24h,
            )

        else:
            raise NoRatesException

    check_overflow(price_request_result)

    return price_request_result


def check_overflow(prr: PriceRequestResult):
    for a in ['rate', 'rate_open', 'low24h', 'high24h']:
        value = getattr(prr, a)
        if value and value > BIGGEST_VALUE:
            raise OverflowException


def combine_values(value0: Decimal or None, value1: Decimal or None) -> (Decimal or None):
    if value0 and value1:
        return value0 * value1
    else:
        return None
