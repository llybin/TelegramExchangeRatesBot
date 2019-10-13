import logging

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from suite.conf import settings


def before_send(event, hint):
    """Filtering"""
    for x in event["breadcrumbs"]:
        if x["category"] == "httplib":
            x["data"]["url"] = x["data"]["url"].replace(
                settings.BOT_TOKEN, "<BOT_TOKEN>"
            )
            x["data"]["url"] = x["data"]["url"].replace(
                settings.DEVELOPER_BOT_TOKEN, "<DEVELOPER_BOT_TOKEN>"
            )

    return event


def init_sentry():
    if settings.SENTRY_URL:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.WARNING,  # Send errors as events
        )

        sentry_sdk.init(
            dsn=settings.SENTRY_URL,
            before_send=before_send,
            integrations=[CeleryIntegration(), sentry_logging],
        )
