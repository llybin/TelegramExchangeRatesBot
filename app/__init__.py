# import gettext
from decimal import getcontext
from logging.config import dictConfig

from suite.conf import settings

dictConfig(settings.LOGGING)

getcontext().prec = 24

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
