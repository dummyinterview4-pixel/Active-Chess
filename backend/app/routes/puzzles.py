from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Puzzle, PuzzleAttempt
from app.schemas import PuzzleOut, PuzzleAttemptIn, PuzzleAttemptOut
from app.core.security import get_current_user
from app.services.gamification import record_activity

router=APIRouter(prefix="/puzzles",tags=["puzzles"])

@router.get("/lesson/{lesson_id}",response_model=list[PuzzleOut])
def lesson_puzzles(lesson_id:int,db:Session=Depends(get_db),user=Depends(get_current_user)):
    return db.query(Puzzle).filter(Puzzle.lesson_id==lesson_id,Puzzle.is_active.is_(True)).order_by(Puzzle.id).all()

@router.post("/{puzzle_id}/attempt",response_model=PuzzleAttemptOut)
def attempt(puzzle_id:int,payload:PuzzleAttemptIn,db:Session=Depends(get_db),user=Depends(get_current_user)):
    p=db.query(Puzzle).filter(Puzzle.id==puzzle_id,Puzzle.is_active.is_(True)).first()
    if not p: raise HTTPException(404,"Puzzle not found")
    correct=payload.answer.strip().lower()==p.answer.strip().lower()
    pts=p.points if correct else 0
    db.add(PuzzleAttempt(puzzle_id=p.id,user_id=user.id,answer=payload.answer,correct=correct,points=pts))
    db.commit()
    new_badges=[]
    if correct:
        _,new_badges=record_activity(db,user,stars=pts)
    return {"correct":correct,"points":pts,"explanation":p.explanation,"new_badges":[b.name for b in new_badges]}
