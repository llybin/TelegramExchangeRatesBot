import logging

import sentry_sdk
from pyramid_sqlalchemy import init_sqlalchemy
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
from suite.conf import settings

from . import sentry_before_send
from .decorators import register_update, chat_language
from .logic import get_keyboard

from app.commands.currencies import currencies_command
from app.commands.disclaimers import disclaimers_command
from app.commands.feedback import feedback_command, send_feedback_command
from app.commands.help import help_command
from app.commands.keyboard import keyboard_command
from app.commands.price import price_command, message_command, empty_command, inline_query
from app.commands.personal_settings import (
    SettingsSteps,
    settings_commands,
    settings_language_commands,
    settings_language_set_commands,
    settings_default_currency_commands,
    settings_default_currency_set_commands,
    settings_default_currency_position_commands,
    settings_default_currency_position_set_commands,
)
from app.commands.sources import sources_command
from app.commands.start import start_command
from app.commands.stop import stop_command
from app.commands.tutorial import tutorial_command


@register_update
@chat_language
def cancel_command(bot, update, chat_info, _):
    bot.send_message(
        chat_id=update.message.chat_id,
        reply_markup=get_keyboard(update.message.chat_id),
        text='👌')

    return ConversationHandler.END


def error_handler(bot, update, err):
    logging.exception(f'Telegram bot error handler: %s', err)


def main():
    if settings.SENTRY_URL:
        sentry_sdk.init(
            dsn=settings.SENTRY_URL,
            before_send=sentry_before_send
        )

    db_engine = create_engine(settings.DATABASE['url'])
    init_sqlalchemy(db_engine)

    updater = Updater(token=settings.BOT_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("currencies", currencies_command))
    dp.add_handler(CommandHandler("disclaimers", disclaimers_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("keyboard", keyboard_command))
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
        entry_points=[CommandHandler("settings", settings_commands)],
        states={
            SettingsSteps.settings: [
                RegexHandler(r"^1:", settings_language_commands),
                RegexHandler(r"^2:", settings_default_currency_commands),
                RegexHandler(r"^3:", settings_default_currency_position_commands),
                RegexHandler(r"^4:", cancel_command),
            ],
            SettingsSteps.language: [
                CommandHandler('back', settings_commands),
                MessageHandler(Filters.text, settings_language_set_commands)
            ],
            SettingsSteps.default_currency: [
                CommandHandler('back', settings_commands),
                MessageHandler(Filters.text, settings_default_currency_set_commands)
            ],
            SettingsSteps.default_currency_position: [
                CommandHandler('back', settings_commands),
                MessageHandler(Filters.text, settings_default_currency_position_set_commands)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)]
    )

    dp.add_handler(settings_handler)
    dp.add_handler(CommandHandler("settings", settings_commands))

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
