import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from .constants import decimal_precision, decimal_scale


Base = declarative_base()


class Chat(Base):
    __tablename__ = 'chats'

    id = sa.Column(sa.BigInteger, primary_key=True)
    first_name = sa.Column(sa.Text, nullable=True)
    username = sa.Column(sa.Text, nullable=True)
    locale = sa.Column(sa.Text, default='en_US', nullable=False)
    is_subscribed = sa.Column(sa.Boolean, server_default='true', nullable=False)
    is_console_mode = sa.Column(sa.Boolean, server_default='true', nullable=False)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
    modified_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)

    requests = relationship('ChatRequests', backref='chat')
    requests_log = relationship('RequestsLog', backref='chat')


class Currency(Base):
    """
    https://en.wikipedia.org/wiki/ISO_4217

    See: migrations/versions/79fd60fe1187_currencies_chat_request_foreigns.py
    """
    __tablename__ = 'currencies'

    id = sa.Column(sa.Integer, primary_key=True)
    code = sa.Column(sa.Text, unique=True, nullable=False)
    name = sa.Column(sa.Text, nullable=False)
    is_active = sa.Column(sa.Boolean, index=True, nullable=False)
    is_crypto = sa.Column(sa.Boolean, index=True, nullable=False)


class ChatRequests(Base):
    __tablename__ = 'chat_requests'

    id = sa.Column(sa.Integer, primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey('chats.id'), nullable=False)
    from_currency_id = sa.Column(sa.Integer, sa.ForeignKey('currencies.id'), nullable=False)
    to_currency_id = sa.Column(sa.Integer, sa.ForeignKey('currencies.id'), nullable=False)
    times = sa.Column(sa.Integer, server_default='0', nullable=False)
    modified_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)

    from_currency = relationship('Currency', foreign_keys=[from_currency_id])
    to_currency = relationship('Currency', foreign_keys=[to_currency_id])


class RequestsLog(Base):
    __tablename__ = 'requests_log'

    id = sa.Column(sa.Integer, primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey('chats.id'), nullable=False)
    message = sa.Column(sa.Text, nullable=False)
    tag = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)


class Exchange(Base):
    __tablename__ = 'exchanges'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, nullable=False, index=True)
    is_active = sa.Column(sa.Boolean, nullable=False)

    rates = relationship('Rate', backref='exchange')


class Rate(Base):
    __tablename__ = 'rates'
    __table_args__ = (sa.UniqueConstraint('exchange_id', 'from_currency_id', 'to_currency_id'),)

    id = sa.Column(sa.Integer, primary_key=True)
    exchange_id = sa.Column(sa.Integer, sa.ForeignKey('exchanges.id'), nullable=False)
    from_currency_id = sa.Column(sa.Integer, sa.ForeignKey('currencies.id'), nullable=False)
    to_currency_id = sa.Column(sa.Integer, sa.ForeignKey('currencies.id'), nullable=False)
    rate = sa.Column(sa.Numeric(decimal_precision, decimal_scale), nullable=False)
    rate_open = sa.Column(sa.Numeric(decimal_precision, decimal_scale), nullable=False)
    low24h = sa.Column(sa.Numeric(decimal_precision, decimal_scale), nullable=True)
    high24h = sa.Column(sa.Numeric(decimal_precision, decimal_scale), nullable=True)
    volume24h = sa.Column(sa.Numeric(decimal_precision, decimal_scale), nullable=True)
    last_trade_at = sa.Column(sa.TIMESTAMP, nullable=False)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
    modified_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)

    from_currency = relationship('Currency', foreign_keys=[from_currency_id])
    to_currency = relationship('Currency', foreign_keys=[to_currency_id])


# class Event(db):
#     __tablename__ = 'events'
#     # __table_args__ = (UniqueConstraint('chat_id', 'event', name='chat_id_events'),)
#
#     id = sa.Column(sa.Integer, primary_key=True)
#     chat_id = sa.Column(sa.BigInteger, nullable=False, index=True)
#     event = sa.Column(sa.Text, nullable=False, index=True)
#     created = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
#
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
#     updated = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
