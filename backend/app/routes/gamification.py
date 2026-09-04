from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UserStats, Badge, UserBadge
from app.schemas import UserStatsOut, BadgeOut, EarnedBadgeOut
from app.core.security import get_current_user

router = APIRouter(tags=["gamification"])


@router.get("/me/stats", response_model=UserStatsOut)
def my_stats(db: Session = Depends(get_db), user=Depends(get_current_user)):
    stats = db.query(UserStats).filter_by(user_id=user.id).first()
    if not stats:
        return {"total_stars": 0, "current_streak": 0, "longest_streak": 0}
    return stats


@router.get("/badges", response_model=list[BadgeOut])
def all_badges(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Badge).order_by(Badge.criteria_type, Badge.criteria_value).all()


@router.get("/me/badges", response_model=list[EarnedBadgeOut])
def my_badges(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(UserBadge).filter_by(user_id=user.id).order_by(UserBadge.earned_at.desc()).all()
