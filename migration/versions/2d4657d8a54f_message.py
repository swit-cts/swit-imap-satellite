"""message

Revision ID: 2d4657d8a54f
Revises: 
Create Date: 2024-04-30 09:00:38.940001

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '2d4657d8a54f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('key', table_name='sys_config')
    op.drop_table('sys_config')
    op.drop_table('com_user_email_auth')
    op.drop_index('user_id', table_name='com_user_info')
    op.drop_table('com_user_info')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('com_user_info',
    sa.Column('user_id', mysql.VARCHAR(length=36), nullable=False),
    sa.Column('email', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('password', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('created_at', mysql.DATETIME(), nullable=False),
    sa.Column('role', mysql.VARCHAR(length=10), nullable=False),
    sa.Column('is_active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('user_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('user_id', 'com_user_info', ['user_id'], unique=True)
    op.create_table('com_user_email_auth',
    sa.Column('user_id', mysql.VARCHAR(length=36), nullable=False),
    sa.Column('email', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('password', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('created_at', mysql.DATETIME(), nullable=False),
    sa.Column('updated_at', mysql.DATETIME(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['com_user_info.user_id'], name='com_user_email_auth_ibfk_1'),
    sa.PrimaryKeyConstraint('user_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('sys_config',
    sa.Column('key', mysql.VARCHAR(length=30), nullable=False),
    sa.Column('value', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('created_at', mysql.DATETIME(), nullable=False),
    sa.Column('updated_at', mysql.DATETIME(), nullable=False),
    sa.PrimaryKeyConstraint('key'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('key', 'sys_config', ['key'], unique=True)
    # ### end Alembic commands ###
