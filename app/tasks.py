import logging

from .celery import celery_app


logging = logging.getLogger(__name__)


@celery_app.task
def example():
    logging.warning('Test message.')
