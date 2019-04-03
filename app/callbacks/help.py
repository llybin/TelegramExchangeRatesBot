from gettext import gettext

from telegram import ParseMode, Update
from telegram.ext import ConversationHandler, CallbackContext

from app.decorators import register_update, chat_language


@register_update
@chat_language
def help_callback(update: Update, context: CallbackContext, chat_info: dict, _: gettext):
    text_to = _('*Commands*')

    text_to += '\n\n'
    text_to += _('/start - Start to enslave mankind')
    text_to += '\n'
    text_to += _('/tutorial - Tutorial, how to talk with me')
    text_to += '\n'
    text_to += _('/currencies - All currencies that I support')
    text_to += '\n'
    text_to += _('/feedback - If you have suggestions, text me')
    text_to += '\n'
    text_to += _('/p - Command for group chats, get exchange rate')
    text_to += '\n'
    text_to += _('/sources - Currency rates sources')
    text_to += '\n'
    text_to += _('/settings - Bot personal settings')
    text_to += '\n'
    text_to += _('/disclaimers - Disclaimers')
    text_to += '\n'
    text_to += _('/stop - Unsubscribe')

    text_to += '\n\n'
    text_to += _("Don't have your localization? Any translation errors? Help fix it 👉 [poeditor.com](%(trans_link)s)") % {  # NOQA
        'trans_link': 'https://poeditor.com/join/project/LLu8AztSPb'}

    text_to += '\n\n'

    text_to += '*Donations*'

    text_to += '\n\n'

    text_to += '''[PayPal](https://paypal.me/lybin)

[Yandex.Money](money.yandex.ru/to/41001252061112)

*WebMoney*: R152423429164, Z282158953669, X159713546826, E378035973063

*Bitcoin (BTC)*: 1GJZ36ahmApeX6RuuDGhi7t8qzBprJ9sQc

*Bitcoin Cash (BCH)*: qznahv6kprwsfrq6sr2ehcfuf259yjcmqgk7fuz976

*Ether (ETH)*: 0x56b2144aFE4564852409B302B29d7B6B2797Cf2D

*BurstCoin (BURST)*: BURST-BTKF-8WT9-L98N-98JH2

*Stellar (XLM)*: GBP332VIMDGSPJOOCXPCAJSS3EDBTYLJ4IVY42674F436ZXCVKVJWJY4
'''

    update.message.reply_text(
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
        text=text_to)

    return ConversationHandler.END
