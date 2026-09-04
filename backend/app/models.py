from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(32), nullable=False, default='student')
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    enrollments = relationship('Enrollment', back_populates='user', cascade='all, delete-orphan')
    progress = relationship('LessonProgress', back_populates='user', cascade='all, delete-orphan')
    parent_links = relationship('ParentStudentLink', foreign_keys='ParentStudentLink.parent_id', back_populates='parent', cascade='all, delete-orphan')
    coach_links = relationship('ParentStudentLink', foreign_keys='ParentStudentLink.student_id', back_populates='student', cascade='all, delete-orphan')

class Track(Base):
    __tablename__ = 'tracks'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    slug = Column(String(120), unique=True, index=True, nullable=False)
    description = Column(Text)
    icon = Column(String(32), default='♟️')
    age_min = Column(Integer)
    age_max = Column(Integer)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    courses = relationship('Course', back_populates='track', cascade='all, delete-orphan')

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey('tracks.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(160), nullable=False)
    slug = Column(String(160), unique=True, index=True, nullable=False)
    description = Column(Text)
    fee = Column(Integer, default=0)
    duration_months = Column(Integer, default=6)
    is_published = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    track = relationship('Track', back_populates='courses')
    chapters = relationship('Chapter', back_populates='course', cascade='all, delete-orphan', order_by='Chapter.order')
    enrollments = relationship('Enrollment', back_populates='course', cascade='all, delete-orphan')

class Chapter(Base):
    __tablename__ = 'chapters'
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(160), nullable=False)
    description = Column(Text)
    order = Column(Integer, nullable=False, default=0)
    is_published = Column(Boolean, nullable=False, default=False)
    course = relationship('Course', back_populates='chapters')
    lessons = relationship('Lesson', back_populates='chapter', cascade='all, delete-orphan', order_by='Lesson.order')
    __table_args__ = (UniqueConstraint('course_id', 'order', name='uq_chapter_course_order'),)

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey('chapters.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(180), nullable=False)
    description = Column(Text)
    content = Column(Text)
    order = Column(Integer, nullable=False, default=0)
    lesson_type = Column(String(32), nullable=False, default='lesson')
    is_published = Column(Boolean, nullable=False, default=False)
    chapter = relationship('Chapter', back_populates='lessons')
    progress = relationship('LessonProgress', back_populates='lesson', cascade='all, delete-orphan')
    __table_args__ = (UniqueConstraint('chapter_id', 'order', name='uq_lesson_chapter_order'),)

class Enrollment(Base):
    __tablename__ = 'enrollments'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    status = Column(String(32), nullable=False, default='active')
    # Which coupon (if any) was redeemed to unlock this enrollment. Only
    # ever set for paid courses (see Coupon below) — free courses enroll
    # without one.
    coupon_code = Column(String(64), nullable=True)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    user = relationship('User', back_populates='enrollments')
    course = relationship('Course', back_populates='enrollments')
    __table_args__ = (UniqueConstraint('user_id', 'course_id', name='uq_enrollment_user_course'),)


class Coupon(Base):
    """
    Stands in for real payment on paid (fee > 0) courses until billing is
    built. A coupon code grants free enrollment instead of charging a card.
    Kept as a real table (not a hardcoded string) so codes — including
    future paid-tier promo codes — can be managed from the Admin Console
    without a deployment, and so redemption counts are tracked from day one.
    Migrated from the V16 signup-level coupon system, but re-scoped to
    enrollment time, matching active-chess's per-course fee model.
    """
    __tablename__ = 'coupons'
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    # None = unlimited redemptions.
    max_redemptions = Column(Integer, nullable=True)
    times_redeemed = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class LessonProgress(Base):
    __tablename__ = 'lesson_progress'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    lesson_id = Column(Integer, ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False)
    completed = Column(Boolean, nullable=False, default=False)
    score = Column(Integer, default=0)
    attempts = Column(Integer, default=0)
    completed_at = Column(DateTime(timezone=True))
    user = relationship('User', back_populates='progress')
    lesson = relationship('Lesson', back_populates='progress')
    __table_args__ = (UniqueConstraint('user_id', 'lesson_id', name='uq_progress_user_lesson'),)

class Puzzle(Base):
    __tablename__ = "puzzles"
    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    fen = Column(String(100), nullable=False)
    prompt = Column(String(500), nullable=False)
    answer = Column(String(50), nullable=False)
    explanation = Column(Text, nullable=True)
    points = Column(Integer, default=10, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

class PuzzleAttempt(Base):
    __tablename__ = "puzzle_attempts"
    id = Column(Integer, primary_key=True)
    puzzle_id = Column(Integer, ForeignKey("puzzles.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    answer = Column(String(50), nullable=False)
    correct = Column(Boolean, default=False, nullable=False)
    points = Column(Integer, default=0, nullable=False)

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    prompt = Column(String(500), nullable=False)
    option_a = Column(String(200), nullable=False)
    option_b = Column(String(200), nullable=False)
    option_c = Column(String(200), nullable=False)
    option_d = Column(String(200), nullable=False)
    correct_option = Column(String(1), nullable=False)
    explanation = Column(Text, nullable=True)
    points = Column(Integer, default=10, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(Integer, primary_key=True)
    quiz_question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    selected_option = Column(String(1), nullable=False)
    correct = Column(Boolean, default=False, nullable=False)
    points = Column(Integer, default=0, nullable=False)

class ChildProfile(Base):
    __tablename__ = "child_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    display_name = Column(String(120), nullable=True)
    avatar = Column(String(16), nullable=False, default="🦁")
    age = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserStats(Base):
    __tablename__ = "user_stats"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    total_stars = Column(Integer, nullable=False, default=0)
    current_streak = Column(Integer, nullable=False, default=0)
    longest_streak = Column(Integer, nullable=False, default=0)
    last_activity_date = Column(Date, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Badge(Base):
    __tablename__ = "badges"
    id = Column(Integer, primary_key=True)
    code = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(16), nullable=False, default="🏅")
    criteria_type = Column(String(32), nullable=False)
    criteria_value = Column(Integer, nullable=False)

class UserBadge(Base):
    __tablename__ = "user_badges"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    badge_id = Column(Integer, ForeignKey("badges.id", ondelete="CASCADE"), nullable=False, index=True)
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
    badge = relationship("Badge")
    __table_args__ = (UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),)


class MasterGame(Base):
    __tablename__ = 'master_games'
    id = Column(Integer, primary_key=True)
    external_id = Column(String(64), unique=True, nullable=True, index=True)
    white = Column(String(120), nullable=False)
    black = Column(String(120), nullable=False)
    year = Column(String(16), nullable=True)
    opening = Column(String(180), nullable=True)
    moves = Column(Text, nullable=False)
    annotation = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

class TrainingPlanProgress(Base):
    """
    Per-user checkmarks against the static 3-Year Structured Training Plan
    (backend/app/data/training_plan.json, migrated from V16's studyPlan.js).
    The plan content itself is read-only reference data, not DB rows, so —
    unlike the Track/Course/Lesson hierarchy — there is nothing to publish
    or author here. Only a user's checkbox state is persisted, one row per
    checked item, keyed the same way V16 did it client-side
    (e.g. 'y1-m1-g0' for year 1 / month 1 / weekly-goal 0,
    'y1-m1-s1' for year 1 / month 1 / daily-session 'session1').
    """
    __tablename__ = 'training_plan_progress'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    item_key = Column(String(64), nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint('user_id', 'item_key', name='uq_training_plan_progress_user_item'),)


class ParentStudentLink(Base):
    __tablename__ = 'parent_student_links'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    parent = relationship('User', foreign_keys=[parent_id], back_populates='parent_links')
    student = relationship('User', foreign_keys=[student_id], back_populates='coach_links')
    __table_args__ = (UniqueConstraint('parent_id','student_id',name='uq_parent_student'),)
