import transaction
from sqlalchemy.sql import false, true
from suite.database import Session
from telegram.ext import ConversationHandler

from app.decorators import register_update, chat_language
from app.models import Chat, Notification


@register_update
@chat_language
def stop_command(bot, update, chat_info, _):
    if chat_info['is_subscribed']:
        Session().query(Chat).filter_by(
            id=update.message.chat_id
        ).update({'is_subscribed': false()})
        transaction.commit()

    bot.send_message(
        chat_id=update.message.chat_id,
        text=_("You're unsubscribed. You always can subscribe again 👉 /start")
    )

    Session().query(
        Notification
    ).filter_by(
        is_active=true(),
        chat_id=update.message.chat_id,
    ).update({'is_active': false()})

    transaction.commit()

    return ConversationHandler.END
