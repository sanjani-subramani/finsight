"""widen simulation_runs.random_seed to bigint

Revision ID: 2e7d4c1f9a83
Revises: 5b8f3a1d7c92
Create Date: 2026-09-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e7d4c1f9a83'
down_revision: Union[str, None] = '5b8f3a1d7c92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The seed is deliberately a ~63-bit value (numpy default_rng's full
    # entropy range) -- int32 overflows on the first real value. Only
    # caught by running against real Postgres (Step 19); SQLite's dynamic
    # typing hid this in every unit test.
    op.alter_column('simulation_runs', 'random_seed', type_=sa.BigInteger(), existing_type=sa.Integer())


def downgrade() -> None:
    op.alter_column('simulation_runs', 'random_seed', type_=sa.Integer(), existing_type=sa.BigInteger())
