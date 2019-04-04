from gettext import gettext

import transaction
from telegram import ParseMode, ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext
from suite.database import Session

from app.callbacks.personal_settings.main import SettingsSteps
from app.decorators import register_update, chat_language
from app.keyboard import KeyboardSimpleClever
from app.models import Chat, Currency, ChatRequests
from app.logic import get_keyboard
from app.queries import have_last_request, get_keyboard_size


def onscreen_menu(update: Update, chat_info: dict, _: gettext):
    text_to = _('Here you can customize on-screen menu with a history requests.')

    update.message.reply_text(
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup([
            ['1. ' + _('Visibility')],
            ['2. ' + _('Size')],
            ['3. ' + _('Delete from a history requests')],
            ['↩️'],
        ]),
        text=text_to)


@register_update
@chat_language
def menu_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    onscreen_menu(update, chat_info, _)

    return SettingsSteps.onscreen_menu


@register_update
@chat_language
def visibility_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    if chat_info['is_show_keyboard']:
        text_to = _('On-screen menu below with a history requests *always shows* at the moment.')
    else:
        text_to = _('On-screen menu below with a history requests *never shows* at the moment.')

    text_to += '\n'

    text_to += _('You can choose. Show always on-screen menu below with a history requests or never show.')

    update.message.reply_text(
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup([
            ['1. ' + _('Always show')],
            ['2. ' + _('Never show')],
            ['↩️'],
        ]),
        text=text_to)

    return SettingsSteps.onscreen_menu_visibility


def visibility_set(update: Update, chat_info: dict, _: gettext, is_show_keyboard: bool):
    db_session = Session()
    chat = db_session.query(Chat).filter_by(id=update.message.chat_id).first()
    chat.is_show_keyboard = is_show_keyboard
    transaction.commit()

    if is_show_keyboard:
        text_to = _('On-screen menu below with a history requests will *always shows*.')
    else:
        text_to = _('On-screen menu below with a history requests will *never shows*.')

    update.message.reply_text(
        parse_mode=ParseMode.MARKDOWN,
        text=text_to)

    onscreen_menu(update, chat_info, _)


@register_update
@chat_language
def visibility_set_true_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    visibility_set(update, chat_info, _, True)

    return SettingsSteps.onscreen_menu


@register_update
@chat_language
def visibility_set_false_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    visibility_set(update, chat_info, _, False)

    return SettingsSteps.onscreen_menu


def get_keyboard_deletion(chat_id: int, _: gettext):
    keyboard = [['↩️', '🅾️ ' + _('Delete hidden'), '🆑 ' + _('Delete all')]]
    return ReplyKeyboardMarkup(keyboard + get_keyboard(chat_id, '❌ '))


@register_update
@chat_language
def edit_history_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    if have_last_request(update.message.chat_id):
        text_to = _('You can *delete* a request from a history requests.')

        keyboard = get_keyboard_deletion(update.message.chat_id, _)

        update.message.reply_text(
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard,
            text=text_to)

        return SettingsSteps.onscreen_menu_edit_history

    else:
        text_to = _('Your history requests is empty for deletion.')

        update.message.reply_text(text=text_to)

        return SettingsSteps.onscreen_menu


@register_update
@chat_language
def edit_history_delete_one_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    parts = update.message.text.split(' ')

    db_session = Session()

    from_currency = db_session.query(Currency).filter_by(
        code=parts[1]
    ).first()

    to_currency = db_session.query(Currency).filter_by(
        code=parts[2]
    ).first()

    if not from_currency or not to_currency:
        update.message.reply_text(text='🧐')
    else:
        db_session.query(ChatRequests).filter_by(
            chat_id=update.message.chat_id,
            from_currency=from_currency,
            to_currency=to_currency
        ).delete()
        transaction.commit()

        text_to = _('*%(first)s %(second)s* was deleted.') % {'first': parts[1], 'second': parts[2]}

        if have_last_request(update.message.chat_id):
            keyboard = get_keyboard_deletion(update.message.chat_id, _)

            update.message.reply_text(
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
                text=text_to)

            return SettingsSteps.onscreen_menu_edit_history

        else:
            update.message.reply_text(
                parse_mode=ParseMode.MARKDOWN,
                text=text_to)

            onscreen_menu(update, chat_info, _)

            return SettingsSteps.onscreen_menu


@register_update
@chat_language
def edit_history_delete_old_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    db_session = Session()

    size = get_keyboard_size(update.message.chat_id)

    subquery = db_session.query(ChatRequests.id).filter_by(
        chat_id=update.message.chat_id
    ).order_by(
        ChatRequests.times.desc()
    ).limit(size)

    db_session.query(ChatRequests).filter(
        ChatRequests.chat_id == update.message.chat_id,
        ChatRequests.id.notin_(subquery)
    ).delete(synchronize_session='fetch')

    transaction.commit()

    text_to = _('History of hidden requests has been cleared.')

    keyboard = get_keyboard_deletion(update.message.chat_id, _)

    update.message.reply_text(
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
        text=text_to)

    return SettingsSteps.onscreen_menu_edit_history


@register_update
@chat_language
def edit_history_delete_all_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    Session().query(ChatRequests).filter_by(
        chat_id=update.message.chat_id,
    ).delete()
    transaction.commit()

    text_to = _('History requests has been cleared fully.')

    keyboard = get_keyboard_deletion(update.message.chat_id, _)

    update.message.reply_text(
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
        text=text_to)

    onscreen_menu(update, chat_info, _)

    return SettingsSteps.onscreen_menu


KEYBOARD_SIZES = sorted(['2x1', '2x2', '2x3', '2x4', '3x1', '3x2', '3x3', '3x4'])


@register_update
@chat_language
def size_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    text_to = _('''%(keyboard_size)s - size of on-screen menu with a history requests at the moment.
You can customize the size. *width x height*''') % {'keyboard_size': chat_info['keyboard_size']}

    keyboard = KeyboardSimpleClever(['↩️'] + KEYBOARD_SIZES, 3).show()

    update.message.reply_text(
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup(keyboard),
        text=text_to)

    return SettingsSteps.onscreen_menu_size


@register_update
@chat_language
def set_size_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    if update.message.text not in KEYBOARD_SIZES:
        update.message.reply_text(text='🧐')
        return SettingsSteps.onscreen_menu_size

    text_to = _('%(keyboard_size)s - size of on-screen menu with a history requests was changed.') % {
        'keyboard_size': update.message.text}

    db_session = Session()
    db_session.query(Chat).filter_by(
        id=update.message.chat_id
    ).update({'keyboard_size': update.message.text})
    transaction.commit()

    update.message.reply_text(
        parse_mode=ParseMode.MARKDOWN,
        text=text_to)

    onscreen_menu(update, chat_info, _)

    return SettingsSteps.onscreen_menu
