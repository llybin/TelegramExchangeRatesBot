from enum import Enum

import transaction
from pyramid_sqlalchemy import Session
from telegram import ReplyKeyboardMarkup, ParseMode, ReplyKeyboardRemove
from suite.conf import settings

from .. import translations
from app.decorators import register_update, chat_language
from app.models import Chat, Currency


class SettingsSteps(Enum):
    settings = 0
    language = 1
    default_currency = 2
    default_currency_position = 3


LANGUAGES_LIST = list(map(lambda x: [x], sorted(settings.LANGUAGES_NAME.keys())))
LOCALE_NAME = {v: k for k, v in settings.LANGUAGES_NAME.items()}


def main_menu(bot, update, chat_info, _):
    bot.send_message(
        chat_id=update.message.chat_id,
        reply_markup=ReplyKeyboardMarkup([
            [f'1: {_("Language")}'],
            [f'2: {_("Default currency")}'],
            [f'3: {_("Default currency position")}'],
            [f'4: {_("Close settings")}']
        ]),
        text=_('What do you want to set up?'))


@register_update
@chat_language
def settings_commands(bot, update, chat_info, _):
    chat_id = update.message.chat_id

    if chat_id < 0:
        update.message.reply_text(_("The command is not available for group chats"))
        return

    main_menu(bot, update, chat_info, _)

    return SettingsSteps.settings


@register_update
@chat_language
def settings_language_commands(bot, update, chat_info, _):
    text_to = _('*%(language)s* is your language now.') % {
        'language': LOCALE_NAME[chat_info['locale']]}
    text_to += ' ' + _('If you\'d like to change send me new or /back')

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup(LANGUAGES_LIST),
        text=text_to)

    return SettingsSteps.language


@register_update
def settings_language_set_commands(bot, update, chat_info):
    if update.message.text not in settings.LANGUAGES_NAME:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='🧐')
        return SettingsSteps.language
    else:
        locale = settings.LANGUAGES_NAME[update.message.text]

    db_session = Session()
    db_session.query(Chat).filter_by(
        id=update.message.chat_id
    ).update({'locale': locale})
    transaction.commit()

    _ = translations[locale].gettext
    text_to = _('*%(language)s* is your language now.') % {'language': LOCALE_NAME[locale]}

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardRemove(),
        text=text_to)

    main_menu(bot, update, chat_info, _)

    return SettingsSteps.settings


@register_update
@chat_language
def settings_default_currency_commands(bot, update, chat_info, _):
    text_to = _('*%(default_currency)s* is your default currency.') % {
        'default_currency': chat_info['default_currency']}
    text_to += ' ' + _('If you\'d like to change send me new or /back')

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardRemove(),
        text=text_to)

    return SettingsSteps.default_currency


@register_update
@chat_language
def settings_default_currency_set_commands(bot, update, chat_info, _):
    currency_code = update.message.text.upper()

    db_session = Session()

    currency = db_session.query(Currency).filter_by(
        code=currency_code,
        is_active=True
    ).first()

    if not currency:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='🧐')
        return SettingsSteps.default_currency

    db_session.query(Chat).filter_by(
        id=update.message.chat_id
    ).update({'default_currency': currency_code})
    transaction.commit()

    text_to = _('*%(default_currency)s* is your default currency.') % {
        'default_currency': currency_code}

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardRemove(),
        text=text_to)

    main_menu(bot, update, chat_info, _)

    return SettingsSteps.settings


@register_update
@chat_language
def settings_default_currency_position_commands(bot, update, chat_info, _):
    if chat_info['default_currency_position']:
        position = f'___{chat_info["default_currency"]}'
    else:
        position = f'{chat_info["default_currency"]}___'

    text_to = _('*%(position)s* - position where your default currency will be added.') % {
        'position': position}
    text_to += ' ' + _('If you\'d like to change send me new or /back')

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup([
            [f'{chat_info["default_currency"]}___', f'___{chat_info["default_currency"]}'],
        ]),
        text=text_to)

    return SettingsSteps.default_currency_position


@register_update
@chat_language
def settings_default_currency_position_set_commands(bot, update, chat_info, _):
    if update.message.text.endswith('___'):
        default_currency_position = False
    elif update.message.text.startswith('___'):
        default_currency_position = True
    else:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='🧐')
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

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardRemove(),
        text=text_to)

    main_menu(bot, update, chat_info, _)

    return SettingsSteps.settings
