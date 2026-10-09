"""add acknowledged_at to interventions

Revision ID: 5b8f3a1d7c92
Revises: 9c4e7a2f18d6
Create Date: 2026-09-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b8f3a1d7c92'
down_revision: Union[str, None] = '9c4e7a2f18d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('interventions', sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('interventions', 'acknowledged_at')
