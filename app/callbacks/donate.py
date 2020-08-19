from gettext import gettext

from telegram import ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler

from app.decorators import chat_language, register_update
from suite.conf import settings


@register_update
@chat_language
def donate_callback(
    update: Update, context: CallbackContext, chat_info: dict, _: gettext
):
    text_to = _("*Bot is free and online since 01 July 2015*")

    text_to += "\n\n"

    for currency, wallet in settings.DONATION_WALLETS.items():
        text_to += f"*{currency}*: `{wallet}`\n"

    update.message.reply_text(
        disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN, text=text_to
    )

    return ConversationHandler.END
