import logging
from decimal import Decimal

import telegram
import transaction
from pyramid_sqlalchemy import Session
from sqlalchemy import true, false
from telegram import ParseMode
from suite.conf import settings

from app.celery import celery_app
from app.converter.converter import convert
from app.converter.formatter import NotifyFormatPriceRequestResult
from app.models import Notification, Currency
from app.parsers.base import PriceRequest


def is_triggered(trigger_clause: str, trigger_value: Decimal, last_rate: Decimal, current_rate: Decimal):
    # TODO: take from enum model values for compare
    if trigger_clause == 'more':
        return current_rate >= last_rate

    elif trigger_clause == 'less':
        return current_rate <= last_rate

    elif trigger_clause == 'diff':
        return abs(last_rate - current_rate) >= trigger_value

    elif trigger_clause == 'percent':
        return abs(last_rate - current_rate) / last_rate * Decimal('100') >= trigger_value

    else:
        raise NotImplemented


def notification_auto_disable(pair: list):
    db_session = Session()

    notifications = db_session.query(
        Notification
    ).filter_by(
        is_active=true(),
        from_currency_id=pair[0],
        to_currency_id=pair[1]
    ).all()

    for n in notifications:
        send_notification(n.chat_id, 'your notification was disabled')

    db_session.query(
        Notification
    ).filter_by(
        is_active=true(),
        from_currency_id=pair[0],
        to_currency_id=pair[1]
    ).update({'is_active': false()})

    transaction.commit()


# TODO: rate limit, repeat on fail
@celery_app.task(queue='send_notification', time_limit=60)
def send_notification(chat_id, text):
    bot = telegram.Bot(settings.BOT_TOKEN)

    bot.send_message(
        chat_id=chat_id,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
        text=text)
    # TODO: except Exception Forbidden - unsubscribe, disable notification
    # TODO: /stop - disable notifications


@celery_app.task(queue='notifications', time_limit=60)
def notification_checker():
    db_session = Session()
    pairs = db_session.query(
        Notification.from_currency_id,
        Notification.to_currency_id,
    ).filter_by(
        is_active=true()
    ).group_by(
        Notification.from_currency_id,
        Notification.to_currency_id
    ).all()

    for pair in pairs:
        from_currency = db_session.query(Currency).get(pair[0])
        to_currency = db_session.query(Currency).get(pair[1])

        if not from_currency.is_active or not to_currency.is_active:
            logging.info('Disable notifications because currency %s %s is not active anymore',
                         from_currency.code, to_currency.code)
            notification_auto_disable(pair)
            continue

        pr = PriceRequest(
            amount=None,
            currency=from_currency.code,
            to_currency=to_currency.code,
            parser_name='notifications'
        )

        prr = convert(pr)

        notifications = db_session.query(
            Notification
        ).filter_by(
            is_active=true()
        ).filter_by(
            from_currency_id=pair[0],
            to_currency_id=pair[1]
        ).all()

        for n in notifications:
            if is_triggered(n.trigger_clause, n.trigger_value, n.last_rate, prr.rate):
                n.last_rate = prr.rate
                # transaction.commit()

                text_to = NotifyFormatPriceRequestResult(prr, n.chat.locale).get()
                send_notification(n.chat_id, text_to)

        transaction.commit()
