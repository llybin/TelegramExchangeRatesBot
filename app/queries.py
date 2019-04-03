from suite.database import Session

from app.cache import region
from app.models import Currency, ChatRequests


@region.cache_on_arguments(expiration_time=300)
def get_all_currency_codes():
    codes = Session.query(Currency.code).filter_by(is_active=True).order_by(Currency.code)
    return [x[0] for x in codes]


@region.cache_on_arguments(expiration_time=300)
def get_all_currencies():
    return Session.query(Currency.code, Currency.name).filter_by(is_active=True).order_by(Currency.name).all()


@region.cache_on_arguments(expiration_time=1)
def get_last_request(chat_id):
    return Session.query(ChatRequests).filter_by(
        chat_id=chat_id
    ).order_by(
        ChatRequests.times.desc()
    ).limit(9).all()
