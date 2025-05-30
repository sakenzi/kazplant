"""update_users

Revision ID: 68e4c6298a61
Revises: 99aba8ad7814
Create Date: 2025-04-28 17:46:23.031769

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68e4c6298a61'
down_revision: Union[str, None] = '99aba8ad7814'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(length=30),
               type_=sa.Text(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'password',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=30),
               existing_nullable=True)
    # ### end Alembic commands ###
