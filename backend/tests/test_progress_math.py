from app.schemas import CourseProgress

def test_course_progress_schema():
    item = CourseProgress(course_id=3, total_lessons=10, completed_lessons=4, percent=40)
    assert item.percent == 40
    assert item.completed_lessons <= item.total_lessons
