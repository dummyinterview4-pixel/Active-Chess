from alembic import op
import sqlalchemy as sa

revision='20260903_add_puzzles'
down_revision='0001_active_learning_core'
branch_labels=None
depends_on=None

def upgrade():
    op.create_table('puzzles',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('lesson_id',sa.Integer(),sa.ForeignKey('lessons.id'),nullable=False),
        sa.Column('fen',sa.String(length=100),nullable=False),
        sa.Column('prompt',sa.String(length=500),nullable=False),
        sa.Column('answer',sa.String(length=50),nullable=False),
        sa.Column('explanation',sa.Text(),nullable=True),
        sa.Column('points',sa.Integer(),nullable=False,server_default='10'),
        sa.Column('is_active',sa.Boolean(),nullable=False,server_default=sa.true()))
    op.create_index('ix_puzzles_lesson_id','puzzles',['lesson_id'])
    op.create_table('puzzle_attempts',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('puzzle_id',sa.Integer(),sa.ForeignKey('puzzles.id'),nullable=False),
        sa.Column('user_id',sa.Integer(),sa.ForeignKey('users.id'),nullable=False),
        sa.Column('answer',sa.String(length=50),nullable=False),
        sa.Column('correct',sa.Boolean(),nullable=False,server_default=sa.false()),
        sa.Column('points',sa.Integer(),nullable=False,server_default='0'))
    op.create_index('ix_puzzle_attempts_puzzle_id','puzzle_attempts',['puzzle_id'])
    op.create_index('ix_puzzle_attempts_user_id','puzzle_attempts',['user_id'])

def downgrade():
    op.drop_index('ix_puzzle_attempts_user_id',table_name='puzzle_attempts')
    op.drop_index('ix_puzzle_attempts_puzzle_id',table_name='puzzle_attempts')
    op.drop_table('puzzle_attempts')
    op.drop_index('ix_puzzles_lesson_id',table_name='puzzles')
    op.drop_table('puzzles')
