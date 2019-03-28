import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from suite.conf import settings
from celery import Celery
from sqlalchemy import create_engine
from suite.database import init_sqlalchemy

from app.sentry import before_send
from app.translations import init_translations

if settings.SENTRY_URL:
    sentry_sdk.init(
        dsn=settings.SENTRY_URL,
        before_send=before_send,
        integrations=[CeleryIntegration()]
    )

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
