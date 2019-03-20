import gettext
from decimal import getcontext
from logging.config import dictConfig

from suite.conf import settings
from .constants import decimal_precision

dictConfig(settings.LOGGING)

getcontext().prec = decimal_precision

translations = dict()
for l in settings.LANGUAGES:
    # pt-br, en
    key = l.lower().replace('_', '-')
    translations[key] = gettext.translation(
        'messages',
        localedir='locale',
        languages=[l]
    )


_ = gettext.gettext
