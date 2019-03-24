from datetime import datetime
import logging

import sentry_sdk
import transaction
from pyramid_sqlalchemy import init_sqlalchemy, Session
from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    ReplyKeyboardRemove,
    ParseMode,
)
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
from .converter.formatter import FormatPriceRequestResult, InlineFormatPriceRequestResult
from .converter.converter import convert
from .converter.exceptions import ConverterException
from .logic import get_keyboard, start_parse
from .models import Chat, Currency, ChatRequests
from .parsers.exceptions import ValidationException
from .exceptions import EmptyPriceRequestException
from .tasks import write_request_log, send_feedback, update_chat_request
from .parsers.base import PriceRequest


def tutorial(bot, update, _):
    bot.send_message(
        chat_id=update.message.chat_id,
        text=_('I am bot. I will help you to know a current exchange rates.'))

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
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
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
        text=_('Inline mode is available. See how to use [here](%(link)s).') % {
            'link': 'https://telegram.org/blog/inline-bots'})

    bot.send_message(
        chat_id=update.message.chat_id,
        reply_markup=get_keyboard(update.message.chat_id),
        text=_('Also take a look here 👉 /help'))


@register_update
@chat_language
def start_command(bot, update, chat_info, _):
    if update.message.chat.type == 'private':
        name = update.message.from_user.first_name
    else:
        name = _('humans')

    bot.send_message(
        chat_id=update.message.chat_id,
        text=_('Hello, %(name)s!') % {'name': name})

    if chat_info['created']:
        tutorial(bot, update, _)

    else:
        if not chat_info['is_subscribed']:
            Session().query(Chat).filter_by(
                id=update.message.chat_id
            ).update({'is_subscribed': True})
            transaction.commit()

        bot.send_message(
            chat_id=update.message.chat_id,
            reply_markup=get_keyboard(update.message.chat_id),
            text=_('Have any question how to talk with me? 👉 /tutorial'))


@register_update
@chat_language
def tutorial_command(bot, update, chat_info, _):
    tutorial(bot, update, _)


@register_update
@chat_language
def stop_command(bot, update, chat_info, _):
    if chat_info['is_subscribed']:
        Session().query(Chat).filter_by(
            id=update.message.chat_id
        ).update({'is_subscribed': False})
        transaction.commit()

    bot.send_message(
        chat_id=update.message.chat_id,
        text=_("You're unsubscribed. You always can subscribe again 👉 /start")
    )


@register_update
@chat_language
def help_command(bot, update, chat_info, _):
    text_to = _('*Commands*')

    text_to += '\n\n'
    text_to += _('/start - Start to enslave mankind')
    text_to += '\n'
    text_to += _('/tutorial - Tutorial, how to talk with me')
    text_to += '\n'
    text_to += _('/currencies - All currencies that I support')
    text_to += '\n'
    text_to += _('/feedback - If you have suggestions, text me')
    text_to += '\n'
    text_to += _('/keyboard - Hide / show a keyboard with request history')
    text_to += '\n'
    text_to += _('/p - Command for group chats, get exchange rate')
    text_to += '\n'
    text_to += _('/sources - Currency rates sources')
    text_to += '\n'
    text_to += _('/disclaimers - Disclaimers')
    text_to += '\n'
    text_to += _('/stop - Unsubscribe')

    text_to += '\n\n'
    text_to += _("Don't have your localization? Any translation errors? Help fix it 👉 [poeditor.com](%(trans_link)s)") % {
        'trans_link': 'https://poeditor.com/join/project/LLu8AztSPb'}

    text_to += '\n\n'
    text_to += '''SSD cloud servers in regions: New York, San Francisco, Amsterdam, Singapore, London, Frankfurt, Toronto, Bangalore.

Sign up using [link](%(link)s) and receive $100. From $5 per month: 1GB / 1 CPU / 25GB SSD Disk.''' % {'link': 'https://m.do.co/c/ba04a478e10d'}  # NOQA

    bot.send_message(
        chat_id=update.message.chat_id,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
        text=text_to)


@register_update
def sources_command(bot, update, chat_info):
    bot.send_message(
        chat_id=update.message.chat_id,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
        text='''*Sources*

https://bitfinex.com - 15min (API limits😭)
https://bittrex.com - 1min
https://fixer.io - 60min
https://openexchangerates.org - 60min''')


@register_update
@chat_language
def keyboard_command(bot, update, chat_info, _):
    chat_id = update.message.chat_id

    if chat_id < 0:
        update.message.reply_text(_('The command is not available for group chats'))
        return

    db_session = Session()
    chat = db_session.query(Chat).filter_by(id=chat_id).first()

    if chat.is_console_mode:
        chat.is_console_mode = False
        reply_markup = get_keyboard(chat_id)
        text_to = _('Keyboard is shown.')
    else:
        chat.is_console_mode = True
        reply_markup = ReplyKeyboardRemove()
        text_to = _('Keyboard is hidden.')

    transaction.commit()

    bot.send_message(
        chat_id=update.message.chat_id,
        reply_markup=reply_markup,
        text=text_to)


@register_update
@chat_language
def feedback_command(bot, update, chat_info, _):
    chat_id = update.message.chat_id

    if chat_id < 0:
        update.message.reply_text(_("The command is not available for group chats"))
        return

    bot.send_message(
        chat_id=update.message.chat_id,
        reply_markup=ReplyKeyboardRemove(),
        text=_('What do you want to tell? Or nothing?') + ' /nothing')

    return 1

@register_update
@chat_language
def send_feedback_command(bot, update, chat_info, _):
    text_to = _('Message sent, thank you.')

    bot.send_message(
        chat_id=update.message.chat_id,
        reply_markup=get_keyboard(update.message.chat_id),
        text=text_to)

    send_feedback(
        update.message.chat.id,
        update.message.from_user.first_name,
        update.message.from_user.username,
        update.message.text
    )

    return ConversationHandler.END


@register_update
@chat_language
def cancel_command(bot, update, chat_info, _):
    bot.send_message(
        chat_id=update.message.chat_id,
        reply_markup=get_keyboard(update.message.chat_id),
        text='👌')

    return ConversationHandler.END


@register_update
def currencies_command(bot, update, chat_info):
    text_to = '\n'.join([f'{code} - {name}' for code, name in Session().query(
        Currency.code, Currency.name).filter_by(is_active=True).order_by(Currency.name)])

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        text=text_to)


@register_update
@chat_language
def settings_commands(bot, update, chat_info, _):
    # locale
    # default_currency
    # default_currency_position
    update.message.reply_text(
        text='https://github.com/llybin/TelegramExchangeRatesBot/issues/11')


@register_update
@chat_language
def disclaimers_command(bot, update, chat_info, _):
    bot.send_message(
        chat_id=update.message.chat_id,
        text=_('Data is provided by financial exchanges and may be delayed '
               'as specified by financial exchanges or our data providers. '
               'Bot does not verify any data and disclaims any obligation '
               'to do so. Bot cannot guarantee the accuracy of the exchange '
               'rates displayed. You should confirm current rates before making '
               'any transactions that could be affected by changes in '
               'the exchange rates.'))


def price(bot, update, text, chat_info, _):
    tag = ''
    try:
        if not text:
            raise EmptyPriceRequestException

        price_request = start_parse(
            text,
            chat_info['chat_id'],
            chat_info['locale'],
            chat_info['default_currency'],
            chat_info['default_currency_position']
        )

        tag = price_request.parser_name

        logging.info(f'price_request: {text} -> {price_request}')

        price_request_result = convert(price_request)

        logging.info(f'price_request: {price_request_result}')

        text_to = FormatPriceRequestResult(price_request_result, chat_info['locale']).get()

        update_chat_request(
            chat_id=update.message.chat_id,
            currency=price_request.currency,
            to_currency=price_request.to_currency
        )

        bot.send_message(
            chat_id=update.message.chat_id,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_keyboard(update.message.chat_id),
            text=text_to)

    except EmptyPriceRequestException:
        if chat_info['chat_id'] > 0:
            update.message.reply_text(
                text=_('The message must contain currencies or amounts 👉 /tutorial'))

    except ValidationException:
        if chat_info['chat_id'] > 0:
            update.message.reply_text(
                text=_("I don't understand you 😞 Take a look here 👉 /help"))

    except ConverterException:
        if chat_info['chat_id'] > 0:
            update.message.reply_text(
                text=_("I understood that you asked, but at the moment "
                       "I don't have actual exchange rates for your request. "
                       "Try later. Sorry. 😭"))

    finally:
        if len(text) <= settings.MAX_LEN_MSG_REQUESTS_LOG:
            write_request_log.delay(
                chat_id=update.message.chat_id,
                msg=text,
                created_at=datetime.now(),
                tag=tag
            )


@register_update
@chat_language
def price_command(bot, update, args, chat_info, _):
    text = ''.join(args)
    price(bot, update, text, chat_info, _)


@register_update
@chat_language
def message_command(bot, update, chat_info, _):
    if not update.message:
        return

    price(bot, update, update.message.text, chat_info, _)


@register_update
@chat_language
def empty_command(bot, update, chat_info, _):
    price(bot, update, update.message.text[1:], chat_info, _)


@register_update
def inline_query(bot, update, chat_info):
    query = update.inline_query.query

    if not query:
        logging.info('inline_request empty query')

        last_requests = Session.query(ChatRequests).filter_by(
            chat_id=update.effective_user.id
        ).order_by(
            ChatRequests.times.desc()
        ).limit(9).all()

        results = []

        for r in last_requests:
            price_request_result = convert(PriceRequest(
                amount=None,
                currency=r.from_currency.code,
                to_currency=r.to_currency.code,
                parser_name='InlineQuery',
            ))

            title = InlineFormatPriceRequestResult(
                price_request_result, chat_info['locale']).get()
            text_to = FormatPriceRequestResult(
                price_request_result, chat_info['locale']).get()

            ident = f'{r.from_currency.code}{r.to_currency.code}' \
                f'{price_request_result.rate}{price_request_result.last_trade_at}'

            results.append(
                InlineQueryResultArticle(
                    id=ident,
                    title=title,
                    input_message_content=InputTextMessageContent(
                        text_to,
                        parse_mode=ParseMode.MARKDOWN
                    )
                )
            )
        write_request_log.delay(
            chat_id=update.effective_user.id,
            msg='',
            created_at=datetime.now(),
            tag='Inline'
        )
        # TODO: increase counter what was chosen if it possible
    else:
        try:
            price_request = start_parse(
                query,
                chat_info['chat_id'],
                chat_info['locale'],
                chat_info['default_currency'],
                chat_info['default_currency_position']
            )

            logging.info(f'inline_request: {query} -> {price_request}')

            price_request_result = convert(price_request)

            logging.info(f'inline_request: {price_request_result}')

            title = InlineFormatPriceRequestResult(
                price_request_result, chat_info['locale']).get()
            text_to = FormatPriceRequestResult(
                price_request_result, chat_info['locale']).get()

            ident = f'{price_request.currency}{price_request.to_currency}' \
                f'{price_request_result.rate}{price_request_result.last_trade_at}'

            results = [
                InlineQueryResultArticle(
                    id=ident,
                    title=title,
                    input_message_content=InputTextMessageContent(
                        text_to,
                        parse_mode=ParseMode.MARKDOWN
                    )
                )
            ]

            update_chat_request.delay(
                chat_id=update.effective_user.id,
                currency=price_request.currency,
                to_currency=price_request.to_currency
            )

        except (ValidationException, ConverterException) as e:
            logging.info(f'inline_request unrecognized: {query}')
            results = []

        finally:
            if len(query) <= settings.MAX_LEN_MSG_REQUESTS_LOG:
                write_request_log.delay(
                    chat_id=update.effective_user.id,
                    msg=query,
                    created_at=datetime.now(),
                    tag='Inline'
                )

    update.inline_query.answer(results)


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
    dp.add_handler(CommandHandler("settings", settings_commands))
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
