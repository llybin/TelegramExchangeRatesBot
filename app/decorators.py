import logging
from functools import wraps

from sqlalchemy.exc import IntegrityError

import transaction
from app.models import Chat
from app.translations import get_translations
from suite.conf import settings
from suite.database import Session
from telegram import Update
from telegram.ext import CallbackContext


def register_update(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        if not update.effective_user:
            # bots, may be exclude in filter messages
            return

        if update.effective_chat:
            # we need settings for a group chats, not for a specific user
            # private chat id == user id
            chat_id = update.effective_chat.id
        else:
            # inline commands, get settings for his private chat
            chat_id = update.effective_user.id

        if update.effective_user.language_code:
            # chats don't have language_code, that why we take from user, not so correct yes
            # they will able change language later
            # https://en.wikipedia.org/wiki/IETF_language_tag
            language_code = update.effective_user.language_code.lower()
        else:
            # some users don't have locale, set default
            language_code = settings.LANGUAGE_CODE

        db_session = Session()

        chat = db_session.query(Chat).filter_by(id=chat_id).first()

        if not chat:
            chat = Chat(
                id=chat_id,
                locale=language_code,
                is_show_keyboard=True
                if chat_id > 0
                else False,  # never show keyboard for a group chats
            )
            db_session.add(chat)
            try:
                transaction.commit()
                chat_created = True
            except IntegrityError:
                chat_created = False
                logging.exception("Error create chat, chat exists")
                transaction.abort()
            finally:
                chat = db_session.query(Chat).filter_by(id=chat_id).one()
        else:
            chat_created = False

        kwargs["chat_info"] = {
            "chat_id": chat.id,
            "created": chat_created,
            "locale": chat.locale,
            "is_subscribed": chat.is_subscribed,
            "is_show_keyboard": chat.is_show_keyboard,
            "keyboard_size": chat.keyboard_size,
            "default_currency": chat.default_currency,
            "default_currency_position": chat.default_currency_position,
        }

        return func(update, context, *args, **kwargs)

    return wrapper


def chat_language(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        language_code = kwargs["chat_info"]["locale"]

        kwargs["_"] = get_translations(language_code)

        return func(update, context, *args, **kwargs)

    return wrapper
