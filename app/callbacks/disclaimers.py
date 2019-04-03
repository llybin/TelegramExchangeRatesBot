from gettext import gettext

from telegram import Update
from telegram.ext import ConversationHandler, CallbackContext

from app.decorators import register_update, chat_language


@register_update
@chat_language
def disclaimers_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    update.message.reply_text(
        text=_('Data is provided by financial exchanges and may be delayed '
               'as specified by financial exchanges or our data providers. '
               'Bot does not verify any data and disclaims any obligation '
               'to do so. Bot cannot guarantee the accuracy of the exchange '
               'rates displayed. You should confirm current rates before making '
               'any transactions that could be affected by changes in '
               'the exchange rates.'))

    return ConversationHandler.END

