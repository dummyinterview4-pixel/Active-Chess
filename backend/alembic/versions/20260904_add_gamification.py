from alembic import op
import sqlalchemy as sa

revision='20260904_add_gamification'
down_revision='20260903_add_puzzles'
branch_labels=None
depends_on=None

def upgrade():
    # Fix pre-existing schema drift: models.Enrollment.completed_at was never
    # added by a migration, causing every ORM SELECT on enrollments to fail
    # with "no such column: enrollments.completed_at" as soon as a query
    # touched that mapped column.
    op.add_column('enrollments', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))

    op.create_table('quiz_questions',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('lesson_id',sa.Integer(),sa.ForeignKey('lessons.id'),nullable=False),
        sa.Column('prompt',sa.String(length=500),nullable=False),
        sa.Column('option_a',sa.String(length=200),nullable=False),
        sa.Column('option_b',sa.String(length=200),nullable=False),
        sa.Column('option_c',sa.String(length=200),nullable=False),
        sa.Column('option_d',sa.String(length=200),nullable=False),
        sa.Column('correct_option',sa.String(length=1),nullable=False),
        sa.Column('explanation',sa.Text(),nullable=True),
        sa.Column('points',sa.Integer(),nullable=False,server_default='10'),
        sa.Column('is_active',sa.Boolean(),nullable=False,server_default=sa.true()))
    op.create_index('ix_quiz_questions_lesson_id','quiz_questions',['lesson_id'])

    op.create_table('quiz_attempts',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('quiz_question_id',sa.Integer(),sa.ForeignKey('quiz_questions.id'),nullable=False),
        sa.Column('user_id',sa.Integer(),sa.ForeignKey('users.id'),nullable=False),
        sa.Column('selected_option',sa.String(length=1),nullable=False),
        sa.Column('correct',sa.Boolean(),nullable=False,server_default=sa.false()),
        sa.Column('points',sa.Integer(),nullable=False,server_default='0'))
    op.create_index('ix_quiz_attempts_quiz_question_id','quiz_attempts',['quiz_question_id'])
    op.create_index('ix_quiz_attempts_user_id','quiz_attempts',['user_id'])

    op.create_table('child_profiles',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('user_id',sa.Integer(),sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),
        sa.Column('display_name',sa.String(length=120),nullable=True),
        sa.Column('avatar',sa.String(length=16),nullable=False,server_default='🦁'),
        sa.Column('age',sa.Integer(),nullable=True),
        sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()),
        sa.Column('updated_at',sa.DateTime(timezone=True)))
    op.create_index('ix_child_profiles_user_id','child_profiles',['user_id'],unique=True)

    op.create_table('user_stats',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('user_id',sa.Integer(),sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),
        sa.Column('total_stars',sa.Integer(),nullable=False,server_default='0'),
        sa.Column('current_streak',sa.Integer(),nullable=False,server_default='0'),
        sa.Column('longest_streak',sa.Integer(),nullable=False,server_default='0'),
        sa.Column('last_activity_date',sa.Date(),nullable=True),
        sa.Column('updated_at',sa.DateTime(timezone=True)))
    op.create_index('ix_user_stats_user_id','user_stats',['user_id'],unique=True)

    op.create_table('badges',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('code',sa.String(length=64),nullable=False),
        sa.Column('name',sa.String(length=120),nullable=False),
        sa.Column('description',sa.Text(),nullable=True),
        sa.Column('icon',sa.String(length=16),nullable=False,server_default='🏅'),
        sa.Column('criteria_type',sa.String(length=32),nullable=False),
        sa.Column('criteria_value',sa.Integer(),nullable=False))
    op.create_index('ix_badges_code','badges',['code'],unique=True)

    op.create_table('user_badges',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('user_id',sa.Integer(),sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),
        sa.Column('badge_id',sa.Integer(),sa.ForeignKey('badges.id',ondelete='CASCADE'),nullable=False),
        sa.Column('earned_at',sa.DateTime(timezone=True),server_default=sa.func.now()),
        sa.UniqueConstraint('user_id','badge_id',name='uq_user_badge'))
    op.create_index('ix_user_badges_user_id','user_badges',['user_id'])
    op.create_index('ix_user_badges_badge_id','user_badges',['badge_id'])

    badges_table = sa.table('badges',
        sa.column('code', sa.String), sa.column('name', sa.String), sa.column('description', sa.Text),
        sa.column('icon', sa.String), sa.column('criteria_type', sa.String), sa.column('criteria_value', sa.Integer))
    op.bulk_insert(badges_table, [
        {'code':'first_star','name':'First Star','description':'Earn your very first star.','icon':'⭐','criteria_type':'stars_total','criteria_value':1},
        {'code':'star_collector','name':'Star Collector','description':'Earn 100 stars.','icon':'🌟','criteria_type':'stars_total','criteria_value':100},
        {'code':'chess_scholar','name':'Chess Scholar','description':'Earn 500 stars.','icon':'💫','criteria_type':'stars_total','criteria_value':500},
        {'code':'streak_3','name':'On a Roll','description':'Practice 3 days in a row.','icon':'🔥','criteria_type':'streak','criteria_value':3},
        {'code':'streak_7','name':'Week Warrior','description':'Practice 7 days in a row.','icon':'🔥','criteria_type':'streak','criteria_value':7},
        {'code':'first_lesson','name':'First Steps','description':'Complete your first lesson.','icon':'🌱','criteria_type':'lessons_completed','criteria_value':1},
        {'code':'lesson_master','name':'Lesson Master','description':'Complete 10 lessons.','icon':'📚','criteria_type':'lessons_completed','criteria_value':10},
        {'code':'puzzle_solver','name':'Puzzle Solver','description':'Solve 10 puzzles.','icon':'🧩','criteria_type':'puzzles_solved','criteria_value':10},
        {'code':'quiz_whiz','name':'Quiz Whiz','description':'Answer 10 quiz questions correctly.','icon':'🧠','criteria_type':'quizzes_solved','criteria_value':10},
    ])

def downgrade():
    op.drop_index('ix_user_badges_badge_id',table_name='user_badges')
    op.drop_index('ix_user_badges_user_id',table_name='user_badges')
    op.drop_table('user_badges')
    op.drop_index('ix_badges_code',table_name='badges')
    op.drop_table('badges')
    op.drop_index('ix_user_stats_user_id',table_name='user_stats')
    op.drop_table('user_stats')
    op.drop_index('ix_child_profiles_user_id',table_name='child_profiles')
    op.drop_table('child_profiles')
    op.drop_index('ix_quiz_attempts_user_id',table_name='quiz_attempts')
    op.drop_index('ix_quiz_attempts_quiz_question_id',table_name='quiz_attempts')
    op.drop_table('quiz_attempts')
    op.drop_index('ix_quiz_questions_lesson_id',table_name='quiz_questions')
    op.drop_table('quiz_questions')
    op.drop_column('enrollments', 'completed_at')
