from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ChildProfile
from app.schemas import ChildProfileIn, ChildProfileOut
from app.core.security import get_current_user

router = APIRouter(prefix="/me", tags=["profile"])

DEFAULT_AVATAR = "🦁"


@router.get("/profile", response_model=ChildProfileOut)
def get_profile(db: Session = Depends(get_db), user=Depends(get_current_user)):
    profile = db.query(ChildProfile).filter_by(user_id=user.id).first()
    if not profile:
        return {"display_name": None, "avatar": DEFAULT_AVATAR, "age": None}
    return profile


@router.put("/profile", response_model=ChildProfileOut)
def update_profile(payload: ChildProfileIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    profile = db.query(ChildProfile).filter_by(user_id=user.id).first()
    if not profile:
        profile = ChildProfile(user_id=user.id, avatar=payload.avatar or DEFAULT_AVATAR)
        db.add(profile)
    if payload.display_name is not None:
        profile.display_name = payload.display_name
    if payload.avatar is not None:
        profile.avatar = payload.avatar
    if payload.age is not None:
        profile.age = payload.age
    db.commit()
    db.refresh(profile)
    return profile
