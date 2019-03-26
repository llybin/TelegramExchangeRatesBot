from telegram import ParseMode

from app.decorators import register_update, chat_language
from app.logic import get_keyboard


def tutorial(bot, update, _):
    bot.send_message(
        chat_id=update.message.chat_id,
        text=_('I am bot. I will help you to know a current exchange rates.'))

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        text=_('''Send me a message like this:
    *BTC USD* - to see the current exchange rate for pair
    *100 USD EUR* - to convert the amount from 100 USD to EUR'''))

    bot.send_message(
        chat_id=update.message.chat_id,
        text=_('Just text me message in private chat.'))

    bot.send_message(
        chat_id=update.message.chat_id,
        text=_('In group chats use commands like this: 👉 /p USD EUR 👈 or simply /USDEUR'))

    bot.send_message(
        chat_id=update.message.chat_id,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
        text=_('Inline mode is available. See how to use [here](%(link)s).') % {
            'link': 'https://telegram.org/blog/inline-bots'})

    bot.send_message(
        chat_id=update.message.chat_id,
        reply_markup=get_keyboard(update.message.chat_id),
        text=_('Also take a look here 👉 /help'))


@register_update
@chat_language
def tutorial_command(bot, update, chat_info, _):
    tutorial(bot, update, _)
