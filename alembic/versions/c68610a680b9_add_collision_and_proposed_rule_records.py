"""add collision and proposed rule records

Revision ID: c68610a680b9
Revises: 21be0f857ee6
Create Date: 2026-09-10 18:48:24.213976

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c68610a680b9'
down_revision: Union[str, None] = '21be0f857ee6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'proposed_rule_records',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('suggested_conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('support', sa.Integer(), nullable=False),
        sa.Column('lift', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('proposed_threshold', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('llm_rationale', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.Column('reviewed_by', sa.UUID(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending_review', 'approved', 'rejected')",
            name='ck_proposed_rule_records_status',
        ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_proposed_rule_records_created_at'), 'proposed_rule_records', ['created_at'], unique=False
    )
    op.create_index(
        op.f('ix_proposed_rule_records_status'), 'proposed_rule_records', ['status'], unique=False
    )

    op.create_table(
        'collision_records',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('condition_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('joint_probability', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('individual_probabilities', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('amplification_factor', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('severity', sa.String(length=16), nullable=False),
        sa.Column('urgency', sa.String(length=16), nullable=False),
        sa.Column('first_impact_date', sa.Date(), nullable=True),
        sa.Column('evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('human_statement', sa.Text(), nullable=False),
        sa.Column('simulation_run_id', sa.UUID(), nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_reason', sa.String(length=255), nullable=True),
        sa.CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')", name='ck_collision_records_severity'
        ),
        sa.CheckConstraint(
            "urgency IN ('low', 'medium', 'high', 'critical')", name='ck_collision_records_urgency'
        ),
        sa.ForeignKeyConstraint(['simulation_run_id'], ['simulation_runs.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_collision_records_detected_at'), 'collision_records', ['detected_at'], unique=False
    )
    op.create_index(op.f('ix_collision_records_severity'), 'collision_records', ['severity'], unique=False)
    op.create_index(
        'ix_collision_records_user_resolved', 'collision_records', ['user_id', 'resolved_at'], unique=False
    )

    op.add_column(
        'users', sa.Column('is_admin', sa.Boolean(), server_default=sa.false(), nullable=False)
    )


def downgrade() -> None:
    op.drop_column('users', 'is_admin')
    op.drop_index('ix_collision_records_user_resolved', table_name='collision_records')
    op.drop_index(op.f('ix_collision_records_severity'), table_name='collision_records')
    op.drop_index(op.f('ix_collision_records_detected_at'), table_name='collision_records')
    op.drop_table('collision_records')
    op.drop_index(op.f('ix_proposed_rule_records_status'), table_name='proposed_rule_records')
    op.drop_index(op.f('ix_proposed_rule_records_created_at'), table_name='proposed_rule_records')
    op.drop_table('proposed_rule_records')
