"""add shadow mode override and intervention snapshot id

Revision ID: f47c3151db74
Revises: c68610a680b9
Create Date: 2026-09-10 19:14:04.933149

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f47c3151db74'
down_revision: Union[str, None] = 'c68610a680b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('interventions', sa.Column('snapshot_id', sa.UUID(), nullable=True))
    op.add_column('users', sa.Column('shadow_mode_override', sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'shadow_mode_override')
    op.drop_column('interventions', 'snapshot_id')
