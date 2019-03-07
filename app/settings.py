import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = {
    'url': os.environ.get('DB_URL', 'postgresql://postgres:@db:5432/postgres'),
}

CACHE = {
    'host': os.environ.get('CACHE_HOST', 'redis'),
    'db': os.environ.get('CACHE_DB', '0'),
}

BOT_TOKEN = os.environ.get('BOT_TOKEN')

BOT_PARSERS = [
    'app.parsers.simple_parser.SimpleParser',
]

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
