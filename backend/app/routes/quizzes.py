from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import QuizQuestion, QuizAttempt
from app.schemas import QuizQuestionOut, QuizAttemptIn, QuizAttemptOut
from app.core.security import get_current_user
from app.services.gamification import record_activity

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.get("/lesson/{lesson_id}", response_model=list[QuizQuestionOut])
def lesson_quizzes(lesson_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(QuizQuestion).filter(QuizQuestion.lesson_id == lesson_id, QuizQuestion.is_active.is_(True)).order_by(QuizQuestion.id).all()


@router.post("/{question_id}/attempt", response_model=QuizAttemptOut)
def attempt(question_id: int, payload: QuizAttemptIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(QuizQuestion).filter(QuizQuestion.id == question_id, QuizQuestion.is_active.is_(True)).first()
    if not q:
        raise HTTPException(404, "Quiz question not found")
    selected = payload.selected_option.strip().lower()
    correct = selected == q.correct_option.strip().lower()
    pts = q.points if correct else 0
    db.add(QuizAttempt(quiz_question_id=q.id, user_id=user.id, selected_option=selected, correct=correct, points=pts))
    db.commit()
    new_badges = []
    if correct:
        _, new_badges = record_activity(db, user, stars=pts)
    return {"correct": correct, "points": pts, "explanation": q.explanation, "new_badges": [b.name for b in new_badges]}
