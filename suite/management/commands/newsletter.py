import time

import click
import telegram
import transaction
from telegram import ParseMode
from sqlalchemy import create_engine
from sqlalchemy.sql import true

from suite.database import Session, init_sqlalchemy
from suite.conf import settings

from app.models import Chat


def send(bot, chat, text):
    try:
        click.echo("Sending to %s, %s" % (chat.first_name, chat.id))
        bot.send_message(
            chat_id=chat.id,
            disable_web_page_preview=True,
            disable_notification=True,
            parse_mode=ParseMode.MARKDOWN,
            text=text)
    except Exception as e:
        # logging.warning("Bot was blocked by the user %s, %s", chat.first_name, chat.id)
        # logging.warning("Bot was kicked by the user %s, %s", chat.first_name, chat.id)
        click.echo(str(e))

        Session().query(Chat).filter_by(
            id=chat.id
        ).update({'is_subscribed': False})
        transaction.commit()


@click.command(help="Delivery newsletter.")
def newsletter():
    click.echo('Will start delivery now...')
    time.sleep(5)

    bot = telegram.Bot(settings.BOT_TOKEN)

    db_engine = create_engine(settings.DATABASE['url'])
    init_sqlalchemy(db_engine)

    # TODO: iterate
    chats = Session.query(Chat.id, Chat.first_name).filter(
        # TODO: args
        Chat.is_subscribed == true(),
        # Chat.locale == 'en',
        # Chat.id > 0,
        Chat.id == settings.DEVELOPER_USER_ID,
    ).all()

    # TODO: args
    text = """ What's new:

- added BTT - BitConnect currency
- added [bx.in.th](https://bx.in.th/ref/s9c3HU/) exchange for THB crypto pairs
- added sp-today.com exchange for SYP pairs
- added Indonesia locale, thanks :)
- added Uzbekistan locale, thanks :)
- other translations were updated, thanks :)
- /settings command, only for private chats: language, default currency settings
- fixes and improvements"""

    for chat in chats:
        send(bot, chat, text)
