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

CELERY_IMPORTS = (
    "app.tasks",
)

CELERY_TIMEZONE = 'UTC'
CELERY_REDIRECT_STDOUTS = False

CELERY_ALWAYS_EAGER = False

CELERY_IGNORE_RESULT = True
CELERY_SEND_TASK_ERROR_EMAILS = False
CELERY_TASK_RESULT_EXPIRES = 600

CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ['application/json']

CELERY_DEFAULT_QUEUE = 'default'

CELERY_QUEUES = (
    Queue('default'),
)

# CELERY_QUEUES = (
#     Queue('default', Exchange('default'), routing_key='default'),
#     Queue('rate_update', Exchange('rate_update'), routing_key='rate_update'),
#     Queue('low', Exchange('low'), routing_key='low'),
# )
# CELERY_DEFAULT_QUEUE = 'default'
# CELERY_DEFAULT_EXCHANGE_TYPE = 'default'
# CELERY_DEFAULT_ROUTING_KEY = 'default'
#
# CELERY_ROUTES = {
#     'telegrambotexchangerates.rate_updater.bitfinex': {'queue': 'rate_update'},
#     'telegrambotexchangerates.rate_updater.main_currency': {'queue': 'rate_update'},
#     'telegrambotexchangerates.rate_updater.sp_today': {'queue': 'rate_update'},
#     'telegrambotexchangerates.rate_updater.yahoo': {'queue': 'rate_update'},
#     'telegrambotexchangerates.rate_updater.cryptonator': {'queue': 'rate_update'},
#     'telegrambotexchangerates.rate_updater.openexchangerates': {'queue': 'rate_update'},
#
#     'telegrambotexchangerates.tasks.check': {'queue': 'rate_update'},
#
#     'telegrambotexchangerates.tasks.send_notification': {'queue': 'low'},
#     'telegrambotexchangerates.tasks.send_feedback': {'queue': 'low'},
#     'telegrambotexchangerates.tasks.send_track': {'queue': 'low'},
#     'telegrambotexchangerates.tasks.to_log': {'queue': 'low'},
#     'telegrambotexchangerates.tasks.update_chat_info': {'queue': 'low'},
# }

CELERYBEAT_SCHEDULE = {
    'exchange_updater_BitfinexExchange': {
        'task': 'app.tasks.exchange_updater',
        'schedule': crontab(minute='*/10'),
        'args': ('app.exchanges.BitfinexExchange',)
    },
    'exchange_updater_BittrexExchange': {
        'task': 'app.tasks.exchange_updater',
        'schedule': crontab(minute='*/1'),
        'args': ('app.exchanges.BittrexExchange',)
    },
    'exchange_updater_OpenExchangeRatesExchange': {
        'task': 'app.tasks.exchange_updater',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': ('app.exchanges.OpenExchangeRatesExchange',)
    },
}

BOT_TOKEN = os.environ.get('BOT_TOKEN')

BOT_PARSERS = [
    'app.parsers.SimpleParser',
]

OPENEXCHANGERATES_TOKEN = os.environ.get('OPENEXCHANGERATES_TOKEN')

LANGUAGES = (
    'en_US',
)

LANGUAGE_CODE = 'en_US'

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
    }
}
