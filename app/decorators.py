import gettext
import logging
from functools import wraps

import transaction
from pyramid_sqlalchemy import Session
from sqlalchemy.exc import IntegrityError

from app import translations
from .models import Chat


def register_update(func):
    def wrapper(bot, update, *args, **kwargs):
        chat_id = update.effective_chat.id

        db_session = Session()
        chat = db_session.query(Chat).filter_by(id=chat_id).scalar()
        chat_created = False

        if not chat:
            chat_created = True
            chat = Chat(
                id=chat_id,
                first_name=update.message.from_user.first_name if chat_id > 0 else None,
                username=update.message.from_user.username if chat_id > 0 else None,
                locale=update.message.from_user.language_code,
                is_console_mode=False if chat_id > 0 else True,
            )
            db_session.add(chat)
            try:
                transaction.commit()
            except IntegrityError:
                logging.exception("Error create chat, chat exists")
                transaction.abort()

        kwargs['chat_info'] = {
            'created': chat_created,
            'locale': chat.locale,
            'is_subscribed': chat.is_subscribed,
            'is_console_mode': chat.is_console_mode,
        }

        return func(bot, update, *args, **kwargs)

    return wrapper


def chat_language(func):
    @wraps(func)
    def wrapper(bot, update, *args, **kwargs):
        language_code = kwargs['chat_info']['locale']

        if language_code in translations:
            locale = language_code
            _ = translations[locale].gettext

        elif language_code[:2] in translations:
            locale = language_code[:2]
            _ = translations[locale].gettext

        else:
            _ = gettext.gettext

        kwargs['_'] = _

        return func(bot, update, *args, **kwargs)

    return wrapper
