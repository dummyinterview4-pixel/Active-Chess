from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Track, Course, Chapter, Lesson, Puzzle, QuizQuestion, Coupon
from app.schemas import (
    TrackCreate, Track as TrackSchema, CourseCreate, Course as CourseSchema,
    ChapterCreate, Chapter as ChapterSchema, LessonCreate, Lesson as LessonSchema,
    AdminLessonOut, PuzzleAdmin, PuzzleCreate, PuzzleUpdate,
    QuizQuestionAdmin, QuizQuestionCreate, QuizQuestionUpdate,
    CouponOut, CouponCreate, CouponUpdate,
)
from app.core.security import require_roles
router=APIRouter(prefix='/admin', tags=['admin'])
@router.post('/tracks', response_model=TrackSchema, status_code=201)
def create_track(data:TrackCreate, db:Session=Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    obj=Track(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj); return obj
@router.post('/courses', response_model=CourseSchema, status_code=201)
def create_course(data:CourseCreate, db:Session=Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    obj=Course(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj); return obj
@router.post('/chapters', response_model=ChapterSchema, status_code=201)
def create_chapter(data:ChapterCreate, db:Session=Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    obj=Chapter(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj); return obj
@router.post('/lessons', response_model=LessonSchema, status_code=201)
def create_lesson(data:LessonCreate, db:Session=Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    obj=Lesson(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj); return obj


@router.patch('/tracks/{track_id}/publish', response_model=TrackSchema)
def toggle_track(track_id: int, db: Session = Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    obj = db.query(Track).filter(Track.id == track_id).first()
    if not obj:
        from fastapi import HTTPException
        raise HTTPException(404, 'Track not found')
    obj.is_active = not obj.is_active
    db.commit(); db.refresh(obj)
    return obj

@router.patch('/courses/{course_id}/publish', response_model=CourseSchema)
def toggle_course(course_id: int, db: Session = Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    obj = db.query(Course).filter(Course.id == course_id).first()
    if not obj:
        from fastapi import HTTPException
        raise HTTPException(404, 'Course not found')
    obj.is_published = not obj.is_published
    db.commit(); db.refresh(obj)
    return obj

@router.patch('/chapters/{chapter_id}/publish', response_model=ChapterSchema)
def toggle_chapter(chapter_id: int, db: Session = Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    obj = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not obj:
        from fastapi import HTTPException
        raise HTTPException(404, 'Chapter not found')
    obj.is_published = not obj.is_published
    db.commit(); db.refresh(obj)
    return obj

@router.patch('/lessons/{lesson_id}/publish', response_model=LessonSchema)
def toggle_lesson(lesson_id: int, db: Session = Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    obj = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not obj:
        from fastapi import HTTPException
        raise HTTPException(404, 'Lesson not found')
    obj.is_published = not obj.is_published
    db.commit(); db.refresh(obj)
    return obj


@router.get('/lessons', response_model=list[AdminLessonOut])
def list_all_lessons(db: Session = Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    rows = (db.query(Lesson, Chapter, Course)
            .join(Chapter, Lesson.chapter_id == Chapter.id)
            .join(Course, Chapter.course_id == Course.id)
            .order_by(Course.name, Chapter.order, Lesson.order).all())
    return [
        {"id": l.id, "title": l.title, "lesson_type": l.lesson_type, "chapter_title": ch.title, "course_name": c.name}
        for l, ch, c in rows
    ]


@router.get('/puzzles', response_model=list[PuzzleAdmin])
def list_puzzles(lesson_id: int | None = None, db: Session = Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    q = db.query(Puzzle)
    if lesson_id is not None:
        q = q.filter(Puzzle.lesson_id == lesson_id)
    return q.order_by(Puzzle.id).all()


@router.post('/puzzles', response_model=PuzzleAdmin, status_code=201)
def create_puzzle(data: PuzzleCreate, db: Session = Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    obj = Puzzle(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@router.put('/puzzles/{puzzle_id}', response_model=PuzzleAdmin)
def update_puzzle(puzzle_id: int, data: PuzzleUpdate, db: Session = Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    obj = db.query(Puzzle).filter(Puzzle.id == puzzle_id).first()
    if not obj:
        raise HTTPException(404, 'Puzzle not found')
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj


@router.delete('/puzzles/{puzzle_id}', status_code=204)
def delete_puzzle(puzzle_id: int, db: Session = Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    obj = db.query(Puzzle).filter(Puzzle.id == puzzle_id).first()
    if not obj:
        raise HTTPException(404, 'Puzzle not found')
    db.delete(obj); db.commit()
    return None


@router.get('/quizzes', response_model=list[QuizQuestionAdmin])
def list_quiz_questions(lesson_id: int | None = None, db: Session = Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    q = db.query(QuizQuestion)
    if lesson_id is not None:
        q = q.filter(QuizQuestion.lesson_id == lesson_id)
    return q.order_by(QuizQuestion.id).all()


@router.post('/quizzes', response_model=QuizQuestionAdmin, status_code=201)
def create_quiz_question(data: QuizQuestionCreate, db: Session = Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    obj = QuizQuestion(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@router.put('/quizzes/{question_id}', response_model=QuizQuestionAdmin)
def update_quiz_question(question_id: int, data: QuizQuestionUpdate, db: Session = Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    obj = db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()
    if not obj:
        raise HTTPException(404, 'Quiz question not found')
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj


@router.delete('/quizzes/{question_id}', status_code=204)
def delete_quiz_question(question_id: int, db: Session = Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    obj = db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()
    if not obj:
        raise HTTPException(404, 'Quiz question not found')
    db.delete(obj); db.commit()
    return None


# --- Coupons ---
# Admin-only (not coach/trainer): coupons stand in for real billing on paid
# courses, so managing them is treated like a payments/finance permission,
# not a content-authoring one.

@router.get('/coupons', response_model=list[CouponOut])
def list_coupons(db: Session = Depends(get_db), _=Depends(require_roles('admin'))):
    return db.query(Coupon).order_by(Coupon.created_at.desc()).all()


@router.post('/coupons', response_model=CouponOut, status_code=201)
def create_coupon(data: CouponCreate, db: Session = Depends(get_db), _=Depends(require_roles('admin'))):
    code = data.code.strip().upper()
    if not code:
        raise HTTPException(400, 'Coupon code is required')
    if db.query(Coupon).filter(Coupon.code == code).first():
        raise HTTPException(400, 'A coupon with that code already exists')
    obj = Coupon(code=code, description=data.description, max_redemptions=data.max_redemptions)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@router.patch('/coupons/{coupon_id}', response_model=CouponOut)
def update_coupon(coupon_id: int, data: CouponUpdate, db: Session = Depends(get_db), _=Depends(require_roles('admin'))):
    obj = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not obj:
        raise HTTPException(404, 'Coupon not found')
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj
