from telegram.ext import ConversationHandler

from app.decorators import register_update, chat_language


@register_update
@chat_language
def disclaimers_command(bot, update, chat_info, _):
    bot.send_message(
        chat_id=update.message.chat_id,
        text=_('Data is provided by financial exchanges and may be delayed '
               'as specified by financial exchanges or our data providers. '
               'Bot does not verify any data and disclaims any obligation '
               'to do so. Bot cannot guarantee the accuracy of the exchange '
               'rates displayed. You should confirm current rates before making '
               'any transactions that could be affected by changes in '
               'the exchange rates.'))

    return ConversationHandler.END

