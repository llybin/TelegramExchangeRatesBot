import sqlalchemy as sa
from pyramid_sqlalchemy import BaseObject, Session
from sqlalchemy import orm

from .cache import region
from suite.conf import settings

from .constants import decimal_precision, decimal_scale


class Chat(BaseObject):
    __tablename__ = 'chats'

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=False)
    first_name = sa.Column(sa.Text, nullable=True)
    username = sa.Column(sa.Text, nullable=True)
    locale = sa.Column(sa.Text, default=settings.LANGUAGE_CODE, nullable=False)
    is_subscribed = sa.Column(sa.Boolean, default=True, nullable=False)
    is_console_mode = sa.Column(sa.Boolean, default=True, nullable=False)
    default_currency = sa.Column(sa.Text, default=settings.DEFAULT_CURRENCY, nullable=False)
    default_currency_position = sa.Column(sa.Boolean, default=settings.DEFAULT_CURRENCY_POSITION, nullable=False)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
    modified_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)

    requests = orm.relationship('ChatRequests')
    requests_log = orm.relationship('RequestsLog')
    events = orm.relationship('Event')


class Currency(BaseObject):
    """
    https://en.wikipedia.org/wiki/ISO_4217

    See:
    migrations/versions/20190306193447_currencies_chat_request_foreigns.py
    migrations/versions/20190326060130_add_btt_currency.py
    """
    __tablename__ = 'currencies'

    id = sa.Column(sa.Integer, primary_key=True)
    code = sa.Column(sa.Text, unique=True, nullable=False)
    name = sa.Column(sa.Text, nullable=False)
    is_active = sa.Column(sa.Boolean, index=True, nullable=False)
    is_crypto = sa.Column(sa.Boolean, index=True, nullable=False)


class ChatRequests(BaseObject):
    __tablename__ = 'chat_requests'
    __table_args__ = (sa.UniqueConstraint('chat_id', 'from_currency_id', 'to_currency_id'),)

    id = sa.Column(sa.Integer, primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey('chats.id'), nullable=False)
    from_currency_id = sa.Column(sa.Integer, sa.ForeignKey('currencies.id'), nullable=False)
    to_currency_id = sa.Column(sa.Integer, sa.ForeignKey('currencies.id'), nullable=False)
    times = sa.Column(sa.Integer, server_default='1', nullable=False)
    modified_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)

    chat = orm.relationship('Chat')
    from_currency = orm.relationship('Currency', foreign_keys=[from_currency_id])
    to_currency = orm.relationship('Currency', foreign_keys=[to_currency_id])


class RequestsLog(BaseObject):
    __tablename__ = 'requests_log'

    id = sa.Column(sa.Integer, primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey('chats.id'), nullable=False)
    message = sa.Column(sa.Text, nullable=False)
    tag = sa.Column(sa.Text, nullable=False)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)

    chat = orm.relationship('Chat')


class Exchange(BaseObject):
    __tablename__ = 'exchanges'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, nullable=False, index=True)
    weight = sa.Column(sa.Integer, nullable=False)
    is_active = sa.Column(sa.Boolean, nullable=False)

    rates = orm.relationship('Rate')


class Rate(BaseObject):
    __tablename__ = 'rates'
    __table_args__ = (sa.UniqueConstraint('exchange_id', 'from_currency_id', 'to_currency_id'),)

    id = sa.Column(sa.Integer, primary_key=True)
    exchange_id = sa.Column(sa.Integer, sa.ForeignKey('exchanges.id'), nullable=False)
    from_currency_id = sa.Column(sa.Integer, sa.ForeignKey('currencies.id'), nullable=False)
    to_currency_id = sa.Column(sa.Integer, sa.ForeignKey('currencies.id'), nullable=False)
    rate = sa.Column(sa.Numeric(decimal_precision, decimal_scale), nullable=False)
    rate_open = sa.Column(sa.Numeric(decimal_precision, decimal_scale), nullable=True)
    low24h = sa.Column(sa.Numeric(decimal_precision, decimal_scale), nullable=True)
    high24h = sa.Column(sa.Numeric(decimal_precision, decimal_scale), nullable=True)
    last_trade_at = sa.Column(sa.TIMESTAMP, nullable=False)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
    modified_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)

    exchange = orm.relationship('Exchange')
    from_currency = orm.relationship('Currency', foreign_keys=[from_currency_id])
    to_currency = orm.relationship('Currency', foreign_keys=[to_currency_id])


class Event(BaseObject):
    __tablename__ = 'events'
    __table_args__ = (sa.UniqueConstraint('chat_id', 'event'),)

    id = sa.Column(sa.Integer, primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey('chats.id'), nullable=False)
    event = sa.Column(sa.Text, nullable=False)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)

    chat = orm.relationship('Chat')


class Notification(BaseObject):
    __tablename__ = 'notifications'

    id = sa.Column(sa.Integer, primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey('chats.id'), nullable=False)
    from_currency_id = sa.Column(sa.Integer, sa.ForeignKey('currencies.id'), nullable=False)
    to_currency_id = sa.Column(sa.Integer, sa.ForeignKey('currencies.id'), nullable=False)
    trigger_clause = sa.Column(sa.Enum('more', 'less', 'diff', 'percent', name='notification_clause'), nullable=False)
    trigger_value = sa.Column(sa.Numeric(decimal_precision, decimal_scale), nullable=False)
    last_rate = sa.Column(sa.Numeric(decimal_precision, decimal_scale), nullable=False)
    is_active = sa.Column(sa.Boolean(), default=True, index=True, nullable=False)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
    modified_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)

    chat = orm.relationship('Chat')
    from_currency = orm.relationship('Currency', foreign_keys=[from_currency_id])
    to_currency = orm.relationship('Currency', foreign_keys=[to_currency_id])


# TODO: move
@region.cache_on_arguments(expiration_time=300)
def get_all_currencies():
    return [x[0] for x in Session.query(Currency.code).filter_by(is_active=True)]
