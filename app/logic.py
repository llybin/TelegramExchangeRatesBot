from pyramid_sqlalchemy import Session
from telegram import ReplyKeyboardMarkup

from suite.conf import settings
from .helpers import import_module
from .keyboard import KeyboardSimpleClever
from .models import Chat, ChatRequests
from .parsers.base import PriceRequest
from .parsers.exceptions import ValidationException


def get_keyboard(chat_id: int) -> ReplyKeyboardMarkup or None:
    if chat_id < 0:
        return None

    chat = Session.query(Chat).filter_by(id=chat_id).first()

    if chat.is_console_mode:
        return None

    else:
        last_requests = Session.query(ChatRequests).filter_by(
            chat_id=chat_id
        ).order_by(
            ChatRequests.times.desc()
        ).limit(9).all()

        if last_requests:
            last_reqs_list = [f'{x.from_currency.code} {x.to_currency.code}' for x in last_requests]
            keyboard = KeyboardSimpleClever(last_reqs_list).show()
            reply_markup = ReplyKeyboardMarkup(keyboard)
        else:
            reply_markup = None

        return reply_markup


PARSERS = {import_module(parser_path) for parser_path in settings.BOT_PARSERS}


def start_parse(text: str, chat_id: int, locale: str, default_currency: str, default_currency_position: bool) -> PriceRequest:
    for parser in PARSERS:
        try:
            return parser(text, chat_id, locale, default_currency, default_currency_position).parse()
        except ValidationException:
            pass

    raise ValidationException
