from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MasterGame
from app.schemas import MasterGame as MasterGameSchema, MasterGameCreate
from app.core.security import require_roles

router = APIRouter(prefix='/master-games', tags=['master-games'])

@router.get('/', response_model=list[MasterGameSchema])
def list_master_games(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(MasterGame).filter(MasterGame.is_active.is_(True)).order_by(MasterGame.id).offset(skip).limit(min(limit, 100)).all()

@router.get('/{master_game_id}', response_model=MasterGameSchema)
def get_master_game(master_game_id: int, db: Session = Depends(get_db)):
    game = db.query(MasterGame).filter(MasterGame.id == master_game_id, MasterGame.is_active.is_(True)).first()
    if not game: raise HTTPException(404, 'Master game not found')
    return game

@router.post('/', response_model=MasterGameSchema, status_code=201)
def create_master_game(data: MasterGameCreate, db: Session = Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    obj = MasterGame(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj); return obj
