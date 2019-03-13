import logging
from pyramid_sqlalchemy import Session
from telegram import ReplyKeyboardMarkup

from suite.conf import settings
from .converter.converter import convert
from .converter.exceptions import ConverterException
from .converter.formatter import format_price_request_result
from .helpers import import_module
from .keyboard import KeyboardSimpleClever
from .models import Chat, ChatRequests
from .parsers.exceptions import ValidationException


def get_keyboard(chat_id):
    if chat_id < 0:
        return None

    db_session = Session()
    chat = db_session.query(Chat).filter_by(id=chat_id).first()

    if chat.is_console_mode:
        return None

    else:
        last_requests = db_session.query(ChatRequests).filter_by(
            chat_id=chat_id
        ).order_by(
            ChatRequests.times.desc()
        ).limit(9).all()

        if last_requests:
            last_reqs_list = [f'{x.from_currency.code} {x.to_currency.code}' for x in last_requests]
            keyboard = KeyboardSimpleClever(last_reqs_list, width=3).show()
            reply_markup = ReplyKeyboardMarkup(keyboard)
        else:
            reply_markup = None

        return reply_markup


PARSERS = {import_module(parser_path) for parser_path in settings.BOT_PARSERS}


def start_parse(text):
    for parser in PARSERS:
        try:
            return parser(text).parse()
        except ValidationException:
            pass

    raise ValidationException


def price_requester(bot, update, text):
    if not text:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Request must contain arguments. See /help')
        return

    try:
        price_request = start_parse(text)
    except ValidationException:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='Wrong format or unknown currency. See /help')
        return

    logging.info(f'price_request: {text} -> {price_request}')

    try:
        price_request_result = convert(price_request)
    except ConverterException:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='No rates. See /help')
        return

    logging.info(f'price_request: {price_request_result}')

    result = format_price_request_result(price_request_result)

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode='Markdown',
        reply_markup=get_keyboard(update.message.chat_id),
        text=f'{result}')
