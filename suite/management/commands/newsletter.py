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
        click.echo("Sending to %s" % chat.id)
        bot.send_message(
            chat_id=chat.id,
            disable_web_page_preview=True,
            disable_notification=True,
            parse_mode=ParseMode.MARKDOWN,
            text=text)
    except Exception as e:
        # logging.warning("Bot was blocked by the user %s", chat.id)
        # logging.warning("Bot was kicked by the user %s", chat.id)
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
    chats = Session.query(Chat.id).filter(
        # TODO: args
        Chat.is_subscribed == true(),
        # Chat.locale == 'en',
        # Chat.id > 0,
        # Chat.id == settings.DEVELOPER_USER_ID,
    ).all()

    # TODO: args
    text = """ What's new:

- Keyboard command has been moved under /settings
- Also you are able now to delete your history requests from keyboard in /settings I know, someone waited it for years 🥳
- Settings and help available from menu (three vertical dots) on mobiles
- I testing notifications and thinking how to create set up in interface
- Also wad added section donations in /help
- Have any problems or suggestions - write me /feedback
"""

    for chat in chats:
        send(bot, chat, text)
