from telegram import ParseMode, Update
from telegram.ext import ConversationHandler, CallbackContext

from app.decorators import register_update


@register_update
def sources_callback(update: Update, context: CallbackContext, chat_info: dict):
    update.message.reply_text(
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
        text='''*Sources*

https://bitfinex.com - 15min (API limits😭)
https://bittrex.com - 1min
[https://bitkub.com](https://www.bitkub.com/signup?ref=64572) - 1min
https://sp-today.com - 60min
https://fixer.io - 60min
https://openexchangerates.org - 60min''')

    return ConversationHandler.END
