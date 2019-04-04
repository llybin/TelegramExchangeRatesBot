import time

import click
from sqlalchemy import create_engine

from suite.database import Session, init_sqlalchemy
from suite.conf import settings

from app.models import Chat
from app.tasks_notifications import send_notification


@click.command(help="Delivery newsletter.")
@click.argument('file_text')
@click.option("--for-all",
              is_flag=True,
              help="Send for all, by default only for developer.")
def newsletter(file_text, for_all):
    try:
        text = open(file_text, 'r').read()
    except FileNotFoundError:
        click.echo('File not found.')
        return

    if for_all:
        click.echo('Will start delivery for all...')
        time.sleep(5)

    db_engine = create_engine(settings.DATABASE['url'])
    init_sqlalchemy(db_engine)

    chats = Session.query(
        Chat.id
    ).filter_by(
        is_subscribed=True
    ).order_by(
        Chat.id
    )

    if not for_all:
        chats = chats.filter_by(id=settings.DEVELOPER_USER_ID)

    for chat in chats.yield_per(100):
        send_notification.delay(chat.id, text)
