import importlib
import logging

from sqlalchemy.orm.exc import NoResultFound

from suite.conf import settings
from .celery import celery_app
from .exchanges.base import reverse_pair_data
from .helpers import import_module, rate_from_pair_data
from .db import db_session
from .models import Exchange, Currency


logging = logging.getLogger(__name__)


@celery_app.task
def scheduled_updater():
    for exchange_class in settings['BOT_EXCHANGES']:
        try:
            exchange_obj = db_session.query(Exchange).filter_by(name=exchange_class.name).one()
            if not exchange_obj.is_active:
                logging.info(f'Exchange: {exchange_class.name} is not active, skip.')
                continue
        except NoResultFound:
            logging.warning(f'Exchange: {exchange_class.name} is not configured, skip.')
            continue

        exchange_updater.delay(exchange_class, exchange_obj.id)


@celery_app.task
def exchange_updater(exchange_class):
        try:
            exchange_obj = db_session.query(Exchange).filter_by(name=exchange_class.name).one()
            if not exchange_obj.is_active:
                logging.info(f'Exchange: {exchange_class.name} is not active, skip.')
                return
        except NoResultFound:
            logging.warning(f'Exchange: {exchange_class.name} is not configured, skip.')
            return

        exchange = import_module(exchange_class)()

        for pair in exchange.list_pairs:
            try:
                db_session.query(Currency).filter_by(is_active=True, code=pair.from_currency).one()
                db_session.query(Currency).filter_by(is_active=True, code=pair.to_currency).one()
            except NoResultFound:
                logging.info(f'Pair: {pair} is not active or nor supported, skip.')
                continue

            pair_data = exchange.get_pair_info(pair)
            reversed_pair_data = reverse_pair_data(pair_data)

            rate_data = rate_from_pair_data(pair_data, exchange_obj.id)
            reversed_rate_data = rate_from_pair_data(reversed_pair_data, exchange_obj.id)

            # TODO: if not rate_open: fill

            db_session.merge(rate_data)
            db_session.merge(reversed_rate_data)
            db_session.flush()

        db_session.commit()
