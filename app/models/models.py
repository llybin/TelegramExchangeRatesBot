from sqlalchemy import (
    UniqueConstraint,
    BigInteger,
    Boolean,
    Enum,
    Column,
    TIMESTAMP,
    func,
    Integer,
    Numeric,
    CHAR,
    Text,
)


from .db import db


class Chat(db):
    __tablename__ = 'chats'

    id = Column(BigInteger, primary_key=True)
    first_name = Column(Text, nullable=True)
    username = Column(Text, nullable=True)
    locale = Column(Text, default='en_US')
    is_subscribed = Column(Boolean, server_default='true')
    is_console_mode = Column(Boolean, server_default='true')
    created = Column(TIMESTAMP, server_default=func.now())
    updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class ChatRate(db):
    __tablename__ = 'chat_rates'
    # __table_args__ = (UniqueConstraint('chat_id', 'currencies'),)

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger)
    currencies = Column(Text)
    cnt = Column(Integer, server_default='0')
    updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


# class Event(db):
#     __tablename__ = 'events'
#     # __table_args__ = (UniqueConstraint('chat_id', 'event', name='chat_id_events'),)
#
#     id = Column(Integer, primary_key=True)
#     chat_id = Column(BigInteger, nullable=False, index=True)
#     event = Column(Text, nullable=False, index=True)
#     created = Column(TIMESTAMP, server_default=func.now(), nullable=False)


class Log(db):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger)
    user_id = Column(BigInteger)
    message = Column(Text)
    tag = Column(Text)
    created = Column(TIMESTAMP, server_default=func.now())


# class Notification(db):
#     __tablename__ = 'notifications'
#     # __table_args__ = (UniqueConstraint('chat_id', 'currencies', 'clause'),)
#
#     id = Column(Integer, primary_key=True)
#     chat_id = Column(BigInteger, nullable=False, index=True)
#     currencies = Column(Text, nullable=False)
#     clause = Column(Enum('more', 'less', 'diff', 'percent', name='notification_clause'), nullable=False)
#     value = Column(Numeric(14, 6), nullable=False)
#     last_rate = Column(Numeric(14, 6), nullable=False)
#     is_active = Column(Boolean(), default=True, nullable=False)
#     created = Column(TIMESTAMP, server_default=func.now(), nullable=False)
#     updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp(), nullable=False)
#
#
# class Rate(db):
#     __tablename__ = 'rates'
#
#     currency = Column(CHAR(3), primary_key=True)
#     rate_open = Column(Numeric(14, 6), nullable=False)
#     rate = Column(Numeric(14, 6), nullable=False)
#     source = Column(Text, nullable=False)
#     weight = Column(Integer, server_default='0', index=True, nullable=False)
#     last_trade_at = Column(TIMESTAMP, nullable=False)
#     created = Column(TIMESTAMP, server_default=func.now(), nullable=False)
#     updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp(), nullable=False)
