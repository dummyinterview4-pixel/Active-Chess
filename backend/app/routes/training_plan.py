import json
import re
from functools import lru_cache
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import TrainingPlanProgress
from app.schemas import TrainingPlanProgressOut, TrainingPlanYearStats
from app.core.security import get_current_user

router = APIRouter(tags=['training-plan'])

DATA_FILE = Path(__file__).resolve().parents[1] / 'data' / 'training_plan.json'

# Item keys are only ever 'm{month}-g{index}' (a weekly goal) or
# 'm{month}-session{N}' (a daily session, N 1-4), month 1-36. Validated
# here so a bad key can't create junk progress rows.
_ITEM_KEY_RE = re.compile(r'^m([1-9]|[12]\d|3[0-6])-(g\d{1,2}|session\d)$')


@lru_cache
def _load_plan() -> dict:
    """
    Loads the static 3-Year Structured Training Plan content, migrated
    verbatim from V16's src/data/studyPlan.js (threeYearPlan, dailyPlans,
    weeklySchedules). This is read-only reference content — there is no
    admin/authoring UI for it, matching how it worked in V16.
    """
    with DATA_FILE.open('r', encoding='utf-8') as fh:
        return json.load(fh)


@router.get('/training-plan')
def get_training_plan():
    """Full 3-Year Structured Training Plan content. Public reference
    content — no enrollment or login required, matching V16."""
    return _load_plan()


@router.get('/training-plan/progress', response_model=TrainingPlanProgressOut)
def get_training_plan_progress(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(TrainingPlanProgress).filter_by(user_id=user.id).all()
    return {'completed_items': [r.item_key for r in rows]}


@router.put('/training-plan/progress/{item_key}', status_code=204)
def mark_training_plan_item(item_key: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not _ITEM_KEY_RE.match(item_key):
        raise HTTPException(400, 'Invalid training plan item key')
    exists = db.query(TrainingPlanProgress).filter_by(user_id=user.id, item_key=item_key).first()
    if not exists:
        db.add(TrainingPlanProgress(user_id=user.id, item_key=item_key))
        db.commit()


@router.delete('/training-plan/progress/{item_key}', status_code=204)
def unmark_training_plan_item(item_key: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db.query(TrainingPlanProgress).filter_by(user_id=user.id, item_key=item_key).delete()
    db.commit()


@router.get('/training-plan/stats', response_model=list[TrainingPlanYearStats])
def training_plan_stats(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Per-year completion percentage, mirroring V16's phaseStats."""
    plan = _load_plan()['threeYearPlan']
    done = {
        r.item_key for r in db.query(TrainingPlanProgress).filter_by(user_id=user.id).all()
    }
    stats = []
    for year_key in ('year1', 'year2', 'year3'):
        year = plan[year_key]
        total = 0
        completed = 0
        for month in year['months']:
            m = month['month']
            goal_keys = [f'm{m}-g{i}' for i in range(len(month.get('weeklyGoals', [])))]
            session_keys = [f'm{m}-{k}' for k in (month.get('dailyPlan') or {}).keys()]
            keys = goal_keys + session_keys
            total += len(keys)
            completed += sum(1 for k in keys if k in done)
        stats.append({
            'year': year_key,
            'title': year['title'],
            'total_items': total,
            'completed_items': completed,
            'percent': round(completed / total * 100) if total else 0,
        })
    return stats
