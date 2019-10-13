from app.decorators import register_update
from app.queries import get_all_currencies
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler


@register_update
def currencies_callback(update: Update, context: CallbackContext, chat_info: dict):
    text_to = "\n".join([f"{code} - {name}" for code, name in get_all_currencies()])

    update.message.reply_text(parse_mode=ParseMode.MARKDOWN, text=text_to)

    return ConversationHandler.END
