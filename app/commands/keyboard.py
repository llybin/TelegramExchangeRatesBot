import transaction
from pyramid_sqlalchemy import Session
from telegram import ReplyKeyboardRemove

from app.decorators import register_update, chat_language
from app.logic import get_keyboard
from app.models import Chat


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
