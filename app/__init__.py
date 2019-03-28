from decimal import getcontext
from logging.config import dictConfig

from suite.conf import settings
from .constants import decimal_precision

dictConfig(settings.LOGGING)

getcontext().prec = decimal_precision
