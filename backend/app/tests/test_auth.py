from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_register_login_and_me():
    suffix = uuid4().hex[:8]
    payload = {
        "username": f"test_{suffix}",
        "email": f"test_{suffix}@example.com",
        "password": "password123",
        "display_name": "Тестовый пользователь",
    }

    with TestClient(app) as client:
        register_response = client.post("/api/auth/register", json=payload)
        assert register_response.status_code == 200
        token = register_response.json()["access_token"]

        login_response = client.post("/api/auth/login", json={"login": payload["username"], "password": payload["password"]})
        assert login_response.status_code == 200

        me_response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert me_response.status_code == 200
    assert me_response.json()["username"] == payload["username"]
