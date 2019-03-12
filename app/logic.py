from functools import lru_cache

from pyramid_sqlalchemy import Session

from .models import Currency


@lru_cache(maxsize=None)
def get_all_currencies():
    return [x[0] for x in Session().query(Currency.code).filter_by(is_active=True)]
