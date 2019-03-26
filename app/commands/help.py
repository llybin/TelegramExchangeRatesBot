from telegram import ParseMode

from app.decorators import register_update, chat_language


@register_update
@chat_language
def help_command(bot, update, chat_info, _):
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
    text_to += _('/keyboard - Hide / show a keyboard with request history')
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
    text_to += _('[ExchangeRatesBotNews](%(link)s) - subscribe to channel, stay tuned news.') % {
        'link': 'https://t.me/ExchangeRatesBotNews'}

    text_to += '\n\n'
    text_to += '''SSD cloud servers in regions: New York, San Francisco, Amsterdam, Singapore, London, Frankfurt, Toronto, Bangalore.

Sign up using [link](%(link)s) and receive $100. From $5 per month: 1GB / 1 CPU / 25GB SSD Disk.''' % {'link': 'https://m.do.co/c/ba04a478e10d'}  # NOQA

    bot.send_message(
        chat_id=update.message.chat_id,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
        text=text_to)
