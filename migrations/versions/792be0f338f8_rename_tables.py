"""rename_tables

Revision ID: 792be0f338f8
Revises: 8b7deeb35c6c
Create Date: 2019-03-06 16:22:41.721964

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '792be0f338f8'
down_revision = '8b7deeb35c6c'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('chat_rates', 'chat_requests')
    op.execute('ALTER SEQUENCE chat_rates_id_seq RENAME TO chat_requests_id_seq')
    op.execute('ALTER INDEX chat_rates_pkey RENAME TO chat_requests_pkey')

    op.rename_table('messages', 'requests_log')
    op.execute('ALTER SEQUENCE messages_id_seq RENAME TO requests_log_id_seq')
    op.execute('ALTER INDEX messages_pkey RENAME TO requests_log_pkey')


def downgrade():
    op.rename_table('chat_requests', 'chat_rates')
    op.execute('ALTER SEQUENCE chat_requests_id_seq RENAME TO chat_rates_id_seq')
    op.execute('ALTER INDEX chat_requests_pkey RENAME TO chat_rates_pkey')

    op.rename_table('requests_log', 'messages')
    op.execute('ALTER SEQUENCE request_logs_id_seq RENAME TO messages_id_seq')
    op.execute('ALTER INDEX request_logs_pkey RENAME TO messages_pkey')
