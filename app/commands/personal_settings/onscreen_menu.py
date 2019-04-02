import transaction
from telegram import ParseMode, ReplyKeyboardMarkup
from suite.database import Session

from app.commands.personal_settings.main import SettingsSteps
from app.decorators import register_update, chat_language
from app.models import Chat, Currency, ChatRequests
from app.logic import get_keyboard


def onscreen_menu(bot, update, chat_info, _):
    text_to = _('Here you can customize on-screen menu with a history requests.')

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup([
            [_('1: Visibility')],
            [_('2: Delete request from a history')],
            ['↩️'],
        ]),
        text=text_to)


@register_update
@chat_language
def menu_command(bot, update, chat_info, _):
    onscreen_menu(bot, update, chat_info, _)

    return SettingsSteps.onscreen_menu


@register_update
@chat_language
def visibility_command(bot, update, chat_info, _):
    if chat_info['is_show_keyboard']:
        text_to = _('On-screen menu below with a history requests *always shows* at the moment.')
    else:
        text_to = _('On-screen menu below with a history requests *never shows* at the moment.')

    text_to += '\n'

    text_to += _('You can choose. Show always on-screen menu below with a history requests or never show.')

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup([
            [_('1: Always show')],
            [_('2: Never show')],
            ['↩️'],
        ]),
        text=text_to)

    return SettingsSteps.onscreen_menu_visibility


@register_update
@chat_language
def visibility_set_true_command(bot, update, chat_info, _):
    db_session = Session()
    chat = db_session.query(Chat).filter_by(id=update.message.chat_id).first()
    chat.is_show_keyboard = True
    transaction.commit()

    text_to = _('On-screen menu below with a history requests will *always shows*.')

    bot.send_message(
        chat_id=update.message.chat_id,
        text=text_to)

    onscreen_menu(bot, update, chat_info, _)

    return SettingsSteps.onscreen_menu


@register_update
@chat_language
def visibility_set_false_command(bot, update, chat_info, _):
    db_session = Session()
    chat = db_session.query(Chat).filter_by(id=update.message.chat_id).first()
    chat.is_show_keyboard = False
    transaction.commit()

    text_to = _('On-screen menu below with a history requests will *never shows*.')

    bot.send_message(
        chat_id=update.message.chat_id,
        text=text_to)

    onscreen_menu(bot, update, chat_info, _)

    return SettingsSteps.onscreen_menu


@register_update
@chat_language
def edit_history_command(bot, update, chat_info, _):
    # TODO: move from get_keyboard query for check to queries and use it
    if get_keyboard(update.message.chat_id):
        text_to = _('You can *delete* a request from a history requests.')

        keyboard = get_keyboard(
            update.message.chat_id,
            ['↩️', '🅾️ ' + _('Delete old'), '🆑 ' + _('Delete all')],
            '❌ '
        )

        bot.send_message(
            chat_id=update.message.chat_id,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard,
            text=text_to)

        return SettingsSteps.onscreen_menu_edit_history

    else:
        text_to = _('Your history requests is empty for deletion.')

        bot.send_message(
            chat_id=update.message.chat_id,
            text=text_to)

        return SettingsSteps.onscreen_menu


def get_keyboard_deletion(chat_id: int, _):
    return get_keyboard(
        chat_id,
        ['↩️', '🅾️ ' + _('Delete old'), '🆑 ' + _('Delete all')],
        '❌ '
    )


@register_update
@chat_language
def edit_history_delete_one_command(bot, update, chat_info, _):
    parts = update.message.text.split(' ')

    db_session = Session()

    from_currency = db_session.query(Currency).filter_by(
        code=parts[1]
    ).first()

    to_currency = db_session.query(Currency).filter_by(
        code=parts[2]
    ).first()

    if not from_currency or not to_currency:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='🧐')
    else:
        db_session.query(ChatRequests).filter_by(
            chat_id=update.message.chat_id,
            from_currency=from_currency,
            to_currency=to_currency
        ).delete()
        transaction.commit()

        text_to = _('*%(first)s %(second)s* was deleted.') % {'first': parts[1], 'second': parts[2]}

        # TODO: move from get_keyboard query for check to queries and use it
        if get_keyboard(update.message.chat_id):
            keyboard = get_keyboard_deletion(update.message.chat_id, _)

            bot.send_message(
                chat_id=update.message.chat_id,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
                text=text_to)

            return SettingsSteps.onscreen_menu_edit_history

        else:
            bot.send_message(
                chat_id=update.message.chat_id,
                parse_mode=ParseMode.MARKDOWN,
                text=text_to)

            onscreen_menu(bot, update, chat_info, _)

            return SettingsSteps.onscreen_menu


@register_update
@chat_language
def edit_history_delete_old_command(bot, update, chat_info, _):
    db_session = Session()

    subquery = db_session.query(ChatRequests.id).filter_by(
        chat_id=update.message.chat_id
    ).order_by(
        ChatRequests.times.desc()
    ).limit(9)

    db_session.query(ChatRequests).filter(
        ChatRequests.chat_id == update.message.chat_id,
        ChatRequests.id.notin_(subquery)
    ).delete(synchronize_session='fetch')

    transaction.commit()

    text_to = _('History of old requests has been cleared.')

    keyboard = get_keyboard_deletion(update.message.chat_id, _)

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
        text=text_to)

    return SettingsSteps.onscreen_menu_edit_history


@register_update
@chat_language
def edit_history_delete_all_command(bot, update, chat_info, _):
    Session().query(ChatRequests).filter_by(
        chat_id=update.message.chat_id,
    ).delete()
    transaction.commit()

    text_to = _('History requests has been cleared fully.')

    keyboard = get_keyboard_deletion(update.message.chat_id, _)

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
        text=text_to)

    onscreen_menu(bot, update, chat_info, _)

    return SettingsSteps.onscreen_menu
