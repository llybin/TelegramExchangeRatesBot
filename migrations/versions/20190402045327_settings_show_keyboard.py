"""settings_show_keyboard

Revision ID: 20190402045327
Revises: 20190402024141
Create Date: 2019-04-02 04:53:27.965342

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "20190402045327"
down_revision = "20190402024141"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "chats", "is_console_mode", nullable=False, new_column_name="is_show_keyboard"
    )
    op.execute("UPDATE chats SET is_show_keyboard=NOT is_show_keyboard")


def downgrade():
    pass
