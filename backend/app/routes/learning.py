from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Track, Course, Chapter, Lesson, Enrollment, LessonProgress, Coupon
from app.schemas import (
    Track as TrackSchema, Course as CourseSchema, Chapter as ChapterSchema,
    Lesson as LessonSchema, LessonDetail, Enrollment as EnrollmentSchema,
    EnrollmentCreate, ProgressItem, CourseProgress,
)
from app.core.security import get_current_user
from app.services.gamification import record_activity

router = APIRouter()


def _require_enrollment(db: Session, user_id: int, course_id: int):
    return db.query(Enrollment).filter_by(
        user_id=user_id, course_id=course_id, status='active'
    ).first()


@router.get('/tracks', response_model=list[TrackSchema])
def tracks(db: Session = Depends(get_db)):
    return db.query(Track).filter(Track.is_active.is_(True)).order_by(Track.id).all()


@router.get('/courses', response_model=list[CourseSchema])
def courses(track_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Course).filter(Course.is_published.is_(True))
    if track_id is not None:
        q = q.filter(Course.track_id == track_id)
    return q.order_by(Course.id).all()


@router.get('/courses/{course_id}', response_model=CourseSchema)
def course(course_id: int, db: Session = Depends(get_db)):
    obj = db.query(Course).filter(
        Course.id == course_id, Course.is_published.is_(True)
    ).first()
    if not obj:
        raise HTTPException(404, 'Course not found')
    return obj


@router.get('/courses/{course_id}/chapters', response_model=list[ChapterSchema])
def chapters(course_id: int, db: Session = Depends(get_db)):
    if not db.query(Course).filter(
        Course.id == course_id, Course.is_published.is_(True)
    ).first():
        raise HTTPException(404, 'Course not found')
    return db.query(Chapter).filter(
        Chapter.course_id == course_id, Chapter.is_published.is_(True)
    ).order_by(Chapter.order).all()


@router.get('/chapters/{chapter_id}/lessons', response_model=list[LessonSchema])
def lessons(chapter_id: int, db: Session = Depends(get_db)):
    if not db.query(Chapter).filter(
        Chapter.id == chapter_id, Chapter.is_published.is_(True)
    ).first():
        raise HTTPException(404, 'Chapter not found')
    return db.query(Lesson).filter(
        Lesson.chapter_id == chapter_id, Lesson.is_published.is_(True)
    ).order_by(Lesson.order).all()


@router.get('/lessons/{lesson_id}', response_model=LessonDetail)
def lesson(lesson_id: int, db: Session = Depends(get_db)):
    obj = db.query(Lesson).filter(
        Lesson.id == lesson_id, Lesson.is_published.is_(True)
    ).first()
    if not obj:
        raise HTTPException(404, 'Lesson not found')
    chapter = db.query(Chapter).filter(Chapter.id == obj.chapter_id).first()
    return {
        'id': obj.id,
        'chapter_id': obj.chapter_id,
        'course_id': chapter.course_id,
        'title': obj.title,
        'description': obj.description,
        'content': obj.content,
        'order': obj.order,
        'lesson_type': obj.lesson_type,
        'is_published': obj.is_published,
    }


def _redeem_coupon(db: Session, code: str | None) -> Coupon | None:
    """Validate and redeem a coupon for a paid enrollment. Raises 400 on any
    invalid/exhausted/missing code. Returns the redeemed Coupon row (caller
    is responsible for committing alongside the enrollment)."""
    if not code or not code.strip():
        raise HTTPException(400, 'This course requires a coupon code to enroll for free — payment isn\'t live yet.')
    coupon = db.query(Coupon).filter(
        Coupon.code == code.strip().upper()
    ).with_for_update().first()
    if not coupon or not coupon.is_active:
        raise HTTPException(400, "That coupon code isn't valid.")
    if coupon.max_redemptions is not None and coupon.times_redeemed >= coupon.max_redemptions:
        raise HTTPException(400, 'That coupon code has already reached its redemption limit.')
    coupon.times_redeemed += 1
    return coupon


@router.post('/enrollments', response_model=EnrollmentSchema, status_code=201)
def enroll(data: EnrollmentCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    course_obj = db.query(Course).filter(
        Course.id == data.course_id, Course.is_published.is_(True)
    ).first()
    if not course_obj:
        raise HTTPException(404, 'Course not found')

    # Paid courses have no billing integration yet, so a valid coupon
    # stands in for payment (see the Coupon model). Free courses (fee==0)
    # never need one.
    coupon = None
    if course_obj.fee and course_obj.fee > 0:
        coupon = _redeem_coupon(db, data.coupon_code)

    existing = db.query(Enrollment).filter_by(
        user_id=user.id, course_id=data.course_id
    ).first()
    if existing:
        if existing.status != 'active':
            existing.status = 'active'
            existing.completed_at = None
            if coupon:
                existing.coupon_code = coupon.code
            db.commit()
            db.refresh(existing)
            return existing
        raise HTTPException(400, 'Already enrolled')
    obj = Enrollment(user_id=user.id, course_id=data.course_id, coupon_code=coupon.code if coupon else None)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get('/me/enrollments', response_model=list[EnrollmentSchema])
def my_enrollments(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Enrollment).filter_by(
        user_id=user.id
    ).order_by(Enrollment.enrolled_at.desc()).all()


@router.get('/me/progress', response_model=list[ProgressItem])
def my_progress(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(LessonProgress).filter_by(user_id=user.id).all()


@router.get('/courses/{course_id}/progress', response_model=CourseProgress)
def course_progress(course_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not db.query(Course).filter(
        Course.id == course_id, Course.is_published.is_(True)
    ).first():
        raise HTTPException(404, 'Course not found')
    if not _require_enrollment(db, user.id, course_id):
        raise HTTPException(403, 'Enroll in this course first')
    lessons = db.query(Lesson).join(Chapter).filter(
        Chapter.course_id == course_id,
        Chapter.is_published.is_(True),
        Lesson.is_published.is_(True),
    ).all()
    lesson_ids = {x.id for x in lessons}
    completed = db.query(LessonProgress).filter(
        LessonProgress.user_id == user.id,
        LessonProgress.lesson_id.in_(lesson_ids),
        LessonProgress.completed.is_(True),
    ).count() if lesson_ids else 0
    total = len(lessons)
    return CourseProgress(
        course_id=course_id,
        total_lessons=total,
        completed_lessons=completed,
        percent=round(completed / total * 100) if total else 0,
    )


@router.post('/lessons/{lesson_id}/complete', response_model=ProgressItem)
def complete(lesson_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    lesson_obj = db.query(Lesson).filter(
        Lesson.id == lesson_id, Lesson.is_published.is_(True)
    ).first()
    if not lesson_obj:
        raise HTTPException(404, 'Lesson not found')
    chapter = db.query(Chapter).filter_by(id=lesson_obj.chapter_id).first()
    if not chapter or not _require_enrollment(db, user.id, chapter.course_id):
        raise HTTPException(403, 'Enroll in this course first')

    row = db.query(LessonProgress).filter_by(
        user_id=user.id, lesson_id=lesson_id
    ).first()
    if not row:
        row = LessonProgress(user_id=user.id, lesson_id=lesson_id)
        db.add(row)

    already_completed = bool(row.completed)
    row.completed = True
    row.completed_at = datetime.now(timezone.utc)
    row.attempts = (row.attempts or 0) + 1

    # Flush so gamification badge queries can see the newly completed lesson,
    # then let record_activity commit the complete workflow once.
    db.flush()
    if not already_completed:
        record_activity(db, user, stars=10, commit=False)
    db.commit()
    db.refresh(row)
    return row


@router.get('/me/next-lesson')
def next_lesson(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Return the first incomplete lesson across the user's active enrollments."""
    enrollments = db.query(Enrollment).filter_by(
        user_id=user.id, status='active'
    ).order_by(Enrollment.enrolled_at).all()
    for enrollment in enrollments:
        lessons = db.query(Lesson).join(Chapter).filter(
            Chapter.course_id == enrollment.course_id,
            Chapter.is_published.is_(True),
            Lesson.is_published.is_(True),
        ).order_by(Chapter.order, Lesson.order).all()
        if not lessons:
            continue
        done_ids = {
            p.lesson_id for p in db.query(LessonProgress).filter(
                LessonProgress.user_id == user.id,
                LessonProgress.lesson_id.in_([l.id for l in lessons]),
                LessonProgress.completed.is_(True),
            ).all()
        }
        for item in lessons:
            if item.id not in done_ids:
                return {
                    'course_id': enrollment.course_id,
                    'lesson_id': item.id,
                    'title': item.title,
                }
    return None
