import os
from celery.schedules import crontab
from kombu import Queue

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = {
    'url': os.environ.get('DB_URL', 'postgresql://postgres:@db:5432/postgres'),
}

CACHE = {
    'host': os.environ.get('CACHE_HOST', 'redis'),
    'db': os.environ.get('CACHE_DB', '1'),
}

BROKER_URL = os.environ.get('BROKER_URL', 'redis://redis:6379/0')

CELERY_ONCE_URL = os.environ.get('CELERY_ONCE_URL', 'redis://redis:6379/2')
CELERY_ONCE_DEFAULT_TIMEOUT = 1800

CELERY_IMPORTS = (
    'app.tasks',
)

CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'UTC'

CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['application/json']

CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_IGNORE_RESULT = True

CELERYD_TASK_TIME_LIMIT = 600

CELERY_DEFAULT_QUEUE = 'low'

CELERY_QUEUES = (
    Queue('low'),
    Queue('exchanges'),
    Queue('update_chat_request'),
)

CELERYBEAT_SCHEDULE = {
    'exchange_updater_BitfinexExchange': {
        'task': 'app.tasks.exchange_updater',
        'schedule': crontab(minute='*/15'),
        'args': ('app.exchanges.BitfinexExchange',),
        'options': {'time_limit': 890, 'once': {'timeout': 900}}
    },
    'exchange_updater_BittrexExchange': {
        'task': 'app.tasks.exchange_updater',
        'schedule': crontab(minute='*/1'),
        'args': ('app.exchanges.BittrexExchange',),
        'options': {'time_limit': 50, 'once': {'timeout': 55}}
    },
    'exchange_updater_OpenExchangeRatesExchange': {
        'task': 'app.tasks.exchange_updater',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': ('app.exchanges.OpenExchangeRatesExchange',),
        'options': {'time_limit': 50, 'once': {'timeout': 55}}
    },
    'delete_expired_rates': {
        'task': 'app.tasks.delete_expired_rates',
        'schedule': crontab(minute=5, hour='*/1'),
        'options': {'time_limit': 50, 'once': {'timeout': 55}}
    },
}

BOT_TOKEN = os.environ.get('BOT_TOKEN')
DEVELOPER_BOT_TOKEN = os.environ.get('DEVELOPER_BOT_TOKEN')
DEVELOPER_USER_ID = os.environ.get('DEVELOPER_USER_ID')

# by order
BOT_PARSERS = [
    'app.parsers.RegexParser',
    'app.parsers.LastRequestParser',
    'app.parsers.ExtendRegexParser',
]

OPENEXCHANGERATES_TOKEN = os.environ.get('OPENEXCHANGERATES_TOKEN')

SENTRY_URL = os.environ.get('SENTRY_URL')

LANGUAGES = (
    'de',
    'en',
    'es',
    'it',
    'kk',
    'ms',
    'pl',
    'pt',
    'pt_BR',
    'ru',
    'uk',
    'zh_CN',
    'zh_SG',
)

LANGUAGE_CODE = 'en'

DEFAULT_CURRENCY = 'USD'
# _0_XXX XXX_1_
DEFAULT_CURRENCY_POSITION = 1

MAX_LEN_MSG_REQUESTS_LOG = 100

LOGGING = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)-5.5s [%(name)s:%(lineno)s][%(threadName)s] %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    },
    'loggers': {
        'sqlalchemy.engine': {
            'level': 'WARNING',
            'handlers': ['console']
        },
    }
}
