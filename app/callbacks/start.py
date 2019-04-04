from gettext import gettext

import transaction
from sqlalchemy.sql import true
from suite.database import Session
from telegram import Update
from telegram.ext import ConversationHandler, CallbackContext

from app.callbacks.tutorial import tutorial
from app.decorators import register_update, chat_language
from app.logic import get_keyboard
from app.models import Chat


@register_update
@chat_language
def start_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    if update.message.chat.type == 'private':
        name = update.message.from_user.first_name
    else:
        name = _('humans')

    update.message.reply_text(
        text=_('Hello, %(name)s!') % {'name': name})

    if chat_info['created']:
        tutorial(update, _)

    else:
        if not chat_info['is_subscribed']:
            Session().query(Chat).filter_by(
                id=update.message.chat_id
            ).update({'is_subscribed': true()})
            transaction.commit()

        update.message.reply_text(
            reply_markup=ReplyKeyboardMarkup(get_keyboard(update.message.chat_id)),
            text=_('Have any question how to talk with me? 👉 /tutorial'))

    return ConversationHandler.END
