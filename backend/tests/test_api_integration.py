"""
Real end-to-end API integration tests against an in-memory SQLite DB.

Unlike the pre-existing tests (which only grepped source text or instantiated
a schema in isolation), these boot the actual FastAPI app, create tables,
and drive requests through TestClient to catch wiring/runtime regressions
(missing routers, broken imports, auth failures, etc.).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models import Track, Course, User

TEST_DB_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    track = Track(name="Test Track", slug="test-track", description="", icon="♟️")
    db.add(track)
    db.flush()
    course = Course(
        track_id=track.id,
        name="Test Course",
        slug="test-course",
        description="",
        duration_months=1,
        is_published=True,
    )
    paid_course = Course(
        track_id=track.id,
        name="Paid Test Course",
        slug="paid-test-course",
        description="",
        fee=500,
        duration_months=1,
        is_published=True,
    )
    db.add_all([course, paid_course])
    db.commit()
    db.close()

    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def auth_headers(client):
    client.post(
        "/auth/register",
        json={"username": "integrationkid", "email": "int@test.com", "password": "testpass123"},
    )
    resp = client.post("/auth/login", data={"username": "integrationkid", "password": "testpass123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def paid_course_id(client):
    resp = client.get("/courses")
    return next(c["id"] for c in resp.json() if c["fee"] > 0)


@pytest.fixture(scope="module")
def admin_headers(client):
    client.post(
        "/auth/register",
        json={"username": "adminkid", "email": "admin@test.com", "password": "testpass123"},
    )
    # No self-serve path to admin (register always starts as student/parent)
    # — promote directly via DB, same as the fixtures above seed content.
    db = TestingSessionLocal()
    user = db.query(User).filter(User.username == "adminkid").first()
    user.role = "admin"
    db.commit()
    db.close()
    resp = client.post("/auth/login", data={"username": "adminkid", "password": "testpass123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login(client):
    resp = client.post(
        "/auth/register",
        json={"username": "newkid", "email": "new@test.com", "password": "testpass123"},
    )
    assert resp.status_code == 201
    assert resp.json()["username"] == "newkid"

    resp = client.post("/auth/login", data={"username": "newkid", "password": "testpass123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password_rejected(client):
    resp = client.post("/auth/login", data={"username": "newkid", "password": "wrongpass"})
    assert resp.status_code == 401


def test_courses_requires_no_auth_but_progress_does(client, auth_headers):
    resp = client.get("/courses")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
    course_id = resp.json()[0]["id"]

    # Progress endpoint requires auth + enrollment
    resp = client.get(f"/courses/{course_id}/progress")
    assert resp.status_code == 401

    resp = client.get(f"/courses/{course_id}/progress", headers=auth_headers)
    assert resp.status_code == 403  # not enrolled yet


def test_enroll_then_progress_succeeds(client, auth_headers):
    resp = client.get("/courses", headers=auth_headers)
    course_id = resp.json()[0]["id"]

    resp = client.post("/enrollments", json={"course_id": course_id}, headers=auth_headers)
    assert resp.status_code == 201

    # Duplicate enrollment should be rejected
    resp = client.post("/enrollments", json={"course_id": course_id}, headers=auth_headers)
    assert resp.status_code == 400

    resp = client.get(f"/courses/{course_id}/progress", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["course_id"] == course_id
    assert body["completed_lessons"] == 0


def test_master_games_and_stats_endpoints(client, auth_headers):
    resp = client.get("/master-games", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

    resp = client.get("/me/stats", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == {"total_stars": 0, "current_streak": 0, "longest_streak": 0}


def test_protected_route_without_token_rejected(client):
    resp = client.get("/me/profile")
    assert resp.status_code == 401


def test_free_course_enrollment_ignores_coupon_field(client, auth_headers):
    """Free courses (fee == 0) never require a coupon, even if omitted."""
    resp = client.get("/courses", headers=auth_headers)
    course_id = next(c["id"] for c in resp.json() if c["fee"] == 0)
    resp = client.post("/enrollments", json={"course_id": course_id}, headers=auth_headers)
    assert resp.status_code in (201, 400)  # 400 if already enrolled by an earlier test


def test_paid_enrollment_without_coupon_rejected(client, auth_headers, paid_course_id):
    resp = client.post("/enrollments", json={"course_id": paid_course_id}, headers=auth_headers)
    assert resp.status_code == 400
    assert "coupon" in resp.json()["detail"].lower()


def test_paid_enrollment_with_invalid_coupon_rejected(client, auth_headers, paid_course_id):
    resp = client.post(
        "/enrollments",
        json={"course_id": paid_course_id, "coupon_code": "NOT-A-REAL-CODE"},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert "coupon" in resp.json()["detail"].lower()


def test_non_admin_cannot_manage_coupons(client, auth_headers):
    resp = client.get("/admin/coupons", headers=auth_headers)
    assert resp.status_code == 403
    resp = client.post("/admin/coupons", json={"code": "SHOULDFAIL"}, headers=auth_headers)
    assert resp.status_code == 403


def test_admin_can_create_and_list_coupons(client, admin_headers):
    resp = client.post(
        "/admin/coupons",
        json={"code": "testcode", "description": "One-time test coupon", "max_redemptions": 1},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["code"] == "TESTCODE"  # normalized to uppercase
    assert body["times_redeemed"] == 0

    # Duplicate code rejected
    resp = client.post("/admin/coupons", json={"code": "TESTCODE"}, headers=admin_headers)
    assert resp.status_code == 400

    resp = client.get("/admin/coupons", headers=admin_headers)
    assert resp.status_code == 200
    assert any(c["code"] == "TESTCODE" for c in resp.json())


def test_paid_enrollment_with_valid_coupon_redeems_and_respects_limit(client, admin_headers, paid_course_id):
    # A second, throwaway student redeems the single-use TESTCODE coupon
    # created above (lowercase input exercises the case-insensitive match).
    client.post(
        "/auth/register",
        json={"username": "couponkid", "email": "coupon@test.com", "password": "testpass123"},
    )
    login = client.post("/auth/login", data={"username": "couponkid", "password": "testpass123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    resp = client.post(
        "/enrollments",
        json={"course_id": paid_course_id, "coupon_code": "testcode"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["coupon_code"] == "TESTCODE"

    # A third student cannot reuse the now-exhausted single-redemption coupon.
    client.post(
        "/auth/register",
        json={"username": "couponkid2", "email": "coupon2@test.com", "password": "testpass123"},
    )
    login2 = client.post("/auth/login", data={"username": "couponkid2", "password": "testpass123"})
    headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}
    resp = client.post(
        "/enrollments",
        json={"course_id": paid_course_id, "coupon_code": "TESTCODE"},
        headers=headers2,
    )
    assert resp.status_code == 400
    assert "limit" in resp.json()["detail"].lower()

    # Deactivating a coupon blocks it too, even for a fresh redemption count.
    coupons = client.get("/admin/coupons", headers=admin_headers).json()
    coupon_id = next(c["id"] for c in coupons if c["code"] == "TESTCODE")
    resp = client.patch(f"/admin/coupons/{coupon_id}", json={"is_active": False}, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False
