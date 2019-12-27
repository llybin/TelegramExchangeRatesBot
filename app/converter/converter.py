from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import orm

from app.constants import BIGGEST_VALUE
from app.converter.base import PriceRequestResult
from app.converter.exceptions import NoRatesException, OverflowException
from app.models import Currency, Exchange, Rate
from app.parsers.base import PriceRequest
from suite.database import Session


def convert(price_request: PriceRequest) -> PriceRequestResult:
    if price_request.currency == price_request.to_currency:
        return PriceRequestResult(
            price_request=price_request,
            exchanges=["Baba Vanga"],
            rate=Decimal("1"),
            last_trade_at=datetime(1996, 8, 11),
        )

    if price_request.amount == 0:
        return PriceRequestResult(
            price_request=price_request,
            exchanges=["Baba Vanga"],
            rate=Decimal("0"),
            last_trade_at=datetime(1996, 8, 11),
        )

    from_currency = Session.query(Currency).filter_by(code=price_request.currency).one()
    to_currency = (
        Session.query(Currency).filter_by(code=price_request.to_currency).one()
    )

    rate_obj = (
        Session.query(Rate)
        .filter_by(from_currency=from_currency, to_currency=to_currency)
        .join(Exchange)
        .filter(Exchange.is_active == sa.true())
        .order_by(sa.desc(Exchange.weight))
        .first()
    )

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
        rate0_model = orm.aliased(Rate)
        rate1_model = orm.aliased(Rate)
        exchange0_model = orm.aliased(Exchange)
        exchange1_model = orm.aliased(Exchange)

        rate_obj = (
            Session.query(
                rate0_model,
                rate1_model,
                (exchange0_model.weight + exchange1_model.weight).label("w"),
            )
            .filter_by(from_currency=from_currency)
            .join(
                rate1_model,
                sa.and_(
                    rate1_model.from_currency_id == rate0_model.to_currency_id,
                    rate1_model.to_currency == to_currency,
                ),
            )
            .join(
                exchange0_model,
                sa.and_(
                    exchange0_model.id == rate0_model.exchange_id,
                    exchange0_model.is_active == sa.true(),
                ),
            )
            .join(
                exchange1_model,
                sa.and_(
                    exchange1_model.id == rate1_model.exchange_id,
                    exchange1_model.is_active == sa.true(),
                ),
            )
            .order_by(sa.desc("w"))
            .first()
        )

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
    for a in ["rate", "rate_open", "low24h", "high24h"]:
        value = getattr(prr, a)
        if value and value > BIGGEST_VALUE:
            raise OverflowException


def combine_values(
    value0: Decimal or None, value1: Decimal or None
) -> (Decimal or None):
    if value0 and value1:
        return value0 * value1
    else:
        return None
