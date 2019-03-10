# import gettext
from decimal import getcontext
from logging.config import dictConfig

from suite.conf import settings
from .constants import decimal_precision

dictConfig(settings.LOGGING)

getcontext().prec = decimal_precision

# translations = dict()
# for l in settings.LANGUAGES:
#     translations[l] = gettext.translation(
#         'messages',
#         localedir='locale',
#         languages=[l]
#     )
#
#
# def _(msg, language=settings.LANGUAGE_CODE):
#     return translations[language].gettext(msg)
