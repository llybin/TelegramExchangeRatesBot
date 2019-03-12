from pyramid_sqlalchemy import Session

from .cache import region
from .models import Currency


@region.cache_on_arguments(expiration_time=300)
def get_all_currencies():
    return [x[0] for x in Session().query(Currency.code).filter_by(is_active=True)]
