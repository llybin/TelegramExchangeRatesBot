from gettext import gettext

import transaction
from telegram import ParseMode, ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext
from suite.database import Session

from app.callbacks.personal_settings.main import SettingsSteps, main_menu
from app.decorators import register_update, chat_language
from app.models import Chat
from app.keyboard import KeyboardSimpleClever


@register_update
@chat_language
def menu_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    if chat_info['default_currency_position']:
        position = f'___{chat_info["default_currency"]}'
    else:
        position = f'{chat_info["default_currency"]}___'

    text_to = _('*%(position)s* - position where your default currency will be added.') % {
        'position': position}

    keyboard = KeyboardSimpleClever(
        [
            f'{chat_info["default_currency"]}___',
            f'___{chat_info["default_currency"]}',
            '↩️',
        ], 3
    ).show()

    update.message.reply_text(
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup(keyboard),
        text=text_to)

    return SettingsSteps.default_currency_position


@register_update
@chat_language
def set_command(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    if update.message.text.endswith('___'):
        default_currency_position = False
    elif update.message.text.startswith('___'):
        default_currency_position = True
    else:
        update.message.reply_text(text='🧐')
        return SettingsSteps.default_currency_position

    if default_currency_position:
        position = f'___{chat_info["default_currency"]}'
    else:
        position = f'{chat_info["default_currency"]}___'

    db_session = Session()
    db_session.query(Chat).filter_by(
        id=update.message.chat_id
    ).update({'default_currency_position': default_currency_position})
    transaction.commit()

    text_to = _('*%(position)s* - position where your default currency will be added.') % {
        'position': position}

    update.message.reply_text(
        parse_mode=ParseMode.MARKDOWN,
        text=text_to)

    main_menu(update, chat_info, _)

    return SettingsSteps.main
