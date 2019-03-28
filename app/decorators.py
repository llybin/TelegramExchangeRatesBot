import logging
from functools import wraps

import transaction
from sqlalchemy.exc import IntegrityError

from suite.database import Session
from suite.conf import settings

from app.translations import get_translations
from app.models import Chat
from app.tasks import update_chat


def register_update(func):
    def wrapper(bot, update, *args, **kwargs):
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
                first_name=update.effective_user.first_name if chat_id > 0 else None,
                username=update.effective_user.username if chat_id > 0 else None,
                locale=language_code,
                is_console_mode=False if chat_id > 0 else True,  # never show keyboard for a group chats
            )
            db_session.add(chat)
            try:
                transaction.commit()
                chat_created = True
                chat = db_session.query(Chat).filter_by(id=chat_id).one()
            except IntegrityError:
                chat_created = False
                logging.exception("Error create chat, chat exists")
                transaction.abort()
                chat = db_session.query(Chat).filter_by(id=chat_id).one()
        else:
            chat_created = False
            update_chat.delay(
                chat_id=chat.id,
                first_name=chat.first_name,
                username=chat.username)

        kwargs['chat_info'] = {
            'chat_id': chat.id,
            'created': chat_created,
            'locale': chat.locale,
            'is_subscribed': chat.is_subscribed,
            'is_console_mode': chat.is_console_mode,
            'default_currency': chat.default_currency,
            'default_currency_position': chat.default_currency_position,
        }

        return func(bot, update, *args, **kwargs)

    return wrapper


def chat_language(func):
    @wraps(func)
    def wrapper(bot, update, *args, **kwargs):
        language_code = kwargs['chat_info']['locale']

        kwargs['_'] = get_translations(language_code)

        return func(bot, update, *args, **kwargs)

    return wrapper
