"""add regimpact tables (products, workflows, regulations, regulatory_rules, impact_reports)

Revision ID: 3f6b8d2a91c7
Revises: 7a1c9e4f2b3d
Create Date: 2026-09-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '3f6b8d2a91c7'
down_revision: Union[str, None] = '7a1c9e4f2b3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'products',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=128), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('org_id', 'name', name='uq_products_org_name'),
    )
    op.create_index('ix_products_category', 'products', ['category'])

    op.create_table(
        'workflows',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('uses_service_node_ids', postgresql.JSONB(), nullable=False),
        sa.Column('uses_product_ids', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('org_id', 'name', name='uq_workflows_org_name'),
    )

    op.create_table(
        'regulations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('source_text', sa.Text(), nullable=False),
        sa.Column('source_url', sa.String(length=1000), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=True),
        sa.Column('ingested_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('ingested_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
    )

    op.create_table(
        'regulatory_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('regulation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('regulations.id'), nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('rule_text', sa.Text(), nullable=False),
        sa.Column('trigger_condition', sa.Text(), nullable=False),
        sa.Column('threshold_json', postgresql.JSONB(), nullable=True),
        sa.Column('required_action', sa.Text(), nullable=False),
        sa.Column('deadline_days', sa.Integer(), nullable=True),
        sa.Column('applies_to_product_categories', postgresql.JSONB(), nullable=False),
        sa.Column('extraction_confidence', sa.Numeric(4, 3), nullable=True),
        sa.Column('status', sa.String(length=16), server_default='pending_review', nullable=False),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending_review', 'confirmed', 'rejected')", name='ck_regulatory_rules_status'
        ),
    )
    op.create_index('ix_regulatory_rules_status', 'regulatory_rules', ['status'])

    op.create_table(
        'impact_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('regulation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('regulations.id'), nullable=False),
        sa.Column('rule_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('regulatory_rules.id'), nullable=False),
        sa.Column('affected_products', postgresql.JSONB(), nullable=False),
        sa.Column('affected_workflows', postgresql.JSONB(), nullable=False),
        sa.Column('affected_service_nodes', postgresql.JSONB(), nullable=False),
        sa.Column('estimated_transactions', sa.Integer(), server_default='0', nullable=False),
        sa.Column('required_changes', postgresql.JSONB(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('impact_reports')
    op.drop_index('ix_regulatory_rules_status', table_name='regulatory_rules')
    op.drop_table('regulatory_rules')
    op.drop_table('regulations')
    op.drop_table('workflows')
    op.drop_index('ix_products_category', table_name='products')
    op.drop_table('products')
