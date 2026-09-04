from pathlib import Path
import json
from alembic import op
import sqlalchemy as sa

revision = '20260904_seed_v16_content'
down_revision = '20260904_add_gamification'
branch_labels = None
depends_on = None

DATA_FILE = Path(__file__).resolve().parents[2] / 'app' / 'data' / 'v16_content.json'

def _load():
    with DATA_FILE.open('r', encoding='utf-8') as fh:
        return json.load(fh)

def _append_games(content, game_ids, games):
    if not game_ids:
        return content or ''
    blocks = [content or '', '<hr><h3>♟️ Master Game Study</h3>']
    for gid in game_ids:
        game = games.get(gid)
        if not game:
            continue
        blocks.append(
            f"<div class=\"game-study\"><h4>{game.get('white','White')} — "
            f"{game.get('black','Black')} ({game.get('year','')})</h4>"
            f"<p><strong>{game.get('opening','')}</strong></p>"
            f"<p><strong>Moves:</strong> {game.get('moves','')}</p>"
            f"<p>{game.get('annotation','')}</p></div>"
        )
    return '\n'.join(blocks)

def upgrade():
    bind = op.get_bind()
    data = _load()
    curriculum = data['curriculumData']
    puzzles = data['puzzles']
    games = data['games']

    tracks = sa.table('tracks', sa.column('id', sa.Integer), sa.column('name', sa.String),
        sa.column('slug', sa.String), sa.column('description', sa.Text), sa.column('icon', sa.String),
        sa.column('age_min', sa.Integer), sa.column('age_max', sa.Integer), sa.column('is_active', sa.Boolean))
    courses = sa.table('courses', sa.column('id', sa.Integer), sa.column('track_id', sa.Integer),
        sa.column('name', sa.String), sa.column('slug', sa.String), sa.column('description', sa.Text),
        sa.column('fee', sa.Integer), sa.column('duration_months', sa.Integer), sa.column('is_published', sa.Boolean))
    chapters = sa.table('chapters', sa.column('id', sa.Integer), sa.column('course_id', sa.Integer),
        sa.column('title', sa.String), sa.column('description', sa.Text), sa.column('order', sa.Integer),
        sa.column('is_published', sa.Boolean))
    lessons = sa.table('lessons', sa.column('id', sa.Integer), sa.column('chapter_id', sa.Integer),
        sa.column('title', sa.String), sa.column('description', sa.Text), sa.column('content', sa.Text),
        sa.column('order', sa.Integer), sa.column('lesson_type', sa.String), sa.column('is_published', sa.Boolean))
    puzzle_table = sa.table('puzzles', sa.column('id', sa.Integer), sa.column('lesson_id', sa.Integer),
        sa.column('fen', sa.String), sa.column('prompt', sa.String), sa.column('answer', sa.String),
        sa.column('explanation', sa.Text), sa.column('points', sa.Integer), sa.column('is_active', sa.Boolean))

    existing_tracks = {r.slug: r.id for r in bind.execute(sa.select(tracks.c.id, tracks.c.slug)).fetchall()}
    track_defs = [
        ('v16-junior', 'V16 Junior & Kids', 'Original V16 kids curriculum, adapted into the Active-Chess learning path.', '⭐', 5, 14),
        ('v16-core', 'V16 Chess Mastery', 'Original V16 fundamentals, tactics, strategy, endgames, calculation and competition curriculum.', '♟️', None, None),
    ]
    track_ids = {}
    for slug, name, desc, icon, amin, amax in track_defs:
        if slug in existing_tracks:
            track_ids[slug] = existing_tracks[slug]
        else:
            bind.execute(sa.insert(tracks).values(name=name, slug=slug, description=desc, icon=icon,
                age_min=amin, age_max=amax, is_active=True))
            track_ids[slug] = bind.execute(sa.select(tracks.c.id).where(tracks.c.slug == slug)).scalar_one()

    lesson_ids = {}
    for course_key, course in curriculum.items():
        track_slug = 'v16-junior' if course_key == 'kids' else 'v16-core'
        course_slug = f"v16-{course_key}"
        course_id = bind.execute(sa.select(courses.c.id).where(courses.c.slug == course_slug)).scalar_one_or_none()
        if course_id is None:
            bind.execute(sa.insert(courses).values(track_id=track_ids[track_slug], name=course['title'],
                slug=course_slug, description=course.get('description'), fee=0,
                duration_months=max(1, round(course.get('estimatedHours', 6) / 20)), is_published=True))
            course_id = bind.execute(sa.select(courses.c.id).where(courses.c.slug == course_slug)).scalar_one()

        chapter_id = bind.execute(sa.select(chapters.c.id).where(
            sa.and_(chapters.c.course_id == course_id, chapters.c.order == 1))).scalar_one_or_none()
        if chapter_id is None:
            bind.execute(sa.insert(chapters).values(course_id=course_id, title=f"V16 {course['title']}",
                description=f"Imported from Chess-Mastery-Academy-V16: {course.get('description','')}",
                order=1, is_published=True))
            chapter_id = bind.execute(sa.select(chapters.c.id).where(
                sa.and_(chapters.c.course_id == course_id, chapters.c.order == 1))).scalar_one()

        for idx, lesson in enumerate(course.get('lessons', []), start=1):
            lesson_id = bind.execute(sa.select(lessons.c.id).where(
                sa.and_(lessons.c.chapter_id == chapter_id, lessons.c.order == idx))).scalar_one_or_none()
            if lesson_id is None:
                lesson_type = 'puzzle' if lesson.get('puzzles') else 'lesson'
                content = _append_games(lesson.get('content', ''), lesson.get('games', []), games)
                bind.execute(sa.insert(lessons).values(chapter_id=chapter_id, title=lesson['title'],
                    description=lesson.get('description') or f"V16 lesson {idx}: {lesson['title']}",
                    content=content, order=idx, lesson_type=lesson_type, is_published=True))
                lesson_id = bind.execute(sa.select(lessons.c.id).where(
                    sa.and_(lessons.c.chapter_id == chapter_id, lessons.c.order == idx))).scalar_one()
            lesson_ids[(course_key, lesson['id'])] = lesson_id

    puzzle_lesson = {}
    for course_key, course in curriculum.items():
        for lesson in course.get('lessons', []):
            for puzzle_id in lesson.get('puzzles', []):
                if puzzle_id in puzzles and (course_key, lesson['id']) in lesson_ids:
                    puzzle_lesson[puzzle_id] = lesson_ids[(course_key, lesson['id'])]

    theme_map = {'Fork': ('tactics', 't1'), 'Pin': ('tactics', 't1'), 'Skewer': ('tactics', 't1'), 'Back Rank Mate': ('tactics', 't3'), 'Checkmate': ('tactics', 't3'), 'Smothered Mate': ('tactics', 't3'), "Anastasia's Mate": ('tactics', 't3'), "Boden's Mate Pattern": ('tactics', 't3'), 'Discovered Attack': ('tactics', 't2'), 'Double Check': ('tactics', 't2'), 'Deflection': ('tactics', 't2'), 'Overloading': ('tactics', 't2'), 'Double Attack': ('tactics', 't1'), 'Tactics': ('tactics', 't1'), 'Bishop Tactics': ('tactics', 't1'), 'Knight Tactics': ('tactics', 't1'), 'Counting Attackers/Defenders': ('calculation', 'c1'), 'Forcing Moves': ('calculation', 'c1'), 'Checks': ('calculation', 'c1'), 'Underpromotion': ('basics', 'b2'), 'Promotion': ('basics', 'b2'), 'Pawn Promotion': ('basics', 'b2'), 'En Passant': ('basics', 'b2'), 'Centre Control': ('basics', 'b3'), 'Development': ('basics', 'b3'), 'King Safety': ('basics', 'b3'), 'Opening Principles': ('basics', 'b3'), 'Opening Strategy': ('basics', 'b3'), 'Piece Activity': ('strategy', 's2'), 'Piece Safety': ('strategy', 's2'), 'Rook Activity': ('strategy', 's2'), 'Knight Activity': ('strategy', 's2'), 'Queen Activity': ('strategy', 's2'), 'Prophylaxis': ('strategy', 's3'), 'Pawn Break': ('strategy', 's1'), 'Pawn Structure': ('strategy', 's1'), 'Positional': ('strategy', 's2'), 'Opposite Side Castling': ('strategy', 's3'), 'Rook Trade': ('endgames', 'e3'), 'King Activity': ('endgames', 'e2'), 'Key Squares': ('endgames', 'e2'), 'Rook Technique': ('endgames', 'e3'), 'Rook Endgame': ('endgames', 'e3'), 'Opposition': ('endgames', 'e2'), 'King and Pawn': ('endgames', 'e2'), 'Square Rule': ('endgames', 'e2'), 'Lucena Position': ('endgames', 'e3'), 'Simplification': ('endgames', 'e3'), 'Attack': ('tactics', 't2')}
    for puzzle_id, puzzle in puzzles.items():
        lesson_id = puzzle_lesson.get(puzzle_id)
        if lesson_id is None:
            course_key, lesson_key = theme_map.get(puzzle.get('theme'), ('tactics', 't1'))
            lesson_id = lesson_ids[(course_key, lesson_key)]
        exists = bind.execute(sa.select(puzzle_table.c.id).where(
            sa.and_(puzzle_table.c.lesson_id == lesson_id, puzzle_table.c.prompt == puzzle.get('title', ''))
        )).scalar_one_or_none()
        if exists is not None:
            continue
        bind.execute(sa.insert(puzzle_table).values(lesson_id=lesson_id, fen=puzzle['fen'],
            prompt=puzzle['title'], answer=puzzle['solution'], explanation=puzzle.get('explanation'),
            points=10, is_active=True))

def downgrade():
    bind = op.get_bind()
    bind.execute(sa.text("DELETE FROM puzzles WHERE lesson_id IN (SELECT l.id FROM lessons l JOIN chapters c ON l.chapter_id=c.id JOIN courses co ON c.course_id=co.id WHERE co.slug LIKE 'v16-%')"))
    bind.execute(sa.text("DELETE FROM lessons WHERE chapter_id IN (SELECT c.id FROM chapters c JOIN courses co ON c.course_id=co.id WHERE co.slug LIKE 'v16-%')"))
    bind.execute(sa.text("DELETE FROM chapters WHERE course_id IN (SELECT id FROM courses WHERE slug LIKE 'v16-%')"))
    bind.execute(sa.text("DELETE FROM courses WHERE slug LIKE 'v16-%'"))
    bind.execute(sa.text("DELETE FROM tracks WHERE slug IN ('v16-junior','v16-core')"))
