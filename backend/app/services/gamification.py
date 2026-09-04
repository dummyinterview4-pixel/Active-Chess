from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models import UserStats, LessonProgress, PuzzleAttempt, QuizAttempt, Badge, UserBadge


def _get_or_create_stats(db: Session, user_id: int) -> UserStats:
    stats = db.query(UserStats).filter_by(user_id=user_id).first()
    if not stats:
        stats = UserStats(user_id=user_id, total_stars=0, current_streak=0, longest_streak=0)
        db.add(stats)
        db.flush()
    return stats


def record_activity(db: Session, user, stars: int = 0, commit: bool = True):
    """Award stars, update the daily streak, and check for newly earned badges.

    Returns (stats, new_badges).
    """
    stats = _get_or_create_stats(db, user.id)
    stats.total_stars = (stats.total_stars or 0) + max(stars, 0)

    today = date.today()
    if stats.last_activity_date == today:
        pass
    elif stats.last_activity_date == today - timedelta(days=1):
        stats.current_streak = (stats.current_streak or 0) + 1
    else:
        stats.current_streak = 1
    stats.last_activity_date = today
    if stats.current_streak > (stats.longest_streak or 0):
        stats.longest_streak = stats.current_streak

    db.flush()

    new_badges = _check_badges(db, user, stats)
    if commit:
        db.commit()
    db.refresh(stats)
    return stats, new_badges


def _check_badges(db: Session, user, stats: UserStats):
    earned_ids = {row[0] for row in db.query(UserBadge.badge_id).filter_by(user_id=user.id).all()}
    lessons_completed = db.query(LessonProgress).filter_by(user_id=user.id, completed=True).count()
    puzzles_solved = db.query(PuzzleAttempt).filter_by(user_id=user.id, correct=True).count()
    quizzes_solved = db.query(QuizAttempt).filter_by(user_id=user.id, correct=True).count()

    metric_values = {
        'stars_total': stats.total_stars or 0,
        'streak': stats.current_streak or 0,
        'lessons_completed': lessons_completed,
        'puzzles_solved': puzzles_solved,
        'quizzes_solved': quizzes_solved,
    }

    newly = []
    for badge in db.query(Badge).all():
        if badge.id in earned_ids:
            continue
        value = metric_values.get(badge.criteria_type)
        if value is not None and value >= badge.criteria_value:
            db.add(UserBadge(user_id=user.id, badge_id=badge.id))
            newly.append(badge)

    return newly
