from telegram import ParseMode, Update
from telegram.ext import ConversationHandler, CallbackContext

from suite.database import Session

from app.decorators import register_update
from app.models import Currency


@register_update
def currencies_callback(update: Update, context: CallbackContext, chat_info: dict):
    text_to = '\n'.join([f'{code} - {name}' for code, name in Session().query(
        Currency.code, Currency.name).filter_by(is_active=True).order_by(Currency.name)])

    update.message.reply_text(
        parse_mode=ParseMode.MARKDOWN,
        text=text_to)

    return ConversationHandler.END
