import transaction
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from suite.database import Session

from app.commands.personal_settings.main import SettingsSteps, main_menu
from app.decorators import register_update, chat_language
from app.models import Chat
from app.keyboard import KeyboardSimpleClever


@register_update
@chat_language
def menu_command(bot, update, chat_info, _):
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

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup(keyboard),
        text=text_to)

    return SettingsSteps.default_currency_position


@register_update
@chat_language
def set_command(bot, update, chat_info, _):
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

    return SettingsSteps.main
