import logging

import sentry_sdk
import transaction
from sentry_sdk.integrations.logging import LoggingIntegration
from pyramid_sqlalchemy import init_sqlalchemy, Session
from telegram import ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler
from sqlalchemy import create_engine

from .logic import get_keyboard, price_requester
from suite.conf import settings

from .decorators import register_update, chat_language
from .models import Chat, Currency


def tutorial(bot, update, _):
    bot.send_message(
        chat_id=update.message.chat_id,
        text=_('I am bot. I will help you to know a current exchange rates.'))

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode='Markdown',
        text=_('''Send me a message like this:
    *BTC USD* - to see the current exchange rate for pair
    *100 USD EUR* - to convert the amount from 100 USD to EUR'''))

    bot.send_message(
        chat_id=update.message.chat_id,
        text=_('Just text me message in private chat.'))

    bot.send_message(
        chat_id=update.message.chat_id,
        text=_('In group chats use commands like this: 👉 /p USD EUR 👈 or simply /USDEUR'))

    bot.send_message(
        chat_id=update.message.chat_id,
        reply_markup=get_keyboard(update.message.chat_id),
        text=_('Also look here 👉 /help'))


@register_update(pass_chat_created=True)
@chat_language
def start_command(bot, update, chat_created, _):
    name = update.message.from_user.first_name if update.message.chat.type == 'private' else _('humans')

    bot.send_message(
        chat_id=update.message.chat_id,
        text=_('Hello, %(name)s!') % {'name': name})

    if chat_created:
        tutorial(bot, update, _)

    else:
        Session().query(Chat).filter_by(id=update.message.chat_id).update({'is_subscribed': True})
        transaction.commit()

        bot.send_message(
            chat_id=update.message.chat_id,
            reply_markup=get_keyboard(update.message.chat_id),
            text=_('Have any question how to talk with me? 👉 /tutorial'))


@register_update()
@chat_language
def tutorial_command(bot, update, _):
    tutorial(bot, update, _)


@register_update()
@chat_language
def stop_command(bot, update, _):
    Session().query(Chat).filter_by(id=update.message.chat_id).update({'is_subscribed': False})
    transaction.commit()

    bot.send_message(
        chat_id=update.message.chat_id,
        text=_("You're unsubscribed.") + " " + _("You can subscribe again /start")
    )


@register_update()
@chat_language
def help_command(bot, update, _):
    text_to = _('''*Commands*

/start - Start to enslave mankind
/tutorial - Tutorial, how to talk with me
/currencies - All currencies that I support.
/cancel - Cancel the current operation
/feedback - If you have suggestions, text me
/keyboard - Hide / show a keyboard with request history
/p - Command for group chats, get exchange rate
/sources - Currency rates sources
/disclaimers - Disclaimers
/stop - Unsubscribe

[Help improve translation](%(trans_link)s)
''' % {'trans_link': 'https://poeditor.com/join/project/LLu8AztSPb'})

    text_to += '''\nSSD cloud servers in regions: New York, San Francisco, Amsterdam, Singapore, London, Frankfurt, Toronto, Bangalore.

Sign up using [link](%(link)s) and receive $100. From $5 per month: 1GB / 1 CPU / 25GB SSD Disk.''' % {
        'link': 'https://m.do.co/c/ba04a478e10d'}  # NOQA

    bot.send_message(
        chat_id=update.message.chat_id,
        disable_web_page_preview=True,
        parse_mode='Markdown',
        text=text_to)


@register_update()
def sources_command(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        disable_web_page_preview=True,
        parse_mode='Markdown',
        text='''*Sources*

https://bitfinex.com - 10min
https://bittrex.com - 1min
https://openexchangerates.org - 60min''')


@register_update()
@chat_language
def keyboard_command(bot, update, _):
    chat_id = update.message.chat_id

    if chat_id > 0:
        db_session = Session()
        chat = db_session.query(Chat).filter_by(id=chat_id).first()

        if chat.is_console_mode:
            chat.is_console_mode = False
            reply_markup = get_keyboard(chat_id)
            text_to = _("Console mode is disabled.")
        else:
            chat.is_console_mode = True
            reply_markup = ReplyKeyboardRemove()
            text_to = _("Console mode is enabled.")

        transaction.commit()
    else:
        text_to = _("The command is not available for group chats")
        reply_markup = ReplyKeyboardRemove()

    bot.send_message(
        chat_id=update.message.chat_id,
        reply_markup=reply_markup,
        text=text_to)


@register_update()
def currencies_command(bot, update):
    text_to = '\n'.join([f'{code} - {name}' for code, name in Session().query(
        Currency.code, Currency.name).filter_by(is_active=True).order_by(Currency.name)])

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode='Markdown',
        text=text_to)


@register_update()
@chat_language
def disclaimers_command(bot, update, _):
    bot.send_message(
        chat_id=update.message.chat_id,
        text=_('Data is provided by financial exchanges and may be delayed '
               'as specified by financial exchanges or our data providers. '
               'Bot does not verify any data and disclaims any obligation '
               'to do so. Bot cannot guarantee the accuracy of the exchange '
               'rates displayed. You should confirm current rates before making '
               'any transactions that could be affected by changes in '
               'the exchange rates.'))


@register_update()
@chat_language
def price_command(bot, update, args, _):
    text = ''.join(args)
    price_requester(bot, update, text)


@register_update()
@chat_language
def message_command(bot, update, _):
    price_requester(bot, update, update.message.text)


@register_update()
@chat_language
def empty_command(bot, update, _):
    price_requester(bot, update, update.message.text[1:])


def error_handler(bot, update, err):
    logging.error(f'Telegram bot error handler', extra=dict(
        bot=bot, update=update, err=err
    ))


def main():
    if settings.SENTRY_URL:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        )
        sentry_sdk.init(
            dsn=settings.SENTRY_URL,
            integrations=[sentry_logging]
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
    dp.add_handler(CommandHandler("sources", sources_command))
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("stop", stop_command))
    dp.add_handler(CommandHandler("tutorial", tutorial_command))
    dp.add_handler(RegexHandler(r"^/", empty_command))

    # on noncommand i.e message - echo the message on Telegram
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
