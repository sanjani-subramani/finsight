"""add conflict_records table

Revision ID: 8e996ee55bd7
Revises: e962fd342bfc
Create Date: 2026-09-09 13:40:23.853502

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8e996ee55bd7'
down_revision: Union[str, None] = 'e962fd342bfc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'conflict_records',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('event_a_id', sa.UUID(), nullable=False),
        sa.Column('event_b_id', sa.UUID(), nullable=False),
        sa.Column('field_name', sa.String(length=64), nullable=False),
        sa.Column('value_a', sa.String(length=255), nullable=False),
        sa.Column('value_b', sa.String(length=255), nullable=False),
        sa.Column('winner_event_id', sa.UUID(), nullable=False),
        sa.Column('winner_reason', sa.Text(), nullable=False),
        sa.Column(
            'resolved_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column('user_overridden', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['event_a_id'], ['financial_events.id']),
        sa.ForeignKeyConstraint(['event_b_id'], ['financial_events.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['winner_event_id'], ['financial_events.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_conflict_records_resolved_at'), 'conflict_records', ['resolved_at'], unique=False
    )
    op.create_index(
        op.f('ix_conflict_records_user_overridden'),
        'conflict_records',
        ['user_overridden'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_conflict_records_user_overridden'), table_name='conflict_records')
    op.drop_index(op.f('ix_conflict_records_resolved_at'), table_name='conflict_records')
    op.drop_table('conflict_records')
