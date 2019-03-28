import transaction
from sqlalchemy.sql import true
from suite.database import Session

from app.commands.tutorial import tutorial
from app.decorators import register_update, chat_language
from app.logic import get_keyboard
from app.models import Chat


@register_update
@chat_language
def start_command(bot, update, chat_info, _):
    if update.message.chat.type == 'private':
        name = update.message.from_user.first_name
    else:
        name = _('humans')

    bot.send_message(
        chat_id=update.message.chat_id,
        text=_('Hello, %(name)s!') % {'name': name})

    if chat_info['created']:
        tutorial(bot, update, _)

    else:
        if not chat_info['is_subscribed']:
            Session().query(Chat).filter_by(
                id=update.message.chat_id
            ).update({'is_subscribed': true()})
            transaction.commit()

        bot.send_message(
            chat_id=update.message.chat_id,
            reply_markup=get_keyboard(update.message.chat_id),
            text=_('Have any question how to talk with me? 👉 /tutorial'))
