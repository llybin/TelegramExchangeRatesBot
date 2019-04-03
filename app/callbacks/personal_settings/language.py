from gettext import gettext

import transaction
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext
from suite.conf import settings
from suite.database import Session

from app.callbacks.personal_settings.main import SettingsSteps, main_menu
from app.decorators import register_update, chat_language
from app.models import Chat
from app.translations import get_translations
from app.keyboard import KeyboardSimpleClever

LANGUAGES_LIST = sorted(settings.LANGUAGES_NAME.keys())
LOCALE_NAME = {v: k for k, v in settings.LANGUAGES_NAME.items()}


@register_update
@chat_language
def menu_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    if chat_info['locale'] in LOCALE_NAME:
        language_name = LOCALE_NAME[chat_info['locale']]
        text_to = _('*%(language)s* is your language now.') % {'language': language_name}
    else:
        text_to = 'Your language has no translation. Help fix it 👉 [poeditor.com](%(trans_link)s)' % {
            'trans_link': 'https://poeditor.com/join/project/LLu8AztSPb'}

    keyboard = KeyboardSimpleClever(['↩️'] + LANGUAGES_LIST, 2).show()

    update.message.reply_text(
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup(keyboard),
        text=text_to)

    return SettingsSteps.language


@register_update
def set_callback(update: Update, context: CallbackContext, chat_info: dict):
    if update.message.text not in settings.LANGUAGES_NAME:
        update.message.reply_text(text='🧐')
        return SettingsSteps.language
    else:
        locale = settings.LANGUAGES_NAME[update.message.text]

    db_session = Session()
    db_session.query(Chat).filter_by(
        id=update.message.chat_id
    ).update({'locale': locale})
    transaction.commit()

    _ = get_translations(locale)
    text_to = _('*%(language)s* is your language now.') % {'language': LOCALE_NAME[locale]}

    update.message.reply_text(
        parse_mode=ParseMode.MARKDOWN,
        text=text_to)

    main_menu(update, chat_info, _)

    return SettingsSteps.main
