from suite.conf import settings
from celery import Celery
from pyramid_sqlalchemy import init_sqlalchemy
from sqlalchemy import create_engine

celery_app = Celery()
celery_app.config_from_object(settings)

db_engine = create_engine(settings.DATABASE['url'])
init_sqlalchemy(db_engine)
