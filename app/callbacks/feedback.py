from gettext import gettext

from telegram import ReplyKeyboardRemove, Update, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackContext

from app.decorators import register_update, chat_language
from app.logic import get_keyboard
from app.tasks import send_feedback


@register_update
@chat_language
def feedback_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    chat_id = update.message.chat_id

    if chat_id < 0:
        update.message.reply_text(_("The command is not available for group chats"))
        return

    update.message.reply_text(
        reply_markup=ReplyKeyboardRemove(),
        text=_('What do you want to tell? Or nothing?') + ' /nothing')

    return 1


@register_update
@chat_language
def send_feedback_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    text_to = _('Message sent, thank you.')

    update.message.reply_text(
        reply_markup=ReplyKeyboardMarkup(get_keyboard(update.message.chat_id)),
        text=text_to)

    send_feedback.delay(
        update.message.chat.id,
        update.message.from_user.first_name,
        update.message.from_user.username,
        update.message.text
    )

    return ConversationHandler.END
