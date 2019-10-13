import os

from celery.schedules import crontab

from kombu import Queue

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = {"url": os.environ.get("DB_URL", "postgresql://postgres:@db:5432/postgres")}

CACHE = {
    "host": os.environ.get("CACHE_HOST", "redis"),
    "db": os.environ.get("CACHE_DB", "1"),
}

BROKER_URL = os.environ.get("BROKER_URL", "redis://redis:6379/0")

CELERY_ONCE_URL = os.environ.get("CELERY_ONCE_URL", "redis://redis:6379/2")
CELERY_ONCE_DEFAULT_TIMEOUT = 1800

CELERY_IMPORTS = ("app.tasks", "app.tasks_notifications")

CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = "UTC"

CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["application/json"]

CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_IGNORE_RESULT = True

CELERYD_TASK_TIME_LIMIT = 600

CELERY_DEFAULT_QUEUE = "low"

CELERY_QUEUES = (
    Queue("low"),
    Queue("exchanges"),
    Queue("notifications"),
    Queue("send_notification"),
    Queue("update_chat_request"),
)

CELERYBEAT_SCHEDULE = {
    "exchange_updater_BitfinexExchange": {
        "task": "app.tasks.exchange_updater",
        "schedule": crontab(minute="*/15"),
        "args": ("app.exchanges.BitfinexExchange",),
        "options": {"time_limit": 900, "once": {"timeout": 900}},
    },
    "exchange_updater_BittrexExchange": {
        "task": "app.tasks.exchange_updater",
        "schedule": crontab(minute="*/1"),
        "args": ("app.exchanges.BittrexExchange",),
        "options": {"time_limit": 60, "once": {"timeout": 60}},
    },
    "exchange_updater_BitkubExchange": {
        "task": "app.tasks.exchange_updater",
        "schedule": crontab(minute="*/1"),
        "args": ("app.exchanges.BitkubExchange",),
        "options": {"time_limit": 60, "once": {"timeout": 60}},
    },
    "exchange_updater_OpenExchangeRatesExchange": {
        "task": "app.tasks.exchange_updater",
        "schedule": crontab(minute=1, hour="*/1"),
        "args": ("app.exchanges.OpenExchangeRatesExchange",),
        "options": {"time_limit": 60, "once": {"timeout": 60}},
    },
    "exchange_updater_FixerExchange": {
        "task": "app.tasks.exchange_updater",
        "schedule": crontab(minute=1, hour="*/1"),
        "args": ("app.exchanges.FixerExchange",),
        "options": {"time_limit": 60, "once": {"timeout": 60}},
    },
    "exchange_updater_SpTodayExchange": {
        "task": "app.tasks.exchange_updater",
        "schedule": crontab(minute=1, hour="*/1"),
        "args": ("app.exchanges.SpTodayExchange",),
        "options": {"time_limit": 60, "once": {"timeout": 60}},
    },
    "delete_expired_rates": {
        "task": "app.tasks.delete_expired_rates",
        "schedule": crontab(minute=5, hour="*/1"),
    },
    "notification_checker": {
        "task": "app.tasks_notifications.notification_checker",
        "schedule": crontab(minute="*/5"),
    },
}

BOT_TOKEN = os.environ.get("BOT_TOKEN")
DEVELOPER_BOT_TOKEN = os.environ.get("DEVELOPER_BOT_TOKEN")
DEVELOPER_USER_ID = os.environ.get("DEVELOPER_USER_ID")

# by order
BOT_PARSERS = [
    "app.parsers.RegexParser",
    "app.parsers.LastRequestParser",
    "app.parsers.ExtendRegexParser",
]

OPENEXCHANGERATES_TOKEN = os.environ.get("OPENEXCHANGERATES_TOKEN")
FIXER_TOKEN = os.environ.get("FIXER_TOKEN")

SENTRY_URL = os.environ.get("SENTRY_URL")

LANGUAGES = (
    # 'ar',  # is not correct translations
    "ca",
    "de",
    "en",
    "es",
    "es_AR",
    "fr",
    "id",
    "it",
    "kk",
    "ms",
    "nl",
    "pl",
    "pt",
    "pt_BR",
    "ru",
    "tr",
    "uk",
    "uz",
    "zh_Hans",
    # 'zh_Hant',
    "zh_Hans_SG",
)

LANGUAGE_CODE = "en"

LANGUAGES_NAME = {
    # 'العربية': 'ar',  # Saudi Arabia
    "Català": "ca",
    "Deutsch": "de",
    "English": "en",
    "Español": "es",
    "Español (AR)": "es-ar",
    "Français": "fr",
    "Bahasa Indonesia": "id",
    "Italiano": "it",
    "Қазақ тілі": "kk",
    "Bahasa Melayu": "ms",  # Malay
    "Nederlands": "nl",
    "Polski": "pl",
    "Português": "pt",
    "Português (BR)": "pt-br",
    "Русский": "ru",
    "Türkçe": "tr",
    "Український": "uk",
    "Ўзбекча": "uz",
    "中文": "zh-hans",  # Simplified Chinese
    "中文 (SG)": "zh-hans-sg",  # Simplified Chinese Singapore
}

DEFAULT_CURRENCY = "USD"
# _0_XXX XXX_1_
DEFAULT_CURRENCY_POSITION = 1

MAX_LEN_MSG_REQUESTS_LOG = 100

LOGGING = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)-5.5s [%(name)s:%(lineno)s][%(threadName)s] %(message)s"
        }
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "default"}},
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {"sqlalchemy.engine": {"level": "WARNING", "handlers": ["console"]}},
}
