import logging

from sqlalchemy.orm.exc import NoResultFound

from .celery import celery_app
from .exchanges.base import reverse_pair_data, PairData
from .helpers import import_module, rate_from_pair_data, fill_rate_open
from .db import db_session
from .models import Exchange, Currency, Rate

logging = logging.getLogger(__name__)

# TODO: hard limits


@celery_app.task
def exchange_updater(exchange_class: str) -> None:
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
            logging.info(f'Exchange: {exchange.name}, pair: {pair} is not active or not supported, skip.')
            continue

        pair_data = exchange.get_pair_info(pair)
        reversed_pair_data = reverse_pair_data(pair_data)

        save_rate(pair_data, exchange_obj.id)
        save_rate(reversed_pair_data, exchange_obj.id)

    db_session.commit()


def save_rate(pair_data: PairData, exchange_id: int) -> None:
    new_rate = rate_from_pair_data(pair_data, exchange_id)

    current_rate = db_session.query(Rate).filter_by(
        from_currency=new_rate.from_currency, to_currency=new_rate.to_currency, exchange_id=exchange_id
    ).first()

    new_rate = fill_rate_open(new_rate, current_rate)

    if current_rate:
        new_rate.id = current_rate.id
        db_session.merge(new_rate)
    else:
        db_session.add(new_rate)

    db_session.flush()
