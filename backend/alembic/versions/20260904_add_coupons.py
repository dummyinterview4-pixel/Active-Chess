"""Add coupons table and enrollments.coupon_code (migrated from V16).

Coupons stand in for real payment on paid (fee > 0) courses. Free courses
are unaffected. Seeds a `FREE` coupon with unlimited redemptions so today's
flow (no live billing) stays frictionless, matching the V16 signup-level
coupon system this replaces — just re-scoped to enrollment time.
"""
from alembic import op
import sqlalchemy as sa

revision = '20260904_add_coupons'
down_revision = '20260904_set6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'coupons',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('max_redemptions', sa.Integer(), nullable=True),
        sa.Column('times_redeemed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_coupons_code', 'coupons', ['code'], unique=True)

    op.add_column('enrollments', sa.Column('coupon_code', sa.String(length=64), nullable=True))

    coupons = sa.table(
        'coupons',
        sa.column('code', sa.String),
        sa.column('description', sa.String),
        sa.column('is_active', sa.Boolean),
        sa.column('max_redemptions', sa.Integer),
        sa.column('times_redeemed', sa.Integer),
    )
    op.get_bind().execute(sa.insert(coupons).values(
        code='FREE',
        description='Unlimited free enrollment while payment is not live yet.',
        is_active=True,
        max_redemptions=None,
        times_redeemed=0,
    ))


def downgrade():
    op.drop_column('enrollments', 'coupon_code')
    op.drop_index('ix_coupons_code', table_name='coupons')
    op.drop_table('coupons')
