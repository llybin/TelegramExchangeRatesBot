from gettext import gettext

from telegram import ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler

from app.decorators import chat_language, register_update


@register_update
@chat_language
def help_callback(
    update: Update, context: CallbackContext, chat_info: dict, _: gettext
):
    text_to = _("*Commands*")

    text_to += "\n\n"
    text_to += _("/start - Start to enslave mankind")
    text_to += "\n"
    text_to += _("/tutorial - Tutorial, how to talk with me")
    text_to += "\n"
    text_to += _("/currencies - All currencies that I support")
    text_to += "\n"
    text_to += _("/feedback - If you have suggestions, text me")
    text_to += "\n"
    text_to += _("/p - Command for group chats, get exchange rate")
    text_to += "\n"
    text_to += _("/sources - Currency rates sources")
    text_to += "\n"
    text_to += _("/settings - Bot personal settings")
    text_to += "\n"
    text_to += _("/disclaimers - Disclaimers")
    text_to += "\n"
    text_to += _("/stop - Unsubscribe")

    text_to += "\n\n"
    text_to += _(
        "Don't have your localization? Any translation errors? Help fix it 👉 [poeditor.com](%(trans_link)s)"
    ) % {  # NOQA
        "trans_link": "https://poeditor.com/join/project/LLu8AztSPb"
    }

    text_to += "\n\n"
    text_to += (
        "🍕🍺 [patreon.com/ExchangeRatesBot](https://www.patreon.com/ExchangeRatesBot)"
    )

    update.message.reply_text(
        disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN, text=text_to
    )

    return ConversationHandler.END
