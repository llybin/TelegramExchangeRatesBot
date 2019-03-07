from dogpile.cache import make_region

from suite.conf import settings


region = make_region().configure(
    'dogpile.cache.redis',
    arguments={
        'host': settings.CACHE['host'],
        'db': settings.CACHE['db'],
    }
)
