def test_learning_routes_source_contains_core_endpoints():
    source = open('app/routes/learning.py', encoding='utf-8').read()
    assert "'/courses/{course_id}/progress'" in source
    assert "'/lessons/{lesson_id}/complete'" in source
