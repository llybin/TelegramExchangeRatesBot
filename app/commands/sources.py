from telegram import ParseMode

from app.decorators import register_update


@register_update
def sources_command(bot, update, chat_info):
    bot.send_message(
        chat_id=update.message.chat_id,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
        text='''*Sources*

https://bitfinex.com - 15min (API limits😭)
https://bittrex.com - 1min
[https://bx.in.th](https://bx.in.th/ref/s9c3HU/) - 1min
https://fixer.io - 60min
https://openexchangerates.org - 60min''')
