"""set 6 dashboards and master games
Revision ID: 20260904_set6
Revises: 20260904_seed_v16_content
"""
from alembic import op
import sqlalchemy as sa
revision='20260904_set6'; down_revision='20260904_seed_v16_content'; branch_labels=None; depends_on=None

def upgrade():
    op.create_table('master_games',
        sa.Column('id',sa.Integer,primary_key=True), sa.Column('external_id',sa.String(64),unique=True),
        sa.Column('white',sa.String(120),nullable=False), sa.Column('black',sa.String(120),nullable=False),
        sa.Column('year',sa.String(16)), sa.Column('opening',sa.String(180)), sa.Column('moves',sa.Text,nullable=False),
        sa.Column('annotation',sa.Text), sa.Column('source',sa.String(255)), sa.Column('is_active',sa.Boolean,nullable=False,server_default=sa.true()))
    op.create_index('ix_master_games_external_id','master_games',['external_id'],unique=True)
    op.create_table('parent_student_links', sa.Column('id',sa.Integer,primary_key=True),
        sa.Column('parent_id',sa.Integer,sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),
        sa.Column('student_id',sa.Integer,sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),
        sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()),
        sa.UniqueConstraint('parent_id','student_id',name='uq_parent_student'))
    op.create_index('ix_parent_student_links_parent_id','parent_student_links',['parent_id'])
    op.create_index('ix_parent_student_links_student_id','parent_student_links',['student_id'])
    # Import the already-migrated V16 master games into the dedicated library.
    import json
    from pathlib import Path
    data=json.loads((Path(__file__).resolve().parents[2]/'app'/'data'/'v16_content.json').read_text(encoding='utf-8'))
    games=data.get('games',{})
    table=sa.table('master_games', sa.column('external_id',sa.String),sa.column('white',sa.String),sa.column('black',sa.String),sa.column('year',sa.String),sa.column('opening',sa.String),sa.column('moves',sa.Text),sa.column('annotation',sa.Text),sa.column('source',sa.String),sa.column('is_active',sa.Boolean))
    for gid,g in games.items():
        op.execute(sa.insert(table).values(external_id=gid,white=g.get('white','White'),black=g.get('black','Black'),year=str(g.get('year','')),opening=g.get('opening',''),moves=g.get('moves',''),annotation=g.get('annotation',''),source='Chess-Mastery-Academy-V16',is_active=True))

def downgrade():
    op.drop_table('parent_student_links'); op.drop_index('ix_master_games_external_id',table_name='master_games'); op.drop_table('master_games')
