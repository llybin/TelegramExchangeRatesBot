import importlib
import logging
from typing import Type

from pyramid_sqlalchemy import Session
from sqlalchemy.orm.exc import NoResultFound

from .exchanges.base import PairData
from .exceptions import CurrencyNotSupportedException
from .models import Rate, Currency


def import_module(name: str) -> Type:
    components = name.rsplit('.', 1)
    return getattr(importlib.import_module(components[0]), components[1])


def rate_from_pair_data(pair_data: PairData, exchange_id: int) -> Rate:
    db_session = Session()
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


def fill_rate_open(new_rate: Rate, current_rate: Rate or None) -> Rate:
    if new_rate.rate_open:
        logging.debug('rate_open provided by exchange: %d, pair: %d-%d',
                      new_rate.exchange_id, new_rate.from_currency.id, new_rate.to_currency.id)
        return new_rate

    if not current_rate:
        if new_rate.last_trade_at.hour == 0:
            new_rate.rate_open = new_rate.rate
            logging.info('Set new rate_open for exchange: %d, pair: %d-%d',
                         new_rate.exchange_id, new_rate.from_currency.id, new_rate.to_currency.id)
    else:
        if new_rate.last_trade_at.date() == current_rate.last_trade_at.date():
            new_rate.rate_open = current_rate.rate_open
            logging.debug('Set existed rate_open for exchange: %d, pair: %d-%d',
                          new_rate.exchange_id, new_rate.from_currency.id, new_rate.to_currency.id)
        elif new_rate.last_trade_at.hour == 0:
            new_rate.rate_open = new_rate.rate
            logging.info('Set new rate_open for exchange: %d, pair: %d-%d',
                         new_rate.exchange_id, new_rate.from_currency.id, new_rate.to_currency.id)
        else:
            logging.info('Reset rate_open for exchange: %d, pair: %d-%d',
                         new_rate.exchange_id, new_rate.from_currency.id, new_rate.to_currency.id)

    return new_rate


def convert_locale(locale: str) -> str:
    # income en, en-us
    if len(locale) == 2:
        return locale

    parts = locale.split('-')
    if len(parts) == 2 and len(parts[0]) == 2 and len(parts[1]) == 2:
        return f'{parts[0]}_{parts[1].upper()}'

    else:
        logging.error('Error converting locale: %s', locale)
        return locale[:2]
