from decimal import Decimal

from sqlalchemy.orm.exc import NoResultFound

from ..db import db_session
from ..models import Currency, Rate
from ..parsers.base import PriceRequest


# TODO: in work
def convert(price_request: PriceRequest) -> str:
    from_currency = db_session.query(Currency).filter_by(is_active=True, code=price_request.currency).one()
    to_currency = db_session.query(Currency).filter_by(is_active=True, code=price_request.to_currency).one()

    rates = db_session.query(Rate).filter_by(from_currency=from_currency, to_currency=to_currency).all()

    amount = price_request.amount or Decimal('1')
    res = amount * rates[0].rate

    return f'{amount} {price_request.currency} = {res} {price_request.to_currency}'
