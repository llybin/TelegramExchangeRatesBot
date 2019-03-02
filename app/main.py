import logging
import time

from suite.conf import settings
from telegram import ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async

from app.libs.price import PRICE_PATTERN

logger = logging.getLogger(__name__)


@run_async
def start(bot, update):
    name = update.message.from_user.first_name if update.message.chat.type == 'private' else 'people'
    bot.send_message(
        chat_id=update.message.chat_id,
        text=f'Hello, {name}!')
    bot.send_message(
        chat_id=update.message.chat_id,
        text='I am bot. I will help you to know a current exchange rates.')
    bot.send_chat_action(
        chat_id=update.message.chat_id,
        action=ChatAction.TYPING)
    time.sleep(1)
    bot.send_message(
        chat_id=update.message.chat_id,
        text='Let\'s start!')
    time.sleep(0.5)
    bot.send_message(
        chat_id=update.message.chat_id,
        text='Here how to use information')


def help(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        disable_web_page_preview=True,
        parse_mode='Markdown',
        text='''*Commands*

/start - Tutorial
/currencies - A list of exchange rates
/cancel - Cancel the current operation
/feedback - If you have suggestions, text me
/consolemodetoggle - Hide/show a custom keyboard
/price, /p - Ask price
/sources - Currency rates sources
/disclaimers - Disclaimers
/stop - Unsubscribe

*How to use*

Send me a message to see the exchange rate: *usdeur*, *btcusd*
You can convert the amount: 2eurusd, irrusd5''')


def sources(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        disable_web_page_preview=True,
        parse_mode='Markdown',
        text='''*Sources*

BTC, LTC, ETH, XMR, ZEC - https://bitfinex.com - 15min
SYP - Syrian bank - 30min
BURST, DGB - https://cryptonator.com - 15min
ALL OTHER - https://openexchangerates.org - 60min''')


def disclaimers(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text='''Data is provided by financial exchanges and may be delayed as specified 
 by financial exchanges or our data providers.Bot does not verify any data
 and disclaims any obligation to do so. Bot cannot guarantee the accuracy
 of the exchange rates displayed. You should confirm current rates before
 making any transactions that could be affected by changes in the exchange rates.''')


def price(bot, update, args):
    obj = PRICE_PATTERN.match(''.join(args))
    if obj:
        param = obj.groups()
    else:
        param = '-><-'
    logging.info(f'{param}')

    bot.send_message(
        chat_id=update.message.chat_id,
        text=f'{param}')


def echo(bot, update):
    logging.info(update.message.text)
    bot.send_message(
        chat_id=update.message.chat_id,
        text=update.message.text)


def error(bot, update):
    logger.warning('Update "%s" caused error "%s"', bot, update.error)


def main():
    updater = Updater(token=settings.BOT_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("disclaimers", disclaimers))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("price", price, pass_args=True))
    dp.add_handler(CommandHandler("p", price, pass_args=True))
    dp.add_handler(CommandHandler("sources", sources))
    dp.add_handler(CommandHandler("start", start))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
