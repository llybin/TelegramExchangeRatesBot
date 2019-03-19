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

CELERY_DEFAULT_QUEUE = 'default'

CELERY_QUEUES = (
    Queue('default'),
    Queue('exchanges'),
    Queue('log'),
)

CELERYBEAT_SCHEDULE = {
    'exchange_updater_BitfinexExchange': {
        'task': 'app.tasks.exchange_updater',
        'schedule': crontab(minute='*/15'),
        'args': ('app.exchanges.BitfinexExchange',),
        'options': {'time_limit': 900}
    },
    'exchange_updater_BittrexExchange': {
        'task': 'app.tasks.exchange_updater',
        'schedule': crontab(minute='*/1'),
        'args': ('app.exchanges.BittrexExchange',),
        'options': {'time_limit': 60}
    },
    'exchange_updater_OpenExchangeRatesExchange': {
        'task': 'app.tasks.exchange_updater',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': ('app.exchanges.OpenExchangeRatesExchange',),
        'options': {'time_limit': 60}
    },
    'delete_expired_rates': {
        'task': 'app.tasks.delete_expired_rates',
        'schedule': crontab(minute=5, hour='*/1'),
    },
}

BOT_TOKEN = os.environ.get('BOT_TOKEN')
DEVELOPER_BOT_TOKEN = os.environ.get('DEVELOPER_BOT_TOKEN')
DEVELOPER_USER_ID = os.environ.get('DEVELOPER_USER_ID')

BOT_PARSERS = [
    'app.parsers.RegexParser',
]

OPENEXCHANGERATES_TOKEN = os.environ.get('OPENEXCHANGERATES_TOKEN')

SENTRY_URL = os.environ.get('SENTRY_URL')

LANGUAGES = (
    'ru',
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
