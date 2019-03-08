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
CELERY_DEFAULT_QUEUE = 'default'

CELERY_ALWAYS_EAGER = False

CELERY_IGNORE_RESULT = True
CELERY_SEND_TASK_ERROR_EMAILS = False
CELERY_TASK_RESULT_EXPIRES = 600

CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ['application/json']

CELERY_QUEUES = (
    Queue('default'),
)

CELERYBEAT_SCHEDULE = {
    'example': {
        'task': 'app.tasks.example',
        'schedule': crontab(minute='*/1'),
    },
}

BOT_TOKEN = os.environ.get('BOT_TOKEN')

BOT_PARSERS = [
    'app.parsers.simple_parser.SimpleParser',
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
