"""add threat event raw reference and financial impact

Revision ID: 1903baf6ebd4
Revises: f47c3151db74
Create Date: 2026-09-10 20:48:49.201142

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1903baf6ebd4'
down_revision: Union[str, None] = 'f47c3151db74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('threat_events', sa.Column('raw_reference', sa.Text(), nullable=True))
    op.add_column(
        'threat_events',
        sa.Column('financial_impact', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('threat_events', 'financial_impact')
    op.drop_column('threat_events', 'raw_reference')
