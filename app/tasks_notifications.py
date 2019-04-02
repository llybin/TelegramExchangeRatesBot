import logging
from decimal import Decimal

import telegram
import transaction
from sqlalchemy import true, false
from telegram import ParseMode
from telegram.error import RetryAfter, TimedOut, Unauthorized
from suite.database import Session
from suite.conf import settings

from app.celery import celery_app
from app.converter.converter import convert, PriceRequestResult
from app.formatter.formatter import NotifyFormatPriceRequestResult
from app.models import Notification, Currency, NotifyTriggerClauseEnum, Chat
from app.parsers.base import PriceRequest
from app.translations import get_translations


def is_triggered(trigger_clause: NotifyTriggerClauseEnum, trigger_value: Decimal,
                 last_notification_rate: Decimal, current_rate: Decimal) -> bool:
    """
    :param trigger_clause: clause of notification
    :param trigger_value: diff or percent depends on trigger_clause
    :param last_notification_rate: rate when was created or last triggered notification
    :param current_rate: rate now
    :return:
    """

    if trigger_clause == NotifyTriggerClauseEnum.more:
        return current_rate >= last_notification_rate

    elif trigger_clause == NotifyTriggerClauseEnum.less:
        return current_rate <= last_notification_rate

    elif trigger_clause == NotifyTriggerClauseEnum.diff:
        return abs(last_notification_rate - current_rate) >= trigger_value

    elif trigger_clause == NotifyTriggerClauseEnum.percent:
        return abs(last_notification_rate - current_rate) / last_notification_rate * Decimal('100') >= trigger_value

    else:
        raise ValueError('Unknown NotifyTriggerClauseEnum')


def notification_auto_disable(pair: list) -> None:
    db_session = Session()

    notifications = db_session.query(
        Notification
    ).filter_by(
        is_active=true(),
        from_currency_id=pair[0],
        to_currency_id=pair[1]
    ).all()

    for n in notifications:
        _ = get_translations(n.chat.locale)
        send_notification.delay(
            n.chat_id,
            _('Your notification has been disabled, due to one of the currencies'
              ' %(from_currency)s %(to_currency)s has been deactivated.') % {
                'from_currency': n.from_currency.code, 'to_currency': n.to_currency.code
            })

    db_session.query(
        Notification
    ).filter_by(
        is_active=true(),
        from_currency_id=pair[0],
        to_currency_id=pair[1]
    ).update({'is_active': false()})

    transaction.commit()


@celery_app.task(bind=True, queue='send_notification', time_limit=60, rate_limit='15/s',
                 retry_backoff=5, retry_backoff_max=300)
def send_notification(self, chat_id: int, text: str) -> None:
    """
    https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bot-39s-subscribers-at-once
    The API will not allow more than ~30 messages to different users per second
    """
    bot = telegram.Bot(settings.BOT_TOKEN)

    try:
        bot.send_message(
            chat_id=chat_id,
            disable_web_page_preview=True,
            parse_mode=ParseMode.MARKDOWN,
            text=text)

    except TimedOut as e:
        raise self.retry(exc=e)

    except RetryAfter as e:
        raise self.retry(exc=e, countdown=int(e.retry_after))

    except Unauthorized:
        # bot deleted
        db_session = Session()

        db_session.query(
            Notification
        ).filter_by(
            is_active=true(),
            chat_id=chat_id,
        ).update({'is_active': false()})

        db_session.query(Chat).filter_by(
            id=chat_id
        ).update({'is_subscribed': false()})

        transaction.commit()


# base=QueueOnce
@celery_app.task(queue='notifications', time_limit=300)
def notification_checker() -> None:
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
            parser_name='Notification'
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
                # replace rate_open from daily to rate when was created or last triggered notification
                # TODO: PriceRequestResult -> dataclass, inside diff and etc
                nprr = PriceRequestResult(
                    price_request=prr.price_request,
                    exchanges=prr.exchanges,
                    rate=prr.rate,
                    rate_open=n.last_rate,
                    last_trade_at=prr.last_trade_at,
                    low24h=prr.low24h,
                    high24h=prr.high24h
                )

                text_to = NotifyFormatPriceRequestResult(nprr, n.chat.locale).get()

                if n.trigger_clause in [NotifyTriggerClauseEnum.less, NotifyTriggerClauseEnum.more]:
                    n.is_active = False
                    _ = get_translations(n.chat.locale)
                    text_to += '\n'
                    text_to += _('_One-time reminder. Set up a new reminder._')

                send_notification.delay(n.chat_id, text_to)

                n.last_rate = prr.rate

                transaction.commit()
