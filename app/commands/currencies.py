from pyramid_sqlalchemy import Session
from telegram import ParseMode

from app.decorators import register_update
from app.models import Currency


@register_update
def currencies_command(bot, update, chat_info):
    text_to = '\n'.join([f'{code} - {name}' for code, name in Session().query(
        Currency.code, Currency.name).filter_by(is_active=True).order_by(Currency.name)])

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        text=text_to)
