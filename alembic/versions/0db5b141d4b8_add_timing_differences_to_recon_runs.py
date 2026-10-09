"""add timing_differences to recon_runs

Revision ID: 0db5b141d4b8
Revises: 1903baf6ebd4
Create Date: 2026-09-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0db5b141d4b8'
down_revision: Union[str, None] = '1903baf6ebd4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('recon_runs', sa.Column('timing_differences', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('recon_runs', 'timing_differences')
