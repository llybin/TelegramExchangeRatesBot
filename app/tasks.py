import logging

from .celery import celery_app
from .exchanges.base import reverse_pair_date
from .exchanges.bitfinex import BitfinexExchange
from .exchanges.bittrex import BittrexExchange
# from .exchanges.openexchangerates import OpenExchangeRatesExchange
from .db import db_session
from .models import Rate, Exchange, Currency


logging = logging.getLogger(__name__)


@celery_app.task
def example():
    logging.warning('Test message.')


def rate_updater():
    for exchange_class in [BittrexExchange, BitfinexExchange]:
        if db_session.query(Exchange).filter_by(is_active=False, id=exchange_class.db_id).exists():
            logging.info(f'Exchange: {exchange_class.db_id} is not active, skip.')
            continue

        exchange = exchange_class()

        for pair in exchange.list_pairs:
            # db_session.query(Currency)
            # pair.from_currency pair.to_currency
            # logging.info(f'Currency: {currency} is not supported by app, skip.')

            pair_data = exchange.get_pair_info(pair)
            reversed_pair_data = reverse_pair_date(pair_data)
            # TODO:
            # update or create two pair
            # Rate equal model PairData
            # db_session.query(Rate)
