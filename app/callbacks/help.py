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
        "Donations, bot is free and online since 01 July 2015:\n"
        "BTC: bc1q2efcwfs7f9pzncj5qv7xxrmntvempup6tr9vgg\n"
        "ETH: 0xAC8bA41C8BeB07398512A893e1f72E6B95D06694\n"
        "LTC: ltc1qqashju57hag8rppwu6u424ctyewp0ck6k7qyut"
    )

    update.message.reply_text(
        disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN, text=text_to
    )

    return ConversationHandler.END
