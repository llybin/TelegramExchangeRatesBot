from logging.config import dictConfig

from suite.conf import settings

dictConfig(settings.LOGGING)
