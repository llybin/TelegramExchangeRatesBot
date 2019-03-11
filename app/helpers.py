import importlib
from typing import Type

from sqlalchemy.orm.exc import NoResultFound

from .db import db_session
from .exchanges.base import PairData
from .exceptions import CurrencyNotSupportedException
from .models import Rate, Currency


def import_module(name: str) -> Type:
    components = name.rsplit('.', 1)
    return getattr(importlib.import_module(components[0]), components[1])


def rate_from_pair_data(pair_data: PairData, exchange_id: int) -> Rate:
    try:
        from_currency = db_session.query(Currency).filter_by(is_active=True, code=pair_data.pair.from_currency).one()
        to_currency = db_session.query(Currency).filter_by(is_active=True, code=pair_data.pair.to_currency).one()
    except NoResultFound:
        raise CurrencyNotSupportedException(pair_data.pair)

    return Rate(
        exchange_id=exchange_id,
        from_currency=from_currency,
        to_currency=to_currency,
        rate=pair_data.rate,
        rate_open=pair_data.rate_open,
        low24h=pair_data.low24h,
        high24h=pair_data.high24h,
        last_trade_at=pair_data.last_trade_at,
    )
