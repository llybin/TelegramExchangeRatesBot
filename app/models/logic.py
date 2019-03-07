from functools import lru_cache

from .db import db_session
from .models import Currency


@lru_cache(maxsize=None)
def get_all_currencies():
    return [x[0] for x in db_session.query(Currency.code).filter_by(is_active=True)]
