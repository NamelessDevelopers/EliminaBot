"""add guild table

Revision ID: 468e613dea13
Revises: 
Create Date: 2024-10-05 06:30:33.683390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '468e613dea13'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('guild',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('delete_delay', sa.Integer(), nullable=False),
    sa.Column('toggled_channels', sqlite.JSON(), nullable=False),
    sa.Column('ignored_bots', sqlite.JSON(), nullable=False),
    sa.Column('image_snipe', sa.Boolean(), nullable=False),
    sa.Column('snipe_enabled', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('guild')
    # ### end Alembic commands ###
