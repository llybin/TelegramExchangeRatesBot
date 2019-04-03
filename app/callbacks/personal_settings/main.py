from gettext import gettext

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext

from app.decorators import register_update, chat_language


class SettingsSteps(object):
    main = 0
    language = 1
    default_currency = 2
    default_currency_position = 3
    onscreen_menu = 4
    onscreen_menu_visibility = 5
    onscreen_menu_edit_history = 6


def main_menu(update: Update, chat_info: dict, _: gettext):
    update.message.reply_text(
        reply_markup=ReplyKeyboardMarkup([
            ['1. ' + _("Language")],
            ['2. ' + _("Default currency")],
            ['3. ' + _("Default currency position")],
            ['4. ' + _("On-screen menu below")],
            ['↩️'],
        ]),
        text=_('What do you want to set up?'))


@register_update
@chat_language
def settings_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    chat_id = update.message.chat_id

    if chat_id < 0:
        update.message.reply_text(_("The command is not available for group chats"))
        return

    main_menu(update, chat_info, _)

    return SettingsSteps.main
