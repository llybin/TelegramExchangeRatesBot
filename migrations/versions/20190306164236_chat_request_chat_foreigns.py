"""chat_request_chat_foreigns

Revision ID: 20190306164236
Revises: 20190306162241
Create Date: 2019-03-06 16:42:36.594307

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# revision identifiers, used by Alembic.
revision = '20190306164236'
down_revision = '20190306162241'
branch_labels = None
depends_on = None

Base = declarative_base()


class Chat(Base):
    __tablename__ = 'chats'

    id = sa.Column(sa.BigInteger, primary_key=True)

    requests = relationship('ChatRequests', backref='chat')
    requests_log = relationship('RequestsLog', backref='chat')


class ChatRequests(Base):
    __tablename__ = 'chat_requests'

    id = sa.Column(sa.Integer, primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey('chats.id'), nullable=False)
    currencies = sa.Column(sa.Text, nullable=False)
    cnt = sa.Column(sa.Integer, server_default='0', nullable=False)
    modified_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)


class RequestsLog(Base):
    __tablename__ = 'requests_log'

    id = sa.Column(sa.Integer, primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey('chats.id'), nullable=False)
    message = sa.Column(sa.Text, nullable=False)
    tag = sa.Column(sa.Text, nullable=False)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)


def upgrade():
    op.drop_column('requests_log', 'user_id')
    op.alter_column('requests_log', 'created', new_column_name='created_at')

    op.alter_column('chat_requests', 'updated', new_column_name='modified_at')
    op.alter_column('chats', 'created', new_column_name='created_at')
    op.alter_column('chats', 'updated', new_column_name='modified_at')

    session = Session(bind=op.get_bind())

    print('checking relations chat_requests on chats')
    for x in session.query(ChatRequests).yield_per(1000):
        if not x.chat:
            print(f'delete bad data from chat_requests {x}')
            session.delete(x)

    op.create_foreign_key(None, 'chat_requests', 'chats', ['chat_id'], ['id'])

    print('checking relations requests_log on chats')
    for x in session.query(RequestsLog).yield_per(1000):
        if not x.chat:
            print(f'delete bad data from requests_log: {x}')
            session.delete(x)

    op.create_foreign_key(None, 'requests_log', 'chats', ['chat_id'], ['id'])


def downgrade():
    pass
