"""twin fold state and recurring candidates

Revision ID: 21be0f857ee6
Revises: 8e996ee55bd7
Create Date: 2026-09-09 21:38:23.127146

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '21be0f857ee6'
down_revision: Union[str, None] = '8e996ee55bd7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'recurring_candidates',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('counterparty', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=128), nullable=True),
        sa.Column('suggested_amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('interval_days', sa.Integer(), nullable=False),
        sa.Column('day_of_month', sa.Integer(), nullable=True),
        sa.Column('confidence', sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column('detection_method', sa.String(length=16), nullable=False),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.Column('evidence_event_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "detection_method IN ('statistical', 'llm')",
            name='ck_recurring_candidates_detection_method',
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'confirmed', 'dismissed')", name='ck_recurring_candidates_status'
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_recurring_candidates_status'), 'recurring_candidates', ['status'], unique=False
    )
    op.add_column('income_sources', sa.Column('last_received_date', sa.Date(), nullable=True))
    op.add_column(
        'twin_states',
        sa.Column('fold_state', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('twin_states', 'fold_state')
    op.drop_column('income_sources', 'last_received_date')
    op.drop_index(op.f('ix_recurring_candidates_status'), table_name='recurring_candidates')
    op.drop_table('recurring_candidates')
