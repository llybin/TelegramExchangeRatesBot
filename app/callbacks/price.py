import logging
from datetime import datetime
from gettext import gettext

from telegram import ParseMode, InlineQueryResultArticle, InputTextMessageContent, Update, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackContext
from suite.conf import settings

from app.converter.converter import convert
from app.converter.exceptions import ConverterException, NoRatesException
from app.formatter.formatter import FormatPriceRequestResult, InlineFormatPriceRequestResult
from app.decorators import register_update, chat_language
from app.exceptions import EmptyPriceRequestException
from app.logic import start_parse, get_keyboard
from app.parsers.base import PriceRequest
from app.parsers.exceptions import ValidationException
from app.tasks import update_chat_request, write_request_log
from app.queries import get_last_request


def price(update: Update, text: str, chat_info: dict, _: gettext):
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

        update.message.reply_text(
            disable_web_page_preview=True,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=ReplyKeyboardMarkup(get_keyboard(update.message.chat_id)),
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
def price_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    text = ''.join(context.args)
    # usd@ExchangeRatesBot
    text = text.split(update.message.bot.name)[0]

    price(update, text, chat_info, _)

    return ConversationHandler.END


@register_update
@chat_language
def message_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    if not update.message:
        return

    price(update, update.message.text, chat_info, _)

    return ConversationHandler.END


@register_update
@chat_language
def on_slash_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    text = update.message.text[1:]
    # /usd@ExchangeRatesBot
    text = text.split(update.message.bot.name)[0]

    price(update, text, chat_info, _)

    return ConversationHandler.END


@register_update
def inline_query_callback(update: Update, context: CallbackContext, chat_info: dict):
    query = update.inline_query.query

    if not query:
        logging.info('inline_request empty query')

        last_requests = get_last_request(update.effective_user.id)

        results = []

        for r in last_requests:
            if not r.from_currency.is_active or not r.to_currency.is_active:
                continue

            try:
                price_request_result = convert(PriceRequest(
                    amount=None,
                    currency=r.from_currency.code,
                    to_currency=r.to_currency.code,
                    parser_name='InlineQuery',
                ))
            except NoRatesException:
                continue

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
                        disable_web_page_preview=True,
                        parse_mode=ParseMode.MARKDOWN
                    )
                )
            )
        write_request_log.delay(
            chat_id=update.effective_user.id,
            msg='',
            created_at=datetime.now(),
            tag='Inline All'
        )
        # TODO: increase counter what was chosen if it possible
    else:
        tag = ''
        try:
            price_request = start_parse(
                query,
                chat_info['chat_id'],
                chat_info['locale'],
                chat_info['default_currency'],
                chat_info['default_currency_position']
            )

            logging.info(f'inline_request: {query} -> {price_request}')

            tag = price_request.parser_name

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
                        disable_web_page_preview=True,
                        parse_mode=ParseMode.MARKDOWN
                    )
                )
            ]

            update_chat_request.delay(
                chat_id=update.effective_user.id,
                currency=price_request.currency,
                to_currency=price_request.to_currency
            )

        except (ValidationException, ConverterException):
            logging.info(f'inline_request unrecognized: {query}')
            results = []

        finally:
            if len(query) <= settings.MAX_LEN_MSG_REQUESTS_LOG:
                write_request_log.delay(
                    chat_id=update.effective_user.id,
                    msg=query,
                    created_at=datetime.now(),
                    tag=f'Inline {tag}' if tag else 'Inline'
                )

    update.inline_query.answer(results)
