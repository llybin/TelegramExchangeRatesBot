from gettext import gettext

from app.decorators import chat_language, register_update
from app.logic import get_keyboard
from telegram import ParseMode, ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler


def tutorial(update, _):
    text_to = _("I am bot. I will help you to know a current exchange rates.")
    text_to += "\n\n"
    text_to += _(
        """Send me a message like this:
*BTC USD* - to see the current exchange rate for pair
*100 USD EUR* - to convert the amount from 100 USD to EUR"""
    )
    text_to += "\n\n"
    text_to += _("Just text me message in private chat.")
    text_to += "\n\n"
    text_to += _(
        "In group chats use commands like this: 👉 /p USD EUR 👈 or simply /USDEUR"
    )
    text_to += "\n\n"
    text_to += _("Inline mode is available. See how to use [here](%(link)s).") % {
        "link": "https://telegram.org/blog/inline-bots"
    }
    text_to += "\n\n"
    text_to += _("Also take a look here 👉 /help")

    keyboard = get_keyboard(update.message.chat_id)

    update.message.reply_text(
        reply_markup=ReplyKeyboardMarkup(keyboard) if keyboard else None,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        text=text_to,
    )


@register_update
@chat_language
def tutorial_callback(
    update: Update, context: CallbackContext, chat_info: dict, _: gettext
):
    tutorial(update, _)
    return ConversationHandler.END
