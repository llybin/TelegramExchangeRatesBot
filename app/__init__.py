import gettext
from decimal import getcontext
from logging.config import dictConfig

from suite.conf import settings
from .constants import decimal_precision

dictConfig(settings.LOGGING)

getcontext().prec = decimal_precision

translations = dict()
for l in settings.LANGUAGES:
    translations[l] = gettext.translation(
        'messages',
        localedir='locale',
        languages=[l]
    )


_ = gettext.gettext


def sentry_before_send(event, hint):
    """Filtering"""
    for x in event['breadcrumbs']:
        if x['category'] == 'httplib':
            x['data']['url'] = x['data']['url'].replace(settings.BOT_TOKEN, '<BOT_TOKEN>')
            x['data']['url'] = x['data']['url'].replace(settings.DEVELOPER_BOT_TOKEN, '<DEVELOPER_BOT_TOKEN>')

    return event
