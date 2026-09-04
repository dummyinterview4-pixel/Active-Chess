from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.core.security import get_current_user, require_roles
from app.models import User, ParentStudentLink, LessonProgress, Lesson, Chapter, Course, Enrollment, UserStats
from app.schemas import StudentSummary, ParentLinkCreate, RecommendationOut

router = APIRouter(tags=['dashboards'])

def _summary(db, user):
    rows = db.query(LessonProgress).filter(LessonProgress.user_id == user.id, LessonProgress.completed.is_(True)).count()
    total = db.query(Lesson).join(Chapter).join(Course).filter(Course.is_published.is_(True), Chapter.is_published.is_(True), Lesson.is_published.is_(True)).count()
    stats = db.query(UserStats).filter_by(user_id=user.id).first()
    percent = round(rows*100/total) if total else 0
    return StudentSummary(id=user.id, username=user.username, full_name=user.full_name, total_stars=stats.total_stars if stats else 0, current_streak=stats.current_streak if stats else 0, completed_lessons=rows, total_lessons=total, percent=percent)

@router.get('/coach/students', response_model=list[StudentSummary])
def coach_students(db: Session = Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    return [_summary(db,u) for u in db.query(User).filter(User.role=='student', User.is_active.is_(True)).order_by(User.username).all()]

@router.post('/coach/parent-links', status_code=201)
def link_parent(data: ParentLinkCreate, db: Session = Depends(get_db), _=Depends(require_roles('admin','coach','trainer'))):
    parent=db.query(User).filter(User.id==data.parent_id, User.role=='parent', User.is_active.is_(True)).first()
    student=db.query(User).filter(User.id==data.student_id, User.role=='student', User.is_active.is_(True)).first()
    if not parent: raise HTTPException(404,'Parent account not found')
    if not student: raise HTTPException(404,'Student not found')
    link=db.query(ParentStudentLink).filter_by(parent_id=parent.id, student_id=student.id).first()
    if link: return {'id':link.id,'status':'already_linked'}
    link=ParentStudentLink(parent_id=parent.id, student_id=student.id); db.add(link); db.commit(); db.refresh(link)
    return {'id':link.id,'status':'linked'}

@router.get('/parent/students', response_model=list[StudentSummary])
def parent_students(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role!='parent': raise HTTPException(403,'Parent role required')
    students=(db.query(User).join(ParentStudentLink, ParentStudentLink.student_id==User.id).filter(ParentStudentLink.parent_id==user.id).all())
    return [_summary(db,u) for u in students]

@router.get('/me/recommendations', response_model=list[RecommendationOut])
def recommendations(db: Session = Depends(get_db), user=Depends(get_current_user)):
    completed_courses=set()
    for course in db.query(Course).filter(Course.is_published.is_(True)).all():
        total=db.query(Lesson).join(Chapter).filter(Chapter.course_id==course.id, Lesson.is_published.is_(True)).count()
        done=db.query(LessonProgress).join(Lesson).join(Chapter).filter(LessonProgress.user_id==user.id, LessonProgress.completed.is_(True), Chapter.course_id==course.id).count()
        if total and done>=total: completed_courses.add(course.id)
    out=[]
    for course in db.query(Course).filter(Course.is_published.is_(True)).order_by(Course.id):
        if course.id in completed_courses: continue
        enrolled=db.query(Enrollment).filter_by(user_id=user.id,course_id=course.id,status='active').first()
        reason='Continue your current course' if enrolled else 'A good next course for your chess journey'
        out.append(RecommendationOut(course_id=course.id,course_name=course.name,reason=reason,priority=0 if enrolled else 1))
    return sorted(out,key=lambda x:(x.priority,x.course_id))[:3]
