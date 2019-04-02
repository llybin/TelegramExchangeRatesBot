import logging

import sentry_sdk
from telegram import ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    RegexHandler,
    ConversationHandler,
    InlineQueryHandler,
)
from sqlalchemy import create_engine
from suite.database import init_sqlalchemy
from suite.conf import settings

from app.decorators import register_update, chat_language
from app.logic import get_keyboard
from app.sentry import before_send
from app.translations import init_translations

from app.commands.currencies import currencies_command
from app.commands.disclaimers import disclaimers_command
from app.commands.feedback import feedback_command, send_feedback_command
from app.commands.help import help_command
from app.commands.price import price_command, message_command, empty_command, inline_query
from app.commands.personal_settings.main import SettingsSteps, settings_command
from app.commands.personal_settings import language
from app.commands.personal_settings import default_currency
from app.commands.personal_settings import default_currency_position
from app.commands.personal_settings import onscreen_menu
from app.commands.sources import sources_command
from app.commands.start import start_command
from app.commands.stop import stop_command
from app.commands.tutorial import tutorial_command


@register_update
@chat_language
def cancel_command(bot, update, chat_info, _):
    keyboard = get_keyboard(update.message.chat_id)
    if not keyboard:
        keyboard = ReplyKeyboardRemove()

    bot.send_message(
        chat_id=update.message.chat_id,
        reply_markup=keyboard,
        text='👌')

    return ConversationHandler.END


def error_handler(bot, update, err):
    logging.exception(f'Telegram bot error handler: %s', err)


def main():
    if settings.SENTRY_URL:
        sentry_sdk.init(
            dsn=settings.SENTRY_URL,
            before_send=before_send
        )

    db_engine = create_engine(settings.DATABASE['url'])
    init_sqlalchemy(db_engine)

    init_translations()

    updater = Updater(token=settings.BOT_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("currencies", currencies_command))
    dp.add_handler(CommandHandler("disclaimers", disclaimers_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("p", price_command, pass_args=True))
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("stop", stop_command))
    dp.add_handler(CommandHandler("sources", sources_command))
    dp.add_handler(CommandHandler("tutorial", tutorial_command))

    feedback_handler = ConversationHandler(
        entry_points=[CommandHandler("feedback", feedback_command)],
        states={
            1: [MessageHandler(Filters.text, send_feedback_command)]
        },
        fallbacks=[CommandHandler("nothing", cancel_command)]
    )

    dp.add_handler(feedback_handler)
    dp.add_handler(CommandHandler("feedback", feedback_command))

    settings_handler = ConversationHandler(
        entry_points=[CommandHandler("settings", settings_command)],
        states={
            SettingsSteps.main: [
                RegexHandler(r"^↩️", cancel_command),
                RegexHandler(r"^1:", language.menu_command),
                RegexHandler(r"^2:", default_currency.menu_command),
                RegexHandler(r"^3:", default_currency_position.menu_command),
                RegexHandler(r"^4:", onscreen_menu.menu_command),
            ],
            SettingsSteps.language: [
                RegexHandler(r"^↩️", settings_command),
                MessageHandler(Filters.text, language.set_command),
            ],
            SettingsSteps.default_currency: [
                RegexHandler(r"^↩️", settings_command),
                MessageHandler(Filters.text, default_currency.set_command),
            ],
            SettingsSteps.default_currency_position: [
                RegexHandler(r"^↩️", settings_command),
                MessageHandler(Filters.text, default_currency_position.set_command),
            ],
            SettingsSteps.onscreen_menu: [
                RegexHandler(r"^↩️", settings_command),
                RegexHandler(r"^1:", onscreen_menu.visibility_command),
                RegexHandler(r"^2:", onscreen_menu.edit_history_command),
            ],
            SettingsSteps.onscreen_menu_visibility: [
                RegexHandler(r"^↩️", onscreen_menu.onscreen_menu),
                RegexHandler(r"^1", onscreen_menu.visibility_set_true_command),
                RegexHandler(r"^2", onscreen_menu.visibility_set_false_command),
            ],
            # SettingsSteps.onscreen_menu_edit_history: [
            #     RegexHandler("^↩️", settings_commands),
            #     MessageHandler(Filters.text, default_currency_position.set_command),
            # ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)]
    )

    dp.add_handler(settings_handler)
    dp.add_handler(CommandHandler("settings", settings_command))

    dp.add_handler(RegexHandler(r"^/", empty_command))

    dp.add_handler(InlineQueryHandler(inline_query))

    dp.add_handler(MessageHandler(Filters.text, message_command))

    # log all errors
    dp.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
