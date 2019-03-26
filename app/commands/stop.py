import transaction
from pyramid_sqlalchemy import Session

from app.decorators import register_update, chat_language
from app.models import Chat


@register_update
@chat_language
def stop_command(bot, update, chat_info, _):
    if chat_info['is_subscribed']:
        Session().query(Chat).filter_by(
            id=update.message.chat_id
        ).update({'is_subscribed': False})
        transaction.commit()

    bot.send_message(
        chat_id=update.message.chat_id,
        text=_("You're unsubscribed. You always can subscribe again 👉 /start")
    )
