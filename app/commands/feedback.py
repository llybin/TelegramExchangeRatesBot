from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from app.decorators import register_update, chat_language
from app.logic import get_keyboard
from app.tasks import send_feedback


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
