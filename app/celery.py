from suite.conf import settings
from celery import Celery
from sqlalchemy import create_engine
from suite.database import init_sqlalchemy

from app.sentry import init_sentry
from app.translations import init_translations

init_sentry()

celery_app = Celery()
celery_app.config_from_object(settings)
celery_app.conf.ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': {
        'url': settings.CELERY_ONCE_URL,
        'default_timeout': settings.CELERY_ONCE_DEFAULT_TIMEOUT
    }
}

db_engine = create_engine(settings.DATABASE['url'])
init_sqlalchemy(db_engine)

init_translations()
