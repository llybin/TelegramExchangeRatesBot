import logging

import transaction
from pyramid_sqlalchemy import Session
from sqlalchemy.orm.exc import NoResultFound

from .celery import celery_app
from .exchanges.base import reverse_pair_data, PairData
from .helpers import import_module, rate_from_pair_data, fill_rate_open
from .models import Exchange, Currency, Rate

logging = logging.getLogger(__name__)


@celery_app.task(queue='exchanges')
def exchange_updater(exchange_class: str) -> None:
    db_session = Session()

    exchange = import_module(exchange_class)()
    try:
        exchange_obj = db_session.query(Exchange).filter_by(name=exchange.name).one()
        if not exchange_obj.is_active:
            logging.info(f'Exchange: {exchange.name} is not active, skip.')
            return
    except NoResultFound:
        logging.warning(f'Exchange: {exchange.name} is not configured, skip.')
        return

    for pair in exchange.list_pairs:
        from_currency = db_session.query(Currency).filter_by(is_active=True, code=pair.from_currency).scalar()
        to_currency = db_session.query(Currency).filter_by(is_active=True, code=pair.to_currency).scalar()

        if not from_currency or not to_currency:
            logging.info(f'Exchange: {exchange.name}, pair: {pair} is not active or not supported, skip.')
            continue

        pair_data = exchange.get_pair_info(pair)
        reversed_pair_data = reverse_pair_data(pair_data)

        def save_rate(the_pair_data):
            new_rate = rate_from_pair_data(the_pair_data, exchange_obj.id)

            current_rate = db_session.query(Rate).filter_by(
                from_currency=new_rate.from_currency, to_currency=new_rate.to_currency, exchange_id=exchange_obj.id
            ).first()

            new_rate = fill_rate_open(new_rate, current_rate)

            if current_rate:
                new_rate.id = current_rate.id
                db_session.merge(new_rate)
            else:
                db_session.add(new_rate)

        save_rate(pair_data)
        save_rate(reversed_pair_data)

    transaction.commit()
