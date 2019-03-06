"""auto_20190306_1642

Revision ID: 91196c1f9f51
Revises: 792be0f338f8
Create Date: 2019-03-06 16:42:36.594307

"""
from alembic import op
from sqlalchemy.orm.session import Session

from app.models.models import ChatRequests, RequestsLog


# revision identifiers, used by Alembic.
revision = '91196c1f9f51'
down_revision = '792be0f338f8'
branch_labels = None
depends_on = None


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
