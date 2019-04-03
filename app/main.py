import logging

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    CallbackContext,
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    InlineQueryHandler,
)
from sqlalchemy import create_engine
from suite.database import init_sqlalchemy
from suite.conf import settings

from app.decorators import register_update
from app.logic import get_keyboard
from app.sentry import init_sentry
from app.state_storage import RedisPersistence
from app.translations import init_translations

from app.callbacks.currencies import currencies_callback
from app.callbacks.disclaimers import disclaimers_callback
from app.callbacks.feedback import feedback_callback, send_feedback_callback
from app.callbacks.help import help_callback
from app.callbacks.price import price_callback, message_callback, on_slash_callback, inline_query_callback
from app.callbacks.personal_settings.main import SettingsSteps, settings_callback
from app.callbacks.personal_settings import language
from app.callbacks.personal_settings import default_currency
from app.callbacks.personal_settings import default_currency_position
from app.callbacks.personal_settings import onscreen_menu
from app.callbacks.sources import sources_callback
from app.callbacks.start import start_callback
from app.callbacks.stop import stop_callback
from app.callbacks.tutorial import tutorial_callback


@register_update
def cancel_callback(update: Update, context: CallbackContext, chat_info: dict):
    keyboard = get_keyboard(update.message.chat_id)
    if not keyboard:
        keyboard = ReplyKeyboardRemove()

    update.message.reply_text(
        reply_markup=keyboard,
        text='👌')

    return ConversationHandler.END


def error_callback(update: Update, context: CallbackContext):
    logging.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    init_sentry()

    db_engine = create_engine(settings.DATABASE['url'])
    init_sqlalchemy(db_engine)

    init_translations()

    updater = Updater(
        token=settings.BOT_TOKEN,
        persistence=RedisPersistence(),
        use_context=True)

    dp = updater.dispatcher

    feedback_handler = ConversationHandler(
        entry_points=[CommandHandler("feedback", feedback_callback)],
        states={
            1: [MessageHandler(Filters.text, send_feedback_callback)]
        },
        fallbacks=[CommandHandler("nothing", cancel_callback)],
        name="feedback_conversation",
        persistent=True
    )

    dp.add_handler(feedback_handler)

    settings_handler = ConversationHandler(
        entry_points=[CommandHandler("settings", settings_callback)],
        states={
            SettingsSteps.main: [
                MessageHandler(Filters.regex(r"^↩️"), cancel_callback),
                MessageHandler(Filters.regex(r"^1:"), language.menu_callback),
                MessageHandler(Filters.regex(r"^2:"), default_currency.menu_callback),
                MessageHandler(Filters.regex(r"^3:"), default_currency_position.menu_callback),
                MessageHandler(Filters.regex(r"^4:"), onscreen_menu.menu_callback),
            ],
            SettingsSteps.language: [
                MessageHandler(Filters.regex(r"^↩️"), settings_callback),
                MessageHandler(Filters.text, language.set_callback),
            ],
            SettingsSteps.default_currency: [
                MessageHandler(Filters.regex(r"^↩️"), settings_callback),
                MessageHandler(Filters.text, default_currency.set_callback),
            ],
            SettingsSteps.default_currency_position: [
                MessageHandler(Filters.regex(r"^↩️"), settings_callback),
                MessageHandler(Filters.text, default_currency_position.set_command),
            ],
            SettingsSteps.onscreen_menu: [
                MessageHandler(Filters.regex(r"^↩️"), settings_callback),
                MessageHandler(Filters.regex(r"^1:"), onscreen_menu.visibility_callback),
                MessageHandler(Filters.regex(r"^2:"), onscreen_menu.edit_history_callback),
            ],
            SettingsSteps.onscreen_menu_visibility: [
                MessageHandler(Filters.regex(r"^↩️"), onscreen_menu.menu_callback),
                MessageHandler(Filters.regex(r"^1"), onscreen_menu.visibility_set_true_callback),
                MessageHandler(Filters.regex(r"^2"), onscreen_menu.visibility_set_false_callback),
            ],
            SettingsSteps.onscreen_menu_edit_history: [
                MessageHandler(Filters.regex(r"^↩️"), onscreen_menu.menu_callback),
                MessageHandler(Filters.regex(r"^🅾️"), onscreen_menu.edit_history_delete_old_callback),
                MessageHandler(Filters.regex(r"^🆑"), onscreen_menu.edit_history_delete_all_callback),
                MessageHandler(Filters.regex(r"^❌"), onscreen_menu.edit_history_delete_one_callback),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)],
        name="settings_conversation",
        persistent=True
    )

    dp.add_handler(settings_handler)

    dp.add_handler(CommandHandler("currencies", currencies_callback))
    dp.add_handler(CommandHandler("disclaimers", disclaimers_callback))
    dp.add_handler(CommandHandler("feedback", feedback_callback))
    dp.add_handler(CommandHandler("help", help_callback))
    dp.add_handler(CommandHandler("p", price_callback, pass_args=True))
    dp.add_handler(CommandHandler("settings", settings_callback))
    dp.add_handler(CommandHandler("start", start_callback))
    dp.add_handler(CommandHandler("stop", stop_callback))
    dp.add_handler(CommandHandler("sources", sources_callback))
    dp.add_handler(CommandHandler("tutorial", tutorial_callback))
    dp.add_handler(MessageHandler(Filters.regex(r"^/"), on_slash_callback))
    dp.add_handler(MessageHandler(Filters.text, message_callback))

    dp.add_handler(InlineQueryHandler(inline_query_callback))

    # log all errors
    dp.add_error_handler(error_callback)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
