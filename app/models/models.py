import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .db import Base


class Chat(Base):
    __tablename__ = 'chats'

    id = sa.Column(sa.BigInteger, primary_key=True)
    first_name = sa.Column(sa.Text, nullable=True)
    username = sa.Column(sa.Text, nullable=True)
    locale = sa.Column(sa.Text, default='en_US')
    is_subscribed = sa.Column(sa.Boolean, server_default='true')
    is_console_mode = sa.Column(sa.Boolean, server_default='true')
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now())
    modified_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now())

    requests = relationship('ChatRequests', backref='chat')
    requests_log = relationship('RequestsLog', backref='chat')


class Currency(Base):
    __tablename__ = 'currencies'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, unique=True)


class ChatRequests(Base):
    __tablename__ = 'chat_requests'

    id = sa.Column(sa.Integer, primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey('chats.id'))
    first_currency_id = sa.Column(sa.Integer, sa.ForeignKey('currencies.id'))
    second_currency_id = sa.Column(sa.Integer, sa.ForeignKey('currencies.id'))
    times = sa.Column(sa.Integer, server_default='0')
    modified_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now())

    first_currency = relationship('Currency', foreign_keys=[first_currency_id])
    second_currency = relationship('Currency', foreign_keys=[second_currency_id])


class RequestsLog(Base):
    __tablename__ = 'requests_log'

    id = sa.Column(sa.Integer, primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey('chats.id'))
    message = sa.Column(sa.Text)
    tag = sa.Column(sa.Text)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now())


# class Event(db):
#     __tablename__ = 'events'
#     # __table_args__ = (UniqueConstraint('chat_id', 'event', name='chat_id_events'),)
#
#     id = sa.Column(sa.Integer, primary_key=True)
#     chat_id = sa.Column(sa.BigInteger, nullable=False, index=True)
#     event = sa.Column(sa.Text, nullable=False, index=True)
#     created = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)


# class Notification(db):
#     __tablename__ = 'notifications'
#     # __table_args__ = (UniqueConstraint('chat_id', 'currencies', 'clause'),)
#
#     id = sa.Column(sa.Integer, primary_key=True)
#     chat_id = sa.Column(sa.BigInteger, nullable=False, index=True)
#     currencies = sa.Column(sa.Text, nullable=False)
#     clause = sa.Column(sa.Enum('more', 'less', 'diff', 'percent', name='notification_clause'), nullable=False)
#     value = sa.Column(sa.Numeric(14, 6), nullable=False)
#     last_rate = sa.Column(sa.Numeric(14, 6), nullable=False)
#     is_active = sa.Column(sa.Boolean(), default=True, nullable=False)
#     created = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
#     updated = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.current_timestamp(), nullable=False)
#
#
# class Rate(db):
#     __tablename__ = 'rates'
#
#     currency = sa.Column(sa.CHAR(3), primary_key=True)
#     rate_open = sa.Column(sa.Numeric(14, 6), nullable=False)
#     rate = sa.Column(sa.Numeric(14, 6), nullable=False)
#     source = sa.Column(sa.Text, nullable=False)
#     weight = sa.Column(sa.Integer, server_default='0', index=True, nullable=False)
#     last_trade_at = sa.Column(sa.TIMESTAMP, nullable=False)
#     created = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
#     updated = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.current_timestamp(), nullable=False)
