from app.database import SessionLocal
from app.models import Track, Course, Chapter, Lesson

def seed():
    db=SessionLocal()
    try:
        if db.query(Track).first(): return
        track=Track(name='Young Champions',slug='young-champions',description='A playful path from first moves to confident chess.',icon='🦁',age_min=5,age_max=8)
        db.add(track); db.flush()
        course=Course(track_id=track.id,name='Chess Starters',slug='chess-starters',description='Learn the board, pieces and your first smart moves.',duration_months=6,is_published=True)
        db.add(course); db.flush()
        chapter=Chapter(course_id=course.id,title='Meet the Chessboard',description='Your first chess adventure.',order=1,is_published=True); db.add(chapter); db.flush()
        db.add_all([Lesson(chapter_id=chapter.id,title='The Chessboard',description='Learn the 64 squares.',content='A chessboard has 64 squares arranged in 8 rows and 8 columns.',order=1,is_published=True),Lesson(chapter_id=chapter.id,title='Meet the Pieces',description='Discover how every piece moves.',content='Kings, queens, rooks, bishops, knights and pawns each have a special move.',order=2,is_published=True)])
        db.commit()
    finally: db.close()
if __name__=='__main__': seed()
