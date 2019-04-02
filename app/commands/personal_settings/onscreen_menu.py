import transaction
from telegram import ParseMode, ReplyKeyboardMarkup
from suite.database import Session

from app.commands.personal_settings.main import SettingsSteps
from app.decorators import register_update, chat_language
from app.models import Chat


def onscreen_menu(bot, update, chat_info, _):
    text_to = _('Here you can customize on-screen menu with history requests.')

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup([
            [_('1: Visibility')],
            [_('2: Remove from history')],
            [_('↩️')],
        ]),
        text=text_to)


@register_update
@chat_language
def menu_command(bot, update, chat_info, _):
    onscreen_menu(bot, update, chat_info, _)

    return SettingsSteps.onscreen_menu


@register_update
@chat_language
def visibility_command(bot, update, chat_info, _):
    if chat_info['is_show_keyboard']:
        text_to = _('On-screen menu below with history requests always shows at the moment.')
    else:
        text_to = _('On-screen menu below with history requests never shows at the moment.')

    text_to += '\n'

    text_to += _('You can choose. Show always on-screen menu below with history requests or never show.')

    bot.send_message(
        chat_id=update.message.chat_id,
        reply_markup=ReplyKeyboardMarkup([
            [_('1: Always show')],
            [_('2: Never show')],
            [_('↩️')],
        ]),
        text=text_to)

    return SettingsSteps.onscreen_menu_visibility


@register_update
@chat_language
def visibility_set_true_command(bot, update, chat_info, _):
    db_session = Session()
    chat = db_session.query(Chat).filter_by(id=update.message.chat_id).first()
    chat.is_show_keyboard = True
    transaction.commit()

    text_to = _('On-screen menu below with history requests will always shows.')

    bot.send_message(
        chat_id=update.message.chat_id,
        text=text_to)

    onscreen_menu(bot, update, chat_info, _)

    return SettingsSteps.onscreen_menu


@register_update
@chat_language
def visibility_set_false_command(bot, update, chat_info, _):
    db_session = Session()
    chat = db_session.query(Chat).filter_by(id=update.message.chat_id).first()
    chat.is_show_keyboard = False
    transaction.commit()

    text_to = _('On-screen menu below with history requests will never shows.')

    bot.send_message(
        chat_id=update.message.chat_id,
        text=text_to)

    onscreen_menu(bot, update, chat_info, _)

    return SettingsSteps.onscreen_menu


@register_update
@chat_language
def edit_history_command(bot, update, chat_info, _):
    text_to = _('You can choose. Show always on-screen menu below with history requests or never show.')

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup([
            [_('1: Show always')],
            [_('2: Never show')],
            [_('↩️')],
        ]),
        text=text_to)

    return SettingsSteps.onscreen_menu_edit_history
