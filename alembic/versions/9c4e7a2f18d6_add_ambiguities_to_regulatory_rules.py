"""add ambiguities to regulatory_rules

Revision ID: 9c4e7a2f18d6
Revises: 3f6b8d2a91c7
Create Date: 2026-09-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '9c4e7a2f18d6'
down_revision: Union[str, None] = '3f6b8d2a91c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'regulatory_rules',
        sa.Column('ambiguities', postgresql.JSONB(), nullable=False, server_default='[]'),
    )


def downgrade() -> None:
    op.drop_column('regulatory_rules', 'ambiguities')
