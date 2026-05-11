from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models.post import Post
from app.repositories import users as users_repo


def _register(client: TestClient):
    suffix = uuid4().hex[:8]
    payload = {
        "username": f"poster_{suffix}",
        "email": f"poster_{suffix}@example.com",
        "password": "password123",
        "display_name": "Автор теста",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return payload, token


def test_create_post_metadata_directly():
    with TestClient(app) as client:
        payload, _ = _register(client)

    db = SessionLocal()
    try:
        user = users_repo.get_by_username(db, payload["username"])
        post = Post(
            author_id=user.id,
            caption="metadata only",
            media_url="http://localhost:9000/socialgram-media/tests/post.svg",
            media_object_key="tests/post.svg",
        )
        db.add(post)
        db.commit()
        db.refresh(post)

        assert post.id is not None
        assert post.media_object_key == "tests/post.svg"
    finally:
        db.close()


def test_like_unlike_logic():
    with TestClient(app) as client:
        payload, token = _register(client)
        db = SessionLocal()
        try:
            user = users_repo.get_by_username(db, payload["username"])
            post = Post(
                author_id=user.id,
                caption="like api",
                media_url="http://localhost:9000/socialgram-media/tests/like.svg",
                media_object_key="tests/like.svg",
            )
            db.add(post)
            db.commit()
            db.refresh(post)
            post_id = str(post.id)
        finally:
            db.close()

        headers = {"Authorization": f"Bearer {token}"}
        like_response = client.post(f"/api/posts/{post_id}/like", headers=headers)
        unlike_response = client.delete(f"/api/posts/{post_id}/like", headers=headers)

    assert like_response.status_code == 200
    assert like_response.json()["liked_by_me"] is True
    assert unlike_response.status_code == 200
    assert unlike_response.json()["liked_by_me"] is False


def test_report_post_logic():
    with TestClient(app) as client:
        payload, token = _register(client)
        db = SessionLocal()
        try:
            user = users_repo.get_by_username(db, payload["username"])
            post = Post(
                author_id=user.id,
                caption="report api",
                media_url="http://localhost:9000/socialgram-media/tests/report.svg",
                media_object_key="tests/report.svg",
            )
            db.add(post)
            db.commit()
            db.refresh(post)
            post_id = str(post.id)
        finally:
            db.close()

        response = client.post(
            f"/api/posts/{post_id}/report",
            headers={"Authorization": f"Bearer {token}"},
            json={"reason": "Спам", "details": "Тестовая жалоба"},
        )

    assert response.status_code == 200
    assert response.json()["reason"] == "Спам"
