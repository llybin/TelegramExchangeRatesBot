import transaction
from telegram import ParseMode, ReplyKeyboardMarkup
from suite.database import Session

from app.commands.personal_settings.main import SettingsSteps, main_menu
from app.decorators import register_update, chat_language
from app.models import Currency, Chat
from app.keyboard import KeyboardSimpleClever
from app.queries import get_all_currencies


@register_update
@chat_language
def menu_command(bot, update, chat_info, _):
    text_to = _('*%(default_currency)s* is your default currency.\n'
                'You can set any currency by default, e.g. *EUR*. When you send only USD - will get *EUR USD*') % {
        'default_currency': chat_info['default_currency']}

    keyboard = KeyboardSimpleClever(['↩️'] + get_all_currencies(), 4).show()

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup(keyboard),
        text=text_to)

    return SettingsSteps.default_currency


@register_update
@chat_language
def set_command(bot, update, chat_info, _):
    currency_code = update.message.text.upper()

    db_session = Session()

    currency = db_session.query(Currency).filter_by(
        code=currency_code,
        is_active=True
    ).first()

    if not currency:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='🧐')
        return SettingsSteps.default_currency

    db_session.query(Chat).filter_by(
        id=update.message.chat_id
    ).update({'default_currency': currency_code})
    transaction.commit()

    text_to = _('*%(default_currency)s* is your default currency.') % {
        'default_currency': currency_code}

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        text=text_to)

    main_menu(bot, update, chat_info, _)

    return SettingsSteps.main
