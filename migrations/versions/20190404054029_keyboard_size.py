"""keyboard_size

Revision ID: 20190404054029
Revises: 20190404023229
Create Date: 2019-04-04 05:40:29.527255

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative import declarative_base


# revision identifiers, used by Alembic.
revision = '20190404054029'
down_revision = '20190404023229'
branch_labels = None
depends_on = None

Base = declarative_base()


class Chat(Base):
    __tablename__ = 'chats'

    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=False)
    keyboard_size = sa.Column(sa.Text, default='3x2', nullable=False)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
    modified_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chats', sa.Column('keyboard_size', sa.Text(), nullable=True))
    # ### end Alembic commands ###

    session = Session(bind=op.get_bind())
    session.query(Chat).update({'keyboard_size': '3x3', 'modified_at': Chat.modified_at})
    op.alter_column('chats', 'keyboard_size', nullable=False)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chats', 'keyboard_size')
    # ### end Alembic commands ###
