"""Add training_plan_progress table (3-Year Structured Training Plan, migrated from V16's studyPlan.js).

The plan's content (36 months of weekly goals / daily sessions / resources,
plus the dailyPlans/weeklySchedules templates) is static reference data
served from app/data/training_plan.json — no table needed for it, matching
how V16 kept it as a plain JS import. Only a user's checkbox state against
that content needs to persist, so this migration adds a single table for
that: one row per (user, item_key) checked off.
"""
from alembic import op
import sqlalchemy as sa

revision = '20260904_add_training_plan'
down_revision = '20260904_add_coupons'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'training_plan_progress',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('item_key', sa.String(length=64), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'item_key', name='uq_training_plan_progress_user_item'),
    )
    op.create_index('ix_training_plan_progress_user_id', 'training_plan_progress', ['user_id'])


def downgrade():
    op.drop_index('ix_training_plan_progress_user_id', table_name='training_plan_progress')
    op.drop_table('training_plan_progress')
