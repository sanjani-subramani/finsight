"""add failure_simulations table

Revision ID: 7a1c9e4f2b3d
Revises: 0db5b141d4b8
Create Date: 2026-09-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '7a1c9e4f2b3d'
down_revision: Union[str, None] = '0db5b141d4b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'failure_simulations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('failed_node', sa.String(length=255), nullable=False),
        sa.Column('duration_hours', sa.Numeric(8, 2), nullable=True),
        sa.Column('result', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('failure_simulations')
