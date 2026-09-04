from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Literal["student", "parent"] = "student"

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; username: str; email: EmailStr; full_name: Optional[str]; role: str; is_active: bool; created_at: datetime

class Token(BaseModel): access_token: str; token_type: str

class TrackBase(BaseModel):
    name: str; slug: str; description: Optional[str] = None; icon: str = '♟️'; age_min: Optional[int] = None; age_max: Optional[int] = None
class TrackCreate(TrackBase): pass
class Track(TrackBase):
    model_config = ConfigDict(from_attributes=True)
    id: int; is_active: bool

class CourseBase(BaseModel):
    track_id: int; name: str; slug: str; description: Optional[str] = None; fee: int = 0; duration_months: int = 6
class CourseCreate(CourseBase): pass
class Course(CourseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int; is_published: bool; created_at: datetime

class ChapterBase(BaseModel): course_id: int; title: str; description: Optional[str] = None; order: int = 0
class ChapterCreate(ChapterBase): pass
class Chapter(ChapterBase):
    model_config = ConfigDict(from_attributes=True)
    id: int; is_published: bool

class LessonBase(BaseModel):
    chapter_id: int; title: str; description: Optional[str] = None; content: Optional[str] = None; order: int = 0; lesson_type: str = 'lesson'
class LessonCreate(LessonBase): pass
class Lesson(LessonBase):
    model_config = ConfigDict(from_attributes=True)
    id: int; is_published: bool

class LessonDetail(Lesson):
    course_id: int

class EnrollmentCreate(BaseModel):
    course_id: int
    # Only required when the target course has a fee > 0 (no payment
    # integration yet — see Coupon). Free courses ignore this field.
    coupon_code: Optional[str] = None
class Enrollment(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; user_id: int; course_id: int; status: str; coupon_code: Optional[str] = None; enrolled_at: datetime

class CouponOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; code: str; description: Optional[str] = None; is_active: bool
    max_redemptions: Optional[int] = None; times_redeemed: int

class CouponCreate(BaseModel):
    code: str
    description: Optional[str] = None
    max_redemptions: Optional[int] = None

class CouponUpdate(BaseModel):
    is_active: Optional[bool] = None
    max_redemptions: Optional[int] = None
    description: Optional[str] = None

class ProgressItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    lesson_id: int; completed: bool; score: int; attempts: int

class CourseProgress(BaseModel):
    course_id: int; total_lessons: int; completed_lessons: int; percent: int

class PuzzleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; lesson_id: int; fen: str; prompt: str; points: int

class PuzzleAttemptIn(BaseModel):
    answer: str

class PuzzleAttemptOut(BaseModel):
    correct: bool; points: int; explanation: Optional[str] = None; new_badges: list[str] = []

class PuzzleAdmin(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; lesson_id: int; fen: str; prompt: str; answer: str; explanation: Optional[str] = None; points: int; is_active: bool

class PuzzleCreate(BaseModel):
    lesson_id: int; fen: str; prompt: str; answer: str; explanation: Optional[str] = None; points: int = 10

class PuzzleUpdate(BaseModel):
    fen: Optional[str] = None; prompt: Optional[str] = None; answer: Optional[str] = None; explanation: Optional[str] = None; points: Optional[int] = None; is_active: Optional[bool] = None

class QuizQuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; lesson_id: int; prompt: str; option_a: str; option_b: str; option_c: str; option_d: str; points: int

class QuizQuestionAdmin(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; lesson_id: int; prompt: str; option_a: str; option_b: str; option_c: str; option_d: str; correct_option: str; explanation: Optional[str] = None; points: int; is_active: bool

class QuizQuestionCreate(BaseModel):
    lesson_id: int; prompt: str; option_a: str; option_b: str; option_c: str; option_d: str; correct_option: str; explanation: Optional[str] = None; points: int = 10

class QuizQuestionUpdate(BaseModel):
    prompt: Optional[str] = None; option_a: Optional[str] = None; option_b: Optional[str] = None; option_c: Optional[str] = None; option_d: Optional[str] = None; correct_option: Optional[str] = None; explanation: Optional[str] = None; points: Optional[int] = None; is_active: Optional[bool] = None

class QuizAttemptIn(BaseModel):
    selected_option: str

class QuizAttemptOut(BaseModel):
    correct: bool; points: int; explanation: Optional[str] = None; new_badges: list[str] = []

class ChildProfileIn(BaseModel):
    display_name: Optional[str] = None; avatar: Optional[str] = None; age: Optional[int] = None

class ChildProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    display_name: Optional[str] = None; avatar: str; age: Optional[int] = None

class UserStatsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    total_stars: int; current_streak: int; longest_streak: int

class BadgeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str; name: str; description: Optional[str] = None; icon: str; criteria_type: str; criteria_value: int

class EarnedBadgeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    badge: BadgeOut; earned_at: datetime

class AdminLessonOut(BaseModel):
    id: int; title: str; lesson_type: str; chapter_title: str; course_name: str


class MasterGameBase(BaseModel):
    white: str; black: str; year: Optional[str] = None; opening: Optional[str] = None
    moves: str; annotation: Optional[str] = None; source: Optional[str] = None
class MasterGameCreate(MasterGameBase):
    external_id: Optional[str] = None
class MasterGame(MasterGameBase):
    model_config = ConfigDict(from_attributes=True)
    id: int; external_id: Optional[str] = None; is_active: bool

class StudentSummary(BaseModel):
    id: int; username: str; full_name: Optional[str]; total_stars: int = 0; current_streak: int = 0; completed_lessons: int = 0; total_lessons: int = 0; percent: int = 0
class ParentLinkCreate(BaseModel):
    parent_id: int
    student_id: int
class RecommendationOut(BaseModel):
    course_id: int; course_name: str; reason: str; priority: int

class TrainingPlanProgressOut(BaseModel):
    completed_items: list[str]

class TrainingPlanYearStats(BaseModel):
    year: str; title: str; total_items: int; completed_items: int; percent: int
