from dogpile.cache import make_region

from suite.conf import settings

region = make_region().configure(
    "dogpile.cache.redis",
    expiration_time=3600,
    arguments={"host": settings.CACHE["host"], "db": settings.CACHE["db"]},
)
