from enum import Enum

from telegram import ReplyKeyboardMarkup

from app.decorators import register_update, chat_language


class SettingsSteps(Enum):
    main = 0
    language = 1
    default_currency = 2
    default_currency_position = 3
    onscreen_menu = 4
    onscreen_menu_visibility = 5
    onscreen_menu_edit_history = 6


def main_menu(bot, update, chat_info, _):
    bot.send_message(
        chat_id=update.message.chat_id,
        reply_markup=ReplyKeyboardMarkup([
            [f'{SettingsSteps.language.value}: ' + _("Language")],
            [f'{SettingsSteps.default_currency.value}: ' + _("Default currency")],
            [f'{SettingsSteps.default_currency_position.value}: ' + _("Default currency position")],
            [f'{SettingsSteps.onscreen_menu.value}: ' + _("On-screen menu below")],
            ['↩️'],
        ]),
        text=_('What do you want to set up?'))


@register_update
@chat_language
def settings_command(bot, update, chat_info, _):
    chat_id = update.message.chat_id

    if chat_id < 0:
        update.message.reply_text(_("The command is not available for group chats"))
        return

    main_menu(bot, update, chat_info, _)

    return SettingsSteps.main


