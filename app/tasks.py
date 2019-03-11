import logging

from sqlalchemy.orm.exc import NoResultFound

from suite.conf import settings
from .celery import celery_app
from .exchanges.base import reverse_pair_data
from .helpers import import_module, rate_from_pair_data
from .db import db_session
from .models import Exchange, Currency, Rate

logging = logging.getLogger(__name__)

# TODO: hard limits


@celery_app.task
def scheduled_updater():
    for exchange_class in settings.BOT_EXCHANGES:
        exchange = import_module(exchange_class)()

        try:
            exchange_obj = db_session.query(Exchange).filter_by(name=exchange.name).one()
            if not exchange_obj.is_active:
                logging.info(f'Exchange: {exchange.name} is not active, skip.')
                continue
        except NoResultFound:
            logging.warning(f'Exchange: {exchange.name} is not configured, skip.')
            continue

        exchange_updater.delay(exchange_class)


@celery_app.task
def exchange_updater(exchange_class):
    exchange = import_module(exchange_class)()
    try:
        exchange_obj = db_session.query(Exchange).filter_by(name=exchange.name).one()
        if not exchange_obj.is_active:
            logging.info(f'Exchange: {exchange.name} is not active, skip.')
            return
    except NoResultFound:
        logging.warning(f'Exchange: {exchange.name} is not configured, skip.')
        return

    # TODO: transactions
    for pair in exchange.list_pairs:
        try:
            db_session.query(Currency).filter_by(is_active=True, code=pair.from_currency).one()
            db_session.query(Currency).filter_by(is_active=True, code=pair.to_currency).one()
        except NoResultFound:
            logging.info(f'Pair: {pair} is not active or not supported, skip.')
            continue

        pair_data = exchange.get_pair_info(pair)
        reversed_pair_data = reverse_pair_data(pair_data)

        save_rate(pair_data, exchange_obj.id)
        save_rate(reversed_pair_data, exchange_obj.id)

    db_session.commit()


def save_rate(pair_data, exchange_id):
    rate_data = rate_from_pair_data(pair_data, exchange_id)

    # TODO:
    if not rate_data.rate_open and rate_data.last_trade_at.hour == 0 and rate_data.last_trade_at.minute < 5:
        rate_data.rate_open = rate_data.rate

    rate_obj = db_session.query(Rate).filter_by(
        from_currency=rate_data.from_currency, to_currency=rate_data.to_currency, exchange_id=exchange_id
    ).first()

    if rate_obj:
        rate_data.id = rate_obj.id
        db_session.merge(rate_data)
    else:
        db_session.add(rate_data)

    db_session.flush()
