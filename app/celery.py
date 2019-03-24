import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from suite.conf import settings
from celery import Celery
from pyramid_sqlalchemy import init_sqlalchemy
from sqlalchemy import create_engine

from . import sentry_before_send

if settings.SENTRY_URL:
    sentry_sdk.init(
        dsn=settings.SENTRY_URL,
        before_send=sentry_before_send,
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
