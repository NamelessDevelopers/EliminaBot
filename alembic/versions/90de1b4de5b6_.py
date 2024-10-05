"""empty message

Revision ID: 90de1b4de5b6
Revises: 468e613dea13
Create Date: 2024-10-05 06:33:02.415024

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '90de1b4de5b6'
down_revision: Union[str, None] = '468e613dea13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
